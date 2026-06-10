from django.db import transaction
from rest_framework import serializers

from apps.core.models import Branch

from .models import BranchTransfer, Category, Product, StockItem, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    children_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "parent", "level", "slug", "children_count", "created_at", "updated_at")
        read_only_fields = ("id", "level", "children_count", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    available_count = serializers.IntegerField(read_only=True)
    total_stock_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "category",
            "category_name",
            "barcode_prefix",
            "buy_price",
            "sell_price",
            "description",
            "is_active",
            "available_count",
            "total_stock_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "category_name", "available_count", "total_stock_count", "created_at", "updated_at")


class StockItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = StockItem
        fields = (
            "id",
            "product",
            "product_name",
            "branch",
            "branch_name",
            "barcode",
            "serial_number",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "product_name", "branch_name", "created_at", "updated_at")

    def create(self, validated_data):
        item = StockItem(**validated_data)
        item._movement_user = self.context["request"].user
        item._movement_note = "Initial stock entry"
        item.save()
        return item


class BulkStockItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.filter(is_active=True))
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        normalized = []
        barcodes = set()
        for index, item in enumerate(value, start=1):
            barcode = str(item.get("barcode", "")).strip()
            if not barcode:
                raise serializers.ValidationError(f"Item {index} requires barcode.")
            if barcode in barcodes:
                raise serializers.ValidationError(f"Duplicate barcode {barcode}.")
            barcodes.add(barcode)
            normalized.append({"barcode": barcode, "serial_number": str(item.get("serial_number", "")).strip()})
        existing = set(StockItem.objects.filter(barcode__in=barcodes).values_list("barcode", flat=True))
        if existing:
            raise serializers.ValidationError(f"Barcode already exists: {', '.join(sorted(existing))}.")
        return normalized

    @transaction.atomic
    def create(self, validated_data):
        product = validated_data["product"]
        branch = validated_data["branch"]
        note = validated_data.get("note", "Bulk stock entry")
        user = self.context["request"].user
        stock_items = [
            StockItem(product=product, branch=branch, barcode=item["barcode"], serial_number=item["serial_number"])
            for item in validated_data["items"]
        ]
        created_items = StockItem.objects.bulk_create(stock_items)
        StockMovement.objects.bulk_create(
            [
                StockMovement(item=item, movement_type=StockMovement.TYPE_PURCHASE, to_branch=branch, user=user, note=note)
                for item in created_items
            ]
        )
        return created_items


class StockStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=StockItem.STATUS_CHOICES)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.filter(is_active=True), required=False)
    note = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        item = self.context["item"]
        user = self.context["request"].user
        previous_branch = item.branch
        previous_status = item.status
        new_branch = self.validated_data.get("branch", item.branch)
        new_status = self.validated_data["status"]
        item.branch = new_branch
        item.status = new_status
        movement_type = StockMovement.TYPE_ADJUSTMENT
        if new_status == StockItem.STATUS_SOLD:
            movement_type = StockMovement.TYPE_SALE
        elif new_status == StockItem.STATUS_RETURNED:
            movement_type = StockMovement.TYPE_RETURN
        elif previous_branch != new_branch or new_status == StockItem.STATUS_TRANSFERRED:
            movement_type = StockMovement.TYPE_TRANSFER_OUT
        item._movement_type = movement_type
        item._movement_from_branch = previous_branch
        item._movement_to_branch = new_branch
        item._movement_user = user
        item._movement_note = self.validated_data.get("note") or f"Status changed from {previous_status} to {new_status}"
        item.save(update_fields=["branch", "status", "updated_at"])
        return item


class StockMovementSerializer(serializers.ModelSerializer):
    item_barcode = serializers.CharField(source="item.barcode", read_only=True)
    product_name = serializers.CharField(source="item.product.name", read_only=True)
    from_branch_name = serializers.CharField(source="from_branch.name", read_only=True)
    to_branch_name = serializers.CharField(source="to_branch.name", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = StockMovement
        fields = (
            "id",
            "item",
            "item_barcode",
            "product_name",
            "movement_type",
            "from_branch",
            "from_branch_name",
            "to_branch",
            "to_branch_name",
            "order_id",
            "user",
            "user_phone",
            "note",
            "created_at",
        )
        read_only_fields = fields


class BranchTransferSerializer(serializers.ModelSerializer):
    from_branch_name = serializers.CharField(source="from_branch.name", read_only=True)
    to_branch_name = serializers.CharField(source="to_branch.name", read_only=True)
    requested_by_phone = serializers.CharField(source="requested_by.phone", read_only=True)
    approved_by_phone = serializers.CharField(source="approved_by.phone", read_only=True)
    item_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = BranchTransfer
        fields = (
            "id",
            "from_branch",
            "from_branch_name",
            "to_branch",
            "to_branch_name",
            "requested_by",
            "requested_by_phone",
            "approved_by",
            "approved_by_phone",
            "status",
            "items",
            "item_ids",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "requested_by", "approved_by", "items", "created_at", "updated_at")

    def validate_item_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one stock item is required.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate stock item IDs are not allowed.")
        return value

    def validate(self, attrs):
        from_branch = attrs.get("from_branch", getattr(self.instance, "from_branch", None))
        to_branch = attrs.get("to_branch", getattr(self.instance, "to_branch", None))
        if from_branch and to_branch and from_branch == to_branch:
            raise serializers.ValidationError({"to_branch": "Transfer destination must be different from origin."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        item_ids = validated_data.pop("item_ids", [])
        stock_items = list(StockItem.objects.select_related("product", "branch").filter(id__in=item_ids))
        found_ids = {item.id for item in stock_items}
        missing_ids = sorted(set(item_ids) - found_ids)
        if missing_ids:
            raise serializers.ValidationError({"item_ids": f"Stock items not found: {missing_ids}."})
        from_branch = validated_data["from_branch"]
        invalid_items = [item.barcode for item in stock_items if item.branch_id != from_branch.id or item.status != StockItem.STATUS_AVAILABLE]
        if invalid_items:
            raise serializers.ValidationError({"item_ids": f"Items must be available in origin branch: {', '.join(invalid_items)}."})
        transfer = BranchTransfer.objects.create(
            **validated_data,
            requested_by=self.context["request"].user,
            items=[{"item_id": item.id, "barcode": item.barcode, "product_name": item.product.name} for item in stock_items],
        )
        return transfer


class BranchTransferStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=BranchTransfer.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)

    @transaction.atomic
    def save(self, **kwargs):
        transfer = self.context["transfer"]
        user = self.context["request"].user
        new_status = self.validated_data["status"]
        transfer.status = new_status
        if new_status in {BranchTransfer.STATUS_APPROVED, BranchTransfer.STATUS_IN_TRANSIT, BranchTransfer.STATUS_COMPLETED} and not transfer.approved_by:
            transfer.approved_by = user
        if new_status == BranchTransfer.STATUS_IN_TRANSIT:
            self._mark_items_transferred(transfer, user)
        elif new_status == BranchTransfer.STATUS_COMPLETED:
            self._complete_transfer(transfer, user)
        transfer.save(update_fields=["status", "approved_by", "updated_at"])
        return transfer

    def _get_items(self, transfer):
        item_ids = [item["item_id"] for item in transfer.items]
        return StockItem.objects.select_for_update().filter(id__in=item_ids).select_related("product", "branch")

    def _mark_items_transferred(self, transfer, user):
        for item in self._get_items(transfer):
            item.status = StockItem.STATUS_TRANSFERRED
            item._movement_type = StockMovement.TYPE_TRANSFER_OUT
            item._movement_from_branch = transfer.from_branch
            item._movement_to_branch = transfer.to_branch
            item._movement_user = user
            item._movement_note = self.validated_data.get("note") or f"Transfer #{transfer.id} dispatched"
            item.save(update_fields=["status", "updated_at"])

    def _complete_transfer(self, transfer, user):
        for item in self._get_items(transfer):
            item.branch = transfer.to_branch
            item.status = StockItem.STATUS_AVAILABLE
            item._movement_type = StockMovement.TYPE_TRANSFER_IN
            item._movement_from_branch = transfer.from_branch
            item._movement_to_branch = transfer.to_branch
            item._movement_user = user
            item._movement_note = self.validated_data.get("note") or f"Transfer #{transfer.id} completed"
            item.save(update_fields=["branch", "status", "updated_at"])
