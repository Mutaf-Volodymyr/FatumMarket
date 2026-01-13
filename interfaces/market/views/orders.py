from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from apps.orders.models import Order, OrderItem
from apps.delivery.models import Delivery


@login_required
def checkout_view(request):
    """Checkout page - create order from cart items"""
    cart_items = OrderItem.objects.filter(
        user=request.user,
        status=OrderItem.OrderItemStatus.CARD
    ).select_related('product')
    
    if not cart_items.exists():
        messages.error(request, 'Корзина пуста')
        return redirect('market:cart')
    
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        
        if not selected_items:
            messages.error(request, 'Выберите товары для оформления заказа')
            return redirect('market:cart')
        
        try:
            with transaction.atomic():
                # Get selected cart items
                selected_cart_items = OrderItem.objects.filter(
                    id__in=selected_items,
                    user=request.user,
                    status=OrderItem.OrderItemStatus.CARD
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
                
                # Create order
                order = Order.objects.create(
                    customer=request.user,
                    status=Order.OrderStatus.DRAFT,
                    total_price=total_price,
                    total_discount=total_discount,
                    comment=request.POST.get('comment', '')
                )
                
                # Update cart items to order items
                selected_cart_items.update(
                    order=order,
                    status=OrderItem.OrderItemStatus.ORDER
                )
                
                # Create delivery (simplified - pickup by default)
                delivery = Delivery.objects.create(
                    order=order,
                    delivery_type=Delivery.DeliveryTypeChoices.pickup,
                    recipient=request.user,
                )
                
                messages.success(request, f'Заказ #{order.id} успешно оформлен!')
                return redirect('market:order_detail', order_id=order.id)
        
        except Exception as e:
            messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
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


@login_required
def order_detail_view(request, order_id):
    """Order detail page"""
    order = get_object_or_404(
        Order.objects.select_related('customer', 'delivery', 'payment')
        .prefetch_related('items__product'),
        id=order_id,
        customer=request.user
    )
    
    return render(request, 'market/order_detail.html', {
        'order': order,
    })


@login_required
def account_view(request):
    """User account page with order history"""
    orders = Order.objects.filter(
        customer=request.user
    ).select_related('delivery', 'payment').prefetch_related('items').order_by('-created_at')
    
    return render(request, 'market/account.html', {
        'orders': orders,
    })

