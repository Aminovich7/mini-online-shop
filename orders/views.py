from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView

from products.models import Product
from shared.mixins import AuthRequiredMessageMixin

from .forms import CheckoutForm
from .models import Card, CardItem, Order, OrderItem, PromoCode


class CheckoutCreateView(AuthRequiredMessageMixin, FormView):
    template_name = "orders/checkout.html"
    form_class = CheckoutForm
    permission_denied_message = "Buyurtma berish uchun tizimga kiring."

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(
            Product.objects.select_related("author", "category").prefetch_related("images"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.product
        return context

    def form_valid(self, form):
        promo_code = None
        code = form.cleaned_data["promo_code"].strip()
        quantity = form.cleaned_data["quantity"]

        if code:
            promo_code = PromoCode.objects.filter(code__iexact=code, active=True).first()
            if not promo_code:
                form.add_error("promo_code", "Promo-kod topilmadi yoki faol emas.")
                return self.form_invalid(form)

        self.order = Order.objects.create(
            user=self.request.user,
            address=form.cleaned_data["address"],
            promo_code=promo_code,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=quantity,
            total_price=self.product.discounted_price() * Decimal(quantity),
        )
        self.order.calculate_total()
        messages.success(self.request, "Buyurtmangiz muvaffaqiyatli yaratildi.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("orders:success", kwargs={"pk": self.order.pk})


class OrderSuccessView(AuthRequiredMessageMixin, DetailView):
    model = Order
    template_name = "orders/order_success.html"
    context_object_name = "order"
    permission_denied_message = "Buyurtma tafsilotlarini ko'rish uchun tizimga kiring."

    def get_queryset(self):
        return Order.objects.select_related("promo_code", "user").prefetch_related(
            "items__product__images"
        ).filter(user=self.request.user)


class CartDetailView(AuthRequiredMessageMixin, TemplateView):
    template_name = "orders/cart.html"
    permission_denied_message = "Savatni ko'rish uchun tizimga kiring."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card, _ = Card.objects.get_or_create(user=self.request.user)
        context["card"] = card
        context["items"] = card.items.select_related("product").all()
        return context


class AddToCartView(AuthRequiredMessageMixin, View):
    permission_denied_message = "Savatga qo'shish uchun tizimga kiring."

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        card, _ = Card.objects.get_or_create(user=request.user)
        item, created = CardItem.objects.get_or_create(
            card=card,
            product=product,
            defaults={
                "quantity": 1,
                "total_price": product.discounted_price(),
            },
        )
        if created:
            messages.success(request, "Mahsulot savatga qo'shildi.")
        else:
            item.quantity += 1
            item.save()
            messages.success(request, "Mahsulot savatdagi miqdori oshirildi.")
        return redirect(request.POST.get("next") or reverse("orders:cart"))


class RemoveFromCartView(AuthRequiredMessageMixin, View):
    permission_denied_message = "Savatni boshqarish uchun tizimga kiring."

    def post(self, request, pk):
        item = get_object_or_404(
            CardItem.objects.select_related("card"),
            pk=pk,
            card__user=request.user,
        )
        item.delete()
        messages.success(request, "Mahsulot savatdan olib tashlandi.")
        return redirect("orders:cart")
