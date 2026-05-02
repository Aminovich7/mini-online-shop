from decimal import Decimal

from django.db import models

from accounts.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class Product(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10000000, decimal_places=2)
    address = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=17)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def discounted_price(self):
        if self.discount_percent > 0:
            return self.price * (Decimal(100) - self.discount_percent) / Decimal(100)
        return self.price

    @property
    def cover_image(self):
        return self.images.first()

    @property
    def has_discount(self):
        return self.discount_percent > 0

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ("-id",)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="products/", default="products/default_product.png"
    )


class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comments")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} -> {self.product} ({self.created_at:%Y-%m-%d})"

    class Meta:
        ordering = ("-created_at",)


class Saved(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="saved_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="saved_by"
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} saved {self.product}"


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="likes")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} liked {self.product}"
