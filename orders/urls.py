from django.urls import path

from .views import (
    AddToCartView,
    CartDetailView,
    CheckoutCreateView,
    OrderSuccessView,
    OrderListView,
    RemoveFromCartView,
    UpdateCartItemView,
    ApplyPromoCodeView,
    CartCheckoutView,
)

app_name = "orders"

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="cart"),
    path("cart/add/<int:pk>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/update/<uuid:pk>/", UpdateCartItemView.as_view(), name="update_cart_item"),
    path("cart/remove/<uuid:pk>/", RemoveFromCartView.as_view(), name="remove_from_cart"),
    path("cart/promo/", ApplyPromoCodeView.as_view(), name="apply_promo"),
    path("cart/checkout/", CartCheckoutView.as_view(), name="cart_checkout"),
    path("checkout/<int:pk>/", CheckoutCreateView.as_view(), name="checkout"),
    path("success/<uuid:pk>/", OrderSuccessView.as_view(), name="success"),
    path("order-list/", OrderListView.as_view(), name="order_list"),

]
