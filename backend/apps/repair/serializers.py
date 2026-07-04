from django.utils import timezone
from rest_framework import serializers

from .models import RepairOrder, RepairSettings


class RepairSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairSettings
        fields = ("id", "markup_percent", "updated_by", "updated_at")
        read_only_fields = ("id", "updated_by", "updated_at")

    def create(self, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        obj, _ = RepairSettings.objects.update_or_create(
            pk=RepairSettings.objects.values_list("pk", flat=True).first(),
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)


class RepairOrderSerializer(serializers.ModelSerializer):
    technician_phone = serializers.CharField(source="technician.phone", read_only=True, default="")
    technician_name = serializers.CharField(source="technician.full_name", read_only=True, default="")
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    device_type_display = serializers.CharField(source="get_device_type_display", read_only=True)

    class Meta:
        model = RepairOrder
        fields = (
            "id",
            "order",
            "order_number",
            "device_type",
            "device_type_display",
            "device_model",
            "issue_description",
            "technician",
            "technician_phone",
            "technician_name",
            "technician_price",
            "markup_percent",
            "final_price",
            "customer_approved",
            "approved_at",
            "status",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "order_number",
            "device_type_display",
            "technician_phone",
            "technician_name",
            "markup_percent",
            "final_price",
            "status_display",
            "approved_at",
            "created_at",
            "updated_at",
        )


class RepairAcceptSerializer(serializers.Serializer):
    def save(self, **kwargs):
        repair = self.context["repair"]
        user = self.context["request"].user
        repair.technician = user
        repair.status = RepairOrder.STATUS_UNDER_REVIEW
        repair.save(update_fields=["technician", "status", "updated_at"])
        return repair


class RepairPriceSerializer(serializers.Serializer):
    technician_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def save(self, **kwargs):
        repair = self.context["repair"]
        repair.technician_price = self.validated_data["technician_price"]
        repair.markup_percent = RepairSettings.get_markup()
        repair.calculate_final_price()
        repair.status = RepairOrder.STATUS_PRICE_SET
        if self.validated_data["notes"]:
            repair.notes = f"{repair.notes}\n{self.validated_data['notes']}".strip()
        repair.save(update_fields=["technician_price", "markup_percent", "final_price", "status", "notes", "updated_at"])
        return repair


class CustomerDecisionSerializer(serializers.Serializer):
    approved = serializers.BooleanField()

    def save(self, **kwargs):
        repair = self.context["repair"]
        approved = self.validated_data["approved"]
        repair.customer_approved = approved
        repair.approved_at = timezone.now()
        repair.status = RepairOrder.STATUS_APPROVED if approved else RepairOrder.STATUS_REJECTED
        repair.save(update_fields=["customer_approved", "approved_at", "status", "updated_at"])
        return repair


class RepairCompleteSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def save(self, **kwargs):
        repair = self.context["repair"]
        repair.status = RepairOrder.STATUS_COMPLETED
        if self.validated_data["notes"]:
            repair.notes = f"{repair.notes}\n{self.validated_data['notes']}".strip()
        repair.save(update_fields=["status", "notes", "updated_at"])
        return repair


class RepairStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RepairOrder.STATUS_CHOICES)

    def save(self, **kwargs):
        repair = self.context["repair"]
        repair.status = self.validated_data["status"]
        repair.save(update_fields=["status", "updated_at"])
        return repair
