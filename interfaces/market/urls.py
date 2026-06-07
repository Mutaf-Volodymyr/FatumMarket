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
    path("checkout/", views.OrdersView.as_view(), name="checkout"),
    path("orders/<str:order_id>/", views.order_detail_view, name="order_detail"),
    path("orders/<str:order_id>/success/", views.order_success_view, name="order_success"),
    path("orders/created/", views.order_created_view, name="order_created"),
    path("account/", views.account_view, name="account"),
    path("showroom/", views.showroom_view, name="showroom"),
    path("fitting/", views.fitting_view, name="fitting"),
    path("fitting-confirm/", views.fitting_confirm_view, name="fitting-confirm"),
    path("fitting/add/<int:product_id>/", views.fitting_add_view, name="fitting_add"),
    path("fitting/remove/<int:product_id>/", views.fitting_remove_view, name="fitting_remove"),
]
