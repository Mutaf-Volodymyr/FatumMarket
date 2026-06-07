from .brands import brand_list_view
from .cart import cart_add_view, cart_remove_view, cart_update_view, cart_view
from .categories import category_list_view
from .fitting import fitting_add_view, fitting_confirm_view, fitting_remove_view, fitting_view
from .orders import (
    OrdersView,
    account_view,
    order_created_view,
    order_detail_view,
    order_success_view,
)
from .products import product_detail_view, product_list_view
from .showroom import showroom_view

__all__ = [
    "product_list_view",
    "product_detail_view",
    "cart_view",
    "cart_add_view",
    "cart_remove_view",
    "cart_update_view",
    "OrdersView",
    "order_detail_view",
    "account_view",
    "category_list_view",
    "brand_list_view",
    "order_success_view",
    "order_created_view",
    "showroom_view",
    "fitting_view",
    "fitting_add_view",
    "fitting_remove_view",
    "fitting_confirm_view",
]
