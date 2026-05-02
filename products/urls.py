from django.urls import path

from .views import (
    CommentCreateView,
    LikedProductsView,
    ProductDetailView,
    SavedProductsView,
    ShopHomeView,
    ToggleLikeView,
    ToggleSavedView,
)

app_name = "products"

urlpatterns = [
    path("", ShopHomeView.as_view(), name="home"),
    path("saved/", SavedProductsView.as_view(), name="saved"),
    path("liked/", LikedProductsView.as_view(), name="liked"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="detail"),
    path("products/<int:pk>/comment/", CommentCreateView.as_view(), name="comment"),
    path("products/<int:pk>/like/", ToggleLikeView.as_view(), name="toggle_like"),
    path("products/<int:pk>/save/", ToggleSavedView.as_view(), name="toggle_save"),
]
