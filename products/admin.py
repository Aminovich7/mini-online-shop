from django.contrib import admin
from .models import Category, Product, ProductImage, Comment, Saved, Like


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'discount_percent')
    list_filter = ('category', 'author')
    search_fields = ('title', 'description', 'author__username')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Product Info', {'fields': ('title', 'description', 'category', 'author')}),
        ('Pricing', {'fields': ('price', 'discount_percent')}),
        ('Contact', {'fields': ('address', 'phone_number')}),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    list_filter = ('product',)
    search_fields = ('product__title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'created_at')
    list_filter = ('created_at', 'product')
    search_fields = ('author__username', 'product__title', 'body')
    readonly_fields = ('created_at',)


@admin.register(Saved)
class SavedAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'product__title')
    readonly_fields = ('saved_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__title')
    readonly_fields = ('created_at',)
