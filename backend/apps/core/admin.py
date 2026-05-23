from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AuditLog, Branch, Module, OTPCode, Permission, Role, User, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("phone", "full_name", "is_active", "is_admin", "is_staff", "created_at")
    list_filter = ("is_active", "is_admin", "is_staff")
    search_fields = ("phone", "full_name")
    ordering = ("phone",)
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal info", {"fields": ("full_name",)}),
        ("Permissions", {"fields": ("is_active", "is_admin", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("phone", "full_name", "password1", "password2")}),)


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "attempts", "expires_at", "verified_at", "created_at")
    search_fields = ("phone",)
    readonly_fields = ("created_at",)


admin.site.register(Branch)
admin.site.register(Role)
admin.site.register(Module)
admin.site.register(Permission)
admin.site.register(UserRole)
admin.site.register(AuditLog)
