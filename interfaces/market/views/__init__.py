from .brands import brand_list_view
from .cart import cart_add_view, cart_remove_view, cart_update_view, cart_view
from .categories import category_list_view
from .orders import account_view, checkout_view, order_detail_view, order_success_view
from .products import product_detail_view, product_list_view
from .staff import staff_create_order_view

__all__ = [
    "product_list_view",
    "product_detail_view",
    "cart_view",
    "cart_add_view",
    "cart_remove_view",
    "cart_update_view",
    "checkout_view",
    "order_detail_view",
    "account_view",
    "category_list_view",
    "brand_list_view",
    "order_success_view",
    "staff_create_order_view",
]
