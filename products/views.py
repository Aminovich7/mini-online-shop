from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from orders.forms import CheckoutForm
from orders.models import Card, CardItem
from shared.mixins import AuthRequiredMessageMixin

from .forms import CommentForm, ProductFilterForm
from .models import Category, Comment, Like, Product, Saved


class ShopHomeView(ListView):
    model = Product
    template_name = "index.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        queryset = (
            Product.objects.select_related("author", "category")
            .prefetch_related("images")
            .annotate(comment_total=Count("comments", distinct=True))
            .annotate(like_total=Count("likes", distinct=True))
            .annotate(saved_total=Count("saved_by", distinct=True))
            .order_by("-id")
        )
        query = self.request.GET.get("query", "").strip()
        category = self.request.GET.get("category", "").strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            )

        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = ProductFilterForm(self.request.GET or None)
        context["categories"] = Category.objects.all()
        context["featured_product"] = self.object_list[0] if self.object_list else None
        context["results_count"] = self.get_queryset().count()
        return context


class UserProductCollectionView(AuthRequiredMessageMixin, ListView):
    model = Product
    template_name = "products/collection.html"
    context_object_name = "products"
    permission_denied_message = "Bu bo'limni ko'rish uchun tizimga kiring."

    collection_type = ""
    heading = ""
    description = ""

    def get_queryset(self):
        queryset = (
            Product.objects.select_related("author", "category")
            .prefetch_related("images")
            .annotate(comment_total=Count("comments", distinct=True))
            .annotate(like_total=Count("likes", distinct=True))
            .annotate(saved_total=Count("saved_by", distinct=True))
            .order_by("-id")
        )
        return self.filter_queryset(queryset)

    def filter_queryset(self, queryset):
        return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["heading"] = self.heading
        context["description"] = self.description
        context["collection_type"] = self.collection_type
        return context


class SavedProductsView(UserProductCollectionView):
    collection_type = "saved"
    heading = "Saqlangan mahsulotlar"
    description = "Keyinroq ko'rish uchun saqlab qo'ygan mahsulotlaringiz ro'yxati."
    permission_denied_message = "Saqlangan mahsulotlarni ko'rish uchun tizimga kiring."

    def filter_queryset(self, queryset):
        return queryset.filter(saved_by__user=self.request.user).distinct()


class LikedProductsView(UserProductCollectionView):
    collection_type = "liked"
    heading = "Yoqtirilgan mahsulotlar"
    description = "Sizga yoqqan mahsulotlar shu yerda jamlangan."
    permission_denied_message = "Yoqtirilgan mahsulotlarni ko'rish uchun tizimga kiring."

    def filter_queryset(self, queryset):
        return queryset.filter(likes__user=self.request.user).distinct()


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return (
            Product.objects.select_related("author", "category")
            .prefetch_related("images", "comments__author")
            .annotate(comment_total=Count("comments", distinct=True))
            .annotate(like_total=Count("likes", distinct=True))
            .annotate(saved_total=Count("saved_by", distinct=True))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = kwargs.get("comment_form", CommentForm())
        context["checkout_form"] = CheckoutForm()
        context["related_products"] = (
            Product.objects.select_related("category")
            .prefetch_related("images")
            .filter(category=self.object.category)
            .exclude(pk=self.object.pk)[:3]
        )
        user = self.request.user
        context["is_liked"] = user.is_authenticated and Like.objects.filter(
            user=user, product=self.object
        ).exists()
        context["is_saved"] = user.is_authenticated and Saved.objects.filter(
            user=user, product=self.object
        ).exists()
        context["is_in_cart"] = False
        if user.is_authenticated:
            card = Card.objects.filter(user=user).first()
            if card:
                context["is_in_cart"] = CardItem.objects.filter(
                    card=card, product=self.object
                ).exists()
        return context


class CommentCreateView(AuthRequiredMessageMixin, View):
    permission_denied_message = "Izoh yozish uchun tizimga kiring."

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            Comment.objects.create(
                author=request.user,
                product=product,
                body=form.cleaned_data["body"],
            )
            messages.success(request, "Izohingiz muvaffaqiyatli qo'shildi.")
        else:
            messages.error(request, "Izohni yuborishda xatolik yuz berdi.")

        return redirect("products:detail", pk=product.pk)


class ToggleLikeView(AuthRequiredMessageMixin, View):
    permission_denied_message = "Mahsulotni yoqtirish uchun tizimga kiring."

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, product=product)
        if created:
            messages.success(request, "Mahsulot yoqtirilganlarga qo'shildi.")
        else:
            like.delete()
            messages.success(request, "Mahsulot yoqtirilganlardan olib tashlandi.")
        return redirect(request.POST.get("next") or reverse("products:detail", kwargs={"pk": product.pk}))


class ToggleSavedView(AuthRequiredMessageMixin, View):
    permission_denied_message = "Mahsulotni saqlash uchun tizimga kiring."

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        saved, created = Saved.objects.get_or_create(user=request.user, product=product)
        if created:
            messages.success(request, "Mahsulot saqlanganlar ro'yxatiga qo'shildi.")
        else:
            saved.delete()
            messages.success(request, "Mahsulot saqlanganlardan olib tashlandi.")
        return redirect(request.POST.get("next") or reverse("products:detail", kwargs={"pk": product.pk}))
