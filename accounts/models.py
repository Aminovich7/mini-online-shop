import uuid

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("seller", "Seller"),
    )

    id = models.UUIDField(unique=True, primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=20, choices=USER_TYPES, default="user")
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default_avatar.png", blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_type_display()})"

    @property
    def is_admin(self):
        return self.type == "admin"

    @property
    def is_user(self):
        return self.type == "user"

    @property
    def is_seller(self):
        return self.type == "seller"

    @property
    def role_name(self):
        return self.type

    @property
    def full_name_or_username(self):
        full_name = self.get_full_name().strip()
        return full_name or self.username

    @property
    def cart_items_count(self):
        Card = apps.get_model("orders", "Card")
        card = Card.objects.filter(user=self).first()
        return card.items.count() if card else 0

    @property
    def saved_items_count(self):
        return self.saved_items.count()

    @property
    def liked_items_count(self):
        return self.likes.count()
