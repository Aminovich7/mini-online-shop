from django.contrib import admin
from .models import PromoCode, Card, CardItem, Order, OrderItem


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active')
    list_filter = ('active',)
    search_fields = ('code',)
    fieldsets = (
        ('Promo Code Info', {'fields': ('code', 'discount_percent', 'active')}),
    )


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_quantity', 'subtotal', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


class CardItemInline(admin.TabularInline):
    model = CardItem
    extra = 0
    fields = ('product', 'quantity', 'total_price')
    readonly_fields = ('total_price',)


@admin.register(CardItem)
class CardItemAdmin(admin.ModelAdmin):
    list_display = ('card', 'product', 'quantity', 'total_price')
    list_filter = ('card', 'product')
    search_fields = ('card__user__username', 'product__title')
    readonly_fields = ('total_price',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'total_price')
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'finished_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'address')
    readonly_fields = ('finished_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('user', 'status', 'address')}),
        ('Promo Code', {'fields': ('promo_code',)}),
        ('Pricing', {'fields': ('finished_price',)}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'total_price')
    list_filter = ('order', 'product')
    search_fields = ('order__user__username', 'product__title')
    readonly_fields = ('total_price',)
