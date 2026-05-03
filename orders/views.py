from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView, ListView

from products.models import Product
from shared.mixins import AuthRequiredMessageMixin

from .forms import CheckoutForm
from .models import Card, CardItem, Order, OrderItem, PromoCode


class OrderListView(AuthRequiredMessageMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    permission_denied_message = "Buyurtmalaringizni ko'rish uchun tizimga kiring."

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


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
        # Remove items with deleted products
        card.items.filter(product__isnull=True).delete()
        context["card"] = card
        context["items"] = card.items.select_related("product").all()
        context["promo_form"] = {'applied_code': self.request.session.get('applied_promo_code', '')}
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


class UpdateCartItemView(AuthRequiredMessageMixin, View):
    permission_denied_message = "Savatni boshqarish uchun tizimga kiring."

    def post(self, request, pk):
        item = get_object_or_404(
            CardItem.objects.select_related("card"),
            pk=pk,
            card__user=request.user,
        )
        action = request.POST.get("action")
        
        if action == "increase":
            item.quantity += 1
            item.save()
            messages.success(request, "Miqdor oshirildi.")
        elif action == "decrease":
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
                messages.success(request, "Miqdor kamaytildi.")
            else:
                item.delete()
                messages.success(request, "Mahsulot savatdan olib tashlandi.")
        
        return redirect("orders:cart")


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


class ApplyPromoCodeView(AuthRequiredMessageMixin, View):
    permission_denied_message = "Promo-kod qo'llash uchun tizimga kiring."

    def post(self, request):
        code = request.POST.get("promo_code", "").strip()
        
        if not code:
            messages.error(request, "Promo-kod bo'sh bo'lishi mumkin emas.")
            return redirect("orders:cart")
        
        promo = PromoCode.objects.filter(code__iexact=code, active=True).first()
        
        if not promo:
            messages.error(request, "Promo-kod topilmadi yoki faol emas.")
            return redirect("orders:cart")
        
        request.session['applied_promo_code'] = code
        request.session['promo_discount_percent'] = promo.discount_percent
        messages.success(request, f"Promo-kod qo'llanildi! {promo.discount_percent}% chegirma.")
        return redirect("orders:cart")


class CartCheckoutView(AuthRequiredMessageMixin, FormView):
    template_name = "orders/cart_checkout.html"
    form_class = CheckoutForm
    permission_denied_message = "Buyurtma berish uchun tizimga kiring."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = Card.objects.get(user=self.request.user)
        promo_code = None
        code = self.request.session.get('applied_promo_code', '')
        
        if code:
            promo_code = PromoCode.objects.filter(code__iexact=code, active=True).first()
        
        context["card"] = card
        context["items"] = card.items.select_related("product").all()
        context["promo_code"] = promo_code
        context["subtotal"] = card.subtotal
        
        if promo_code:
            discount_amount = card.subtotal * Decimal(promo_code.discount_percent) / Decimal(100)
            context["discount_amount"] = discount_amount
            context["total"] = card.subtotal - discount_amount
        else:
            context["discount_amount"] = Decimal(0)
            context["total"] = card.subtotal
        
        return context

    def form_valid(self, form):
        card = Card.objects.get(user=self.request.user)
        
        if not card.items.exists():
            messages.error(self.request, "Savat bo'sh. Mahsulot qo'shing.")
            return redirect("orders:cart")
        
        promo_code = None
        code = self.request.session.get('applied_promo_code', '')
        
        if code:
            promo_code = PromoCode.objects.filter(code__iexact=code, active=True).first()
        
        order = Order.objects.create(
            user=self.request.user,
            address=form.cleaned_data["address"],
            promo_code=promo_code,
        )
        
        # Copy items from cart to order
        for item in card.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                total_price=item.total_price,
            )
        
        order.calculate_total()
        
        # Clear cart and session
        card.items.all().delete()
        if 'applied_promo_code' in self.request.session:
            del self.request.session['applied_promo_code']
        if 'promo_discount_percent' in self.request.session:
            del self.request.session['promo_discount_percent']
        
        messages.success(self.request, "Buyurtmangiz muvaffaqiyatli yaratildi.")
        return redirect(reverse("orders:success", kwargs={"pk": order.pk}))
