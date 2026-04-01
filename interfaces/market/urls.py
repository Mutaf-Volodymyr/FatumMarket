from django.urls import path

from . import views

app_name = "market"

urlpatterns = [
    path("", views.product_list_view, name="home"),
    path("products/<slug:slug>/", views.product_detail_view, name="product_detail"),
    path("categories/", views.category_list_view, name="category_list"),
    path("categories/<slug:slug>/", views.category_list_view, name="category_detail"),
    path("brands/", views.brand_list_view, name="brand_list"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add_view, name="cart_add"),
    path("cart/remove/<int:item_id>/", views.cart_remove_view, name="cart_remove"),
    path("cart/update/<int:item_id>/", views.cart_update_view, name="cart_update"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("orders/<str:order_id>/", views.order_detail_view, name="order_detail"),
    path("orders/<str:order_id>/success/", views.order_success_view, name="order_success"),
    path("staff/create_order/", views.staff_create_order_view, name="staff_create_order"),
    path("account/", views.account_view, name="account"),
]
