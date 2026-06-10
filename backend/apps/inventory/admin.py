from django.contrib import admin

from .models import BranchTransfer, Category, Product, StockItem, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "level", "slug", "created_at")
    list_filter = ("level",)
    search_fields = ("name", "slug")
    readonly_fields = ("level", "created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "buy_price", "sell_price", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("name", "barcode_prefix", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("barcode", "product", "branch", "status", "serial_number", "created_at")
    list_filter = ("status", "branch")
    search_fields = ("barcode", "serial_number", "product__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "movement_type", "from_branch", "to_branch", "user", "created_at")
    list_filter = ("movement_type", "from_branch", "to_branch")
    search_fields = ("item__barcode", "item__product__name", "note", "user__phone")
    readonly_fields = ("created_at",)


@admin.register(BranchTransfer)
class BranchTransferAdmin(admin.ModelAdmin):
    list_display = ("from_branch", "to_branch", "status", "requested_by", "approved_by", "created_at")
    list_filter = ("status", "from_branch", "to_branch")
    search_fields = ("requested_by__phone", "approved_by__phone", "notes")
    readonly_fields = ("created_at", "updated_at")
