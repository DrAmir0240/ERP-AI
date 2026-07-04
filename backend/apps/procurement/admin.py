from django.contrib import admin

from .models import PurchaseOrder, PurchaseRequest, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_person", "phone", "balance", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("company_name", "contact_person", "phone", "email")


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ("request_number", "requested_by", "branch", "status", "approved_by", "created_at")
    list_filter = ("status",)
    search_fields = ("request_number", "reason")
    readonly_fields = ("request_number", "approved_at", "created_at", "updated_at")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("purchase_number", "supplier", "branch", "total_amount", "payment_method", "purchased_by", "purchased_at")
    list_filter = ("payment_method",)
    search_fields = ("purchase_number", "supplier__company_name", "supplier_invoice_no")
    readonly_fields = ("purchase_number", "purchased_at", "created_at", "updated_at")
