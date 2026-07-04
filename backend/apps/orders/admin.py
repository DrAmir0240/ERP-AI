from django.contrib import admin

from .models import Invoice, Order, OrderItem, Payment, Refund, ReturnPolicy


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("item_type", "product", "stock_item", "account", "game_ids", "quantity", "unit_price", "total_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "order_type", "channel", "branch", "customer", "status", "total", "payment_status", "created_at")
    list_filter = ("order_type", "channel", "status", "payment_status", "branch")
    search_fields = ("order_number", "customer__phone", "customer__full_name", "notes")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "tax_rate", "tax_amount", "total", "issued_at")
    search_fields = ("invoice_number", "order__order_number")
    readonly_fields = ("invoice_number", "issued_at", "created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "amount", "status", "paid_by", "paid_at")
    list_filter = ("method", "status")
    search_fields = ("order__order_number", "reference_code", "paid_by__phone")
    readonly_fields = ("paid_at",)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("order", "requested_by", "amount", "status", "refund_method", "created_at")
    list_filter = ("status", "refund_method")
    search_fields = ("order__order_number", "requested_by__phone", "reason")
    readonly_fields = ("created_at", "updated_at", "completed_at")


@admin.register(ReturnPolicy)
class ReturnPolicyAdmin(admin.ModelAdmin):
    list_display = ("category", "return_days", "is_returnable")
    search_fields = ("category__name",)
