from django.contrib import admin

from .models import AccountGame, AccountSale, Game, GameAccount


@admin.register(GameAccount)
class GameAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "account_type", "total_capacity", "sold_count", "is_active", "created_at")
    list_filter = ("account_type", "is_active")
    search_fields = ("name", "email", "notes")
    readonly_fields = ("sold_count", "created_at", "updated_at")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "platform", "is_active", "created_at")
    list_filter = ("platform", "is_active")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AccountGame)
class AccountGameAdmin(admin.ModelAdmin):
    list_display = ("account", "game")
    list_filter = ("game__platform",)
    search_fields = ("account__name", "game__name")


@admin.register(AccountSale)
class AccountSaleAdmin(admin.ModelAdmin):
    list_display = ("account", "customer", "order_id", "sold_at")
    list_filter = ("account__account_type",)
    search_fields = ("account__name", "customer__phone", "customer__full_name")
    readonly_fields = ("sold_at",)
