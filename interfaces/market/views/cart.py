from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.orders.models import OrderItem
from apps.products.models import Product


@login_required
def cart_view(request):
    """View cart with all items"""
    cart_items = OrderItem.objects.filter(
        user=request.user,
        status=OrderItem.OrderItemStatus.CARD
    ).select_related('product').prefetch_related('product__images')
    
    total_price = Decimal('0.00')
    total_discount = Decimal('0.00')
    
    for item in cart_items:
        item_total = (item.price or item.product.price) * item.quantity
        total_price += item_total
        item_discount = (item.discount or Decimal('0.00')) * item.quantity
        total_discount += item_discount
    
    return render(request, 'market/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': total_price - total_discount,
    })


@login_required
def cart_add_view(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            quantity = 1
        
        # Check if product already in cart
        cart_item = OrderItem.objects.filter(
            user=request.user,
            product=product,
            status=OrderItem.OrderItemStatus.CARD
        ).first()
        
        success = False
        error_message = None
        
        if cart_item:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.quantity:
                error_message = f'Недостаточно товара на складе. Доступно: {product.quantity}'
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                success = True
        else:
            # Create new cart item
            if quantity > product.quantity:
                error_message = f'Недостаточно товара на складе. Доступно: {product.quantity}'
            else:
                OrderItem.objects.create(
                    user=request.user,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                    discount=product.discount if product.has_discount else Decimal('0.00'),
                    product_name=product.name,
                    status=OrderItem.OrderItemStatus.CARD
                )
                success = True
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            # Get updated cart count
            cart_count = OrderItem.objects.filter(
                user=request.user,
                status=OrderItem.OrderItemStatus.CARD
            ).count()
            
            if success:
                return JsonResponse({
                    'success': True,
                    'cart_count': cart_count,
                    'in_cart': True
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': error_message,
                    'cart_count': cart_count
                }, status=400)
        
        # Regular form submission - redirect (messages removed, using AJAX instead)
        if not success:
            messages.error(request, error_message)
        
        # Redirect back to the same page (use HTTP_REFERER or home)
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('market:home')
    
    return redirect('market:home')


@login_required
def cart_remove_view(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(
        OrderItem,
        id=item_id,
        user=request.user,
        status=OrderItem.OrderItemStatus.CARD
    )
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('market:cart')


@login_required
def cart_update_view(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(
            OrderItem,
            id=item_id,
            user=request.user,
            status=OrderItem.OrderItemStatus.CARD
        )
        quantity = int(request.POST.get('quantity', 1))
        
        success = False
        error_message = None
        removed = False
        
        if quantity < 1:
            cart_item.delete()
            removed = True
            success = True
        elif quantity > cart_item.product.quantity:
            error_message = f'Недостаточно товара на складе. Доступно: {cart_item.product.quantity}'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            success = True
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            # Calculate updated totals
            cart_items = OrderItem.objects.filter(
                user=request.user,
                status=OrderItem.OrderItemStatus.CARD
            ).select_related('product')
            
            total_price = Decimal('0.00')
            total_discount = Decimal('0.00')
            
            for item in cart_items:
                item_total = (item.price or item.product.price) * item.quantity
                total_price += item_total
                item_discount = (item.discount or Decimal('0.00')) * item.quantity
                total_discount += item_discount
            
            if success:
                return JsonResponse({
                    'success': True,
                    'removed': removed,
                    'total_price': str(total_price),
                    'total_discount': str(total_discount),
                    'final_price': str(total_price - total_discount),
                    'cart_count': cart_items.count()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': error_message
                }, status=400)
        
        # Regular form submission - redirect
        if not success:
            messages.error(request, error_message)
        elif removed:
            messages.success(request, 'Товар удален из корзины')
        
        return redirect('market:cart')
    
    return redirect('market:cart')

