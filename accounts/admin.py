from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, OTPVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)

    list_display = (
        "avatar_preview",
        "email",
        "name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "created_at",
    )

    list_display_links = ("email", "name", "avatar_preview")

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    search_fields = (
        "email",
        "name",
        "last_name",
        "phone_number",
    )

    readonly_fields = (
        "created_at",
        "last_login",
        "avatar_preview",
    )

    fieldsets = (
        (None, {
            "fields": (
                "email",
                "password",
            )
        }),
        ("Профиль", {
            "fields": (
                "avatar",
                "avatar_preview",
                "name",
                "last_name",
                "phone_number",
            )
        }),
        ("Роль и доступы", {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Системная информация", {
            "fields": (
                "last_login",
                "created_at",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "role",
                "is_active",
                "is_staff",
            ),
        }),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="45" height="45" '
                'style="border-radius:50%; object-fit:cover;" />',
                obj.avatar.url
            )
        return "—"

    avatar_preview.short_description = "Аватар"


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "code",
        "is_expired",
        "created_at",
    )

    search_fields = ("email",)

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)

    def is_expired(self, obj):
        return obj.is_expired()

    is_expired.boolean = True
    is_expired.short_description = "Просрочен"
