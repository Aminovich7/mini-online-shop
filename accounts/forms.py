from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Foydalanuvchi nomi",
        widget=forms.TextInput(attrs={"placeholder": "Foydalanuvchi nomingizni kiriting"}),
    )
    password = forms.CharField(
        label="Parol",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Parolingizni kiriting"}),
    )


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email"]
        labels = {
            "username": "Foydalanuvchi nomi",
            "first_name": "Ism",
            "last_name": "Familiya",
            "email": "Email",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Masalan: azizbek01"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Ismingiz"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Familiyangiz"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email manzilingiz"}),
        }

    password1 = forms.CharField(
        label="Parol",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Kamida 8 ta belgidan iborat parol"}),
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlang",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Parolni qayta kiriting"}),
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.type = "user"
        if commit:
            user.save()
        return user


class SellerRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email"]
        labels = {
            "username": "Foydalanuvchi nomi",
            "first_name": "Ism",
            "last_name": "Familiya",
            "email": "Email",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Masalan: azizbek01"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Ismingiz"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Familiyangiz"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email manzilingiz"}),
        }

    password1 = forms.CharField(
        label="Parol",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Kamida 8 ta belgidan iborat parol"}),
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlang",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Parolni qayta kiriting"}),
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.type = "seller"
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "avatar"]
        labels = {
            "username": "Foydalanuvchi nomi",
            "first_name": "Ism",
            "last_name": "Familiya",
            "email": "Email",
            "avatar": "Avatar",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Foydalanuvchi nomi"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Ism"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Familiya"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }
