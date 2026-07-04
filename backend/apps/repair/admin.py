from django.contrib import admin

from .models import RepairOrder, RepairSettings


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = ("order", "device_type", "device_model", "technician", "status", "final_price", "customer_approved", "created_at")
    list_filter = ("status", "device_type", "customer_approved")
    search_fields = ("order__order_number", "device_model", "issue_description", "technician__phone")
    readonly_fields = ("final_price", "markup_percent", "approved_at", "created_at", "updated_at")


@admin.register(RepairSettings)
class RepairSettingsAdmin(admin.ModelAdmin):
    list_display = ("markup_percent", "updated_by", "updated_at")
    readonly_fields = ("updated_at",)
