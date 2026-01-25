from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from pydantic import ValidationError
from apps.address.domain.schema import CreateAddressSchema
from apps.address.models import Address
from apps.delivery.domain.manager import GeneralOrderDeliveryCreator, OrderDeliveryException
from apps.users.models import User
from apps.orders.models import Order, OrderItem
from apps.delivery.models import Delivery
from interfaces.market.cart_utils import get_order_item_creator_kwark_by_request, get_cart_queryset_by_request


def checkout_view(request):
    """Checkout page - create order from cart items"""
    cart_items = get_cart_queryset_by_request(request).select_related('product')
    
    if not cart_items.exists():
        messages.error(request, 'Корзина пуста')
        return redirect('market:cart')
    
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        
        if not selected_items:
            return redirect('market:cart')
        
        try:
            with transaction.atomic():
                # Get selected cart items
                selected_cart_items = get_cart_queryset_by_request(request).filter(
                    id__in=selected_items,
                )
                
                if not selected_cart_items.exists():
                    messages.error(request, 'Выбранные товары не найдены')
                    return redirect('market:cart')
                
                # Calculate totals
                total_price = Decimal('0.00')
                total_discount = Decimal('0.00')
                
                for item in selected_cart_items:
                    item_total = (item.price or item.product.price) * item.quantity
                    total_price += item_total
                    item_discount = (item.discount or Decimal('0.00')) * item.quantity
                    total_discount += item_discount
                
                def _clean_optional(value):
                    if value is None:
                        return None
                    if isinstance(value, str):
                        value = value.strip()
                        return value or None
                    return value

                def _split_name(full_name):
                    parts = full_name.split()
                    first_name = parts[0] if parts else ''
                    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    return first_name, last_name

                def _build_unknown_recipient(name, phone, email):
                    parts = [item for item in [name, phone, email] if item]
                    return ', '.join(parts) if parts else None

                if request.user.is_authenticated:
                    order_owner = request.user
                else:
                    customer_name = _clean_optional(request.POST.get('customer_name', '')) or ''
                    customer_phone = _clean_optional(request.POST.get('customer_phone', '')) or ''
                    customer_email = _clean_optional(request.POST.get('customer_email', ''))

                    if not customer_phone:
                        raise ValueError('Укажите телефон заказчика')

                    first_name, last_name = _split_name(customer_name)
                    order_owner = User.objects.filter(phone=customer_phone).first()
                    if order_owner is None:
                        order_owner = User.objects.create_user(
                            phone=customer_phone,
                            password=None,
                            is_active=False,
                            first_name=first_name,
                            last_name=last_name,
                            email=customer_email,
                        )
                    else:
                        fields_to_update = []
                        if customer_email and not order_owner.email:
                            order_owner.email = customer_email
                            fields_to_update.append('email')
                        if first_name and not order_owner.first_name:
                            order_owner.first_name = first_name
                            fields_to_update.append('first_name')
                        if last_name and not order_owner.last_name:
                            order_owner.last_name = last_name
                            fields_to_update.append('last_name')
                        if fields_to_update:
                            order_owner.save(update_fields=fields_to_update)

                order_kwargs = {'user': order_owner}
                if request.session.session_key:
                    order_kwargs['session_id'] = request.session.session_key

                # Create order
                order = Order.objects.create(
                    **order_kwargs,
                    status=Order.OrderStatus.IN_WORK,
                    total_price=total_price,
                    total_discount=total_discount,
                    comment=request.POST.get('comment', '')
                )
                
                # Update cart items to order items
                selected_cart_items.update(
                    order=order,
                    status=OrderItem.OrderItemStatus.ORDER,
                    user=order.user,
                )
                
                delivery_type = request.POST.get(
                    'delivery_type',
                    Delivery.DeliveryTypeChoices.pickup,
                )

                recipient_id = None
                unknown_recipient = None
                if request.user.is_authenticated:
                    recipient_type = request.POST.get('recipient_type', 'self')
                    if recipient_type == 'other':
                        recipient_name = _clean_optional(request.POST.get('recipient_name', '')) or ''
                        recipient_phone = _clean_optional(request.POST.get('recipient_phone', '')) or ''
                        recipient_email = _clean_optional(request.POST.get('recipient_email', ''))
                        unknown_recipient = _build_unknown_recipient(recipient_name, recipient_phone, recipient_email)
                        if not unknown_recipient:
                            raise ValueError('Укажите данные получателя')
                    else:
                        recipient_id = request.user.id
                else:
                    recipient_id = order_owner.id

                delivery_payload = {
                    'delivery_type': delivery_type,
                    'recipient_id': recipient_id,
                    'unknown_recipient': unknown_recipient,
                    'comment': _clean_optional(request.POST.get('delivery_comment')),
                    'possible_delivery_date': _clean_optional(request.POST.get('delivery_date')),
                    'possible_delivery_time_from': _clean_optional(request.POST.get('delivery_time_from')),
                    'possible_delivery_time_to': _clean_optional(request.POST.get('delivery_time_to')),
                }

                if delivery_type == Delivery.DeliveryTypeChoices.courier:
                    address_payload = {
                        'address': _clean_optional(request.POST.get('delivery_address')),
                        'geolocation': _clean_optional(request.POST.get('delivery_geolocation')),
                    }
                    address_schema = CreateAddressSchema.model_validate(address_payload)
                    address = Address.objects.create(**address_schema.model_dump())
                    delivery_payload.update({
                        'address_id': address.id,
                        'delivery_cost': Decimal('100.00'),
                    })
                else:
                    delivery_payload.update({
                        'delivery_type': Delivery.DeliveryTypeChoices.pickup,
                        'delivery_cost': Decimal('0.00'),
                    })

                delivery_creator = GeneralOrderDeliveryCreator(order, delivery_payload['delivery_type'])
                delivery_creator.create_order_delivery(delivery_payload)
                

                return redirect('market:order_detail', order_id=order.id)
        
        except (ValidationError, OrderDeliveryException, ValueError) as e:
            messages.error(request, f'Ошибка доставки: {e}')
            return redirect('market:cart')
        except Exception:
            return redirect('market:cart')
    
    # Calculate totals for display
    total_price = Decimal('0.00')
    total_discount = Decimal('0.00')
    
    for item in cart_items:
        item_total = (item.price or item.product.price) * item.quantity
        total_price += item_total
        item_discount = (item.discount or Decimal('0.00')) * item.quantity
        total_discount += item_discount
    
    return render(request, 'market/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': total_price - total_discount,
    })


def order_detail_view(request, order_id):
    """Order detail page"""
    order = get_object_or_404(
        Order.objects.select_related('user', 'delivery', 'payment')
        .prefetch_related('items__product'),
        id=order_id,
        **get_order_item_creator_kwark_by_request(request),
    )
    
    return render(request, 'market/order_detail.html', {
        'order': order,
    })


@login_required
def account_view(request):
    """User account page with order history"""
    orders = Order.objects.filter(
        **get_order_item_creator_kwark_by_request(request),
    ).select_related('delivery', 'payment').prefetch_related('items').order_by('-created_at')
    
    return render(request, 'market/account.html', {
        'orders': orders,
    })

