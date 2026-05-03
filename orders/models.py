from django.db import models
from shared.models import BaseModel
from accounts.models import CustomUser
from decimal import Decimal
from products.models import Product

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Card(BaseModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True, related_name="card"
    )

    def __str__(self):
        return self.user.username

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum((item.total_price for item in self.items.all()), Decimal("0.00"))


class CardItem(BaseModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="card_products"
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.product:
            self.total_price = self.product.discounted_price() * self.quantity
        else:
            self.total_price = 0
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["product", "card"]


class Order(BaseModel):
    STATUS = (
        ("new", "New"),
        ("paid", "Paid"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    address = models.CharField(max_length=120)
    promo_code = models.ForeignKey(
            PromoCode,
            on_delete=models.SET_NULL,
            null=True,
            blank=True
        )


    status = models.CharField(max_length=20, choices=STATUS, default="new")
    finished_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )



    @property
    def subtotal(self):
        return sum((item.total_price for item in self.items.all()), Decimal("0.00"))

    @property
    def discount_amount(self):
        if self.promo_code:
            return self.subtotal * Decimal(self.promo_code.discount_percent) / Decimal(100)
        return Decimal("0.00")

    def calculate_total(self):
        total = self.subtotal

        if self.promo_code and self.promo_code.active:
            total = total - self.discount_amount

        self.finished_price = total
        self.save()

    def __str__(self):
        return self.user.username

    @property
    def status_label_uz(self):
        labels = {
            "new": "Yangi",
            "paid": "To'langan",
            "done": "Yakunlangan",
            "cancelled": "Bekor qilingan",
        }
        return labels.get(self.status, self.status)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.product:
            self.total_price = self.product.discounted_price() * self.quantity
        else:
            self.total_price = 0
        super().save(*args, **kwargs)


    def __str__(self):
        return self.order.user.username






