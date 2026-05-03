from django.urls import path

from .views import ProfileUpdateView, UserLoginView, UserLogoutView, UserRegisterView, SellerRegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("register-seller/", SellerRegisterView.as_view(), name="register_seller"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
