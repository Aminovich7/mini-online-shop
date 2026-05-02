from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from shared.mixins import AuthRequiredMessageMixin

from .forms import ProfileForm, UserLoginForm, UserRegisterForm
from .models import CustomUser


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Tizimga muvaffaqiyatli kirdingiz.")
        return super().form_valid(form)


class UserRegisterView(CreateView):
    model = CustomUser
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("products:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request, "Hisobingiz yaratildi.")
        return response


class ProfileUpdateView(AuthRequiredMessageMixin, UpdateView):
    model = CustomUser
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")
    permission_denied_message = "Profilni tahrirlash uchun tizimga kiring."

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil ma'lumotlari yangilandi.")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("products:home")
