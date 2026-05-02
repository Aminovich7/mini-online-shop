from django.urls import path

from .views import (
    AddToCartView,
    CartDetailView,
    CheckoutCreateView,
    OrderSuccessView,
    RemoveFromCartView,
)

app_name = "orders"

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="cart"),
    path("cart/add/<int:pk>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/remove/<uuid:pk>/", RemoveFromCartView.as_view(), name="remove_from_cart"),
    path("checkout/<int:pk>/", CheckoutCreateView.as_view(), name="checkout"),
    path("success/<uuid:pk>/", OrderSuccessView.as_view(), name="success"),
]
