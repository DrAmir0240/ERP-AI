from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.inventory.models import StockItem, StockMovement

from .models import PurchaseOrder, PurchaseRequest, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            "id",
            "company_name",
            "contact_person",
            "phone",
            "email",
            "address",
            "balance",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class SupplierListSerializer(serializers.ModelSerializer):
    order_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Supplier
        fields = ("id", "company_name", "contact_person", "phone", "is_active", "balance", "order_count")
        read_only_fields = fields


class PurchaseRequestSerializer(serializers.ModelSerializer):
    requested_by_phone = serializers.CharField(source="requested_by.phone", read_only=True)
    approved_by_phone = serializers.CharField(source="approved_by.phone", read_only=True, default="")
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = (
            "id",
            "request_number",
            "requested_by",
            "requested_by_phone",
            "branch",
            "branch_name",
            "items",
            "reason",
            "status",
            "status_display",
            "approved_by",
            "approved_by_phone",
            "approved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "request_number",
            "requested_by",
            "requested_by_phone",
            "branch_name",
            "status_display",
            "approved_by",
            "approved_by_phone",
            "approved_at",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["requested_by"] = self.context["request"].user
        return PurchaseRequest.objects.create(**validated_data)


class PurchaseRequestStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=PurchaseRequest.STATUS_CHOICES)

    def save(self, **kwargs):
        pr = self.context["purchase_request"]
        new_status = self.validated_data["status"]
        user = self.context["request"].user

        if new_status == PurchaseRequest.STATUS_APPROVED:
            pr.approved_by = user
            pr.approved_at = timezone.now()
            pr.status = new_status
            pr.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        elif new_status == PurchaseRequest.STATUS_REJECTED:
            pr.approved_by = user
            pr.approved_at = timezone.now()
            pr.status = new_status
            pr.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        else:
            pr.status = new_status
            pr.save(update_fields=["status", "updated_at"])
        return pr


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.company_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    request_number = serializers.CharField(source="request.request_number", read_only=True, default="")
    purchased_by_phone = serializers.CharField(source="purchased_by.phone", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = (
            "id",
            "purchase_number",
            "request",
            "request_number",
            "supplier",
            "supplier_name",
            "branch",
            "branch_name",
            "items",
            "total_amount",
            "payment_method",
            "payment_method_display",
            "supplier_invoice_no",
            "notes",
            "purchased_by",
            "purchased_by_phone",
            "purchased_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "purchase_number",
            "request_number",
            "supplier_name",
            "branch_name",
            "payment_method_display",
            "purchased_by",
            "purchased_by_phone",
            "purchased_at",
            "created_at",
        )


class CreatePurchaseOrderSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(required=False, allow_null=True)
    supplier = serializers.IntegerField()
    branch = serializers.IntegerField()
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=PurchaseOrder.PAYMENT_CHOICES)
    supplier_invoice_no = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    @transaction.atomic
    def create(self, validated_data):
        from apps.core.models import Branch

        user = self.context["request"].user
        branch = Branch.objects.get(pk=validated_data["branch"])
        supplier = Supplier.objects.get(pk=validated_data["supplier"])

        po = PurchaseOrder.objects.create(
            request_id=validated_data.get("request_id"),
            supplier=supplier,
            branch=branch,
            items=validated_data["items"],
            total_amount=validated_data["total_amount"],
            payment_method=validated_data["payment_method"],
            supplier_invoice_no=validated_data["supplier_invoice_no"],
            notes=validated_data["notes"],
            purchased_by=user,
        )

        if po.request:
            po.request.status = PurchaseRequest.STATUS_PURCHASED
            po.request.save(update_fields=["status", "updated_at"])

        for item_data in validated_data["items"]:
            stock_item_id = item_data.get("stock_item_id")
            if stock_item_id:
                StockMovement.objects.create(
                    item_id=stock_item_id,
                    movement_type=StockMovement.TYPE_PURCHASE,
                    to_branch=branch,
                    order_id=po.pk,
                    user=user,
                    note=f"Purchase Order {po.purchase_number}",
                )

        return po
