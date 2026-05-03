from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'avatar')}),
        ('Type', {'fields': ('type',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
