from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.inventory.models import StockItem

from .models import Invoice, Order, OrderItem, Payment, Refund, ReturnPolicy


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True, default="")
    stock_item_barcode = serializers.CharField(source="stock_item.barcode", read_only=True, default="")
    account_name = serializers.CharField(source="account.name", read_only=True, default="")

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "order",
            "item_type",
            "product",
            "product_name",
            "stock_item",
            "stock_item_barcode",
            "account",
            "account_name",
            "game_ids",
            "quantity",
            "unit_price",
            "total_price",
        )
        read_only_fields = ("id", "order", "product_name", "stock_item_barcode", "account_name")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    cashier_phone = serializers.CharField(source="cashier.phone", read_only=True, default="")
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    order_type_display = serializers.CharField(source="get_order_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_status_display = serializers.CharField(source="get_payment_status_display", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "order_type",
            "order_type_display",
            "channel",
            "branch",
            "branch_name",
            "customer",
            "customer_phone",
            "customer_name",
            "cashier",
            "cashier_phone",
            "status",
            "status_display",
            "subtotal",
            "discount_amount",
            "discount_note",
            "tax_amount",
            "total",
            "payment_status",
            "payment_status_display",
            "courier_name",
            "courier_phone",
            "courier_fee",
            "notes",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "order_number",
            "order_type_display",
            "branch_name",
            "customer_phone",
            "customer_name",
            "cashier_phone",
            "status_display",
            "payment_status_display",
            "items",
            "created_at",
            "updated_at",
        )


class OrderListSerializer(serializers.ModelSerializer):
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    order_type_display = serializers.CharField(source="get_order_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_status_display = serializers.CharField(source="get_payment_status_display", read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "order_type",
            "order_type_display",
            "channel",
            "branch",
            "branch_name",
            "customer",
            "customer_phone",
            "customer_name",
            "status",
            "status_display",
            "total",
            "payment_status",
            "payment_status_display",
            "item_count",
            "created_at",
        )
        read_only_fields = fields


class CreateOrderSerializer(serializers.Serializer):
    order_type = serializers.ChoiceField(choices=Order.TYPE_CHOICES)
    channel = serializers.ChoiceField(choices=Order.CHANNEL_CHOICES)
    branch = serializers.IntegerField()
    customer = serializers.UUIDField()
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_note = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)

    @transaction.atomic
    def create(self, validated_data):
        from apps.core.models import Branch, User

        branch = Branch.objects.get(pk=validated_data["branch"])
        customer = User.objects.get(pk=validated_data["customer"])
        user = self.context["request"].user

        order = Order.objects.create(
            order_type=validated_data["order_type"],
            channel=validated_data["channel"],
            branch=branch,
            customer=customer,
            cashier=user if validated_data["channel"] == Order.CHANNEL_IN_STORE else None,
            discount_amount=validated_data["discount_amount"],
            discount_note=validated_data["discount_note"],
            notes=validated_data["notes"],
        )

        subtotal = Decimal("0")
        for item_data in validated_data["items"]:
            item_type = item_data.get("item_type", "product")
            quantity = int(item_data.get("quantity", 1))
            unit_price = Decimal(str(item_data.get("unit_price", "0")))
            total_price = unit_price * quantity

            oi = OrderItem.objects.create(
                order=order,
                item_type=item_type,
                product_id=item_data.get("product_id"),
                stock_item_id=item_data.get("stock_item_id"),
                account_id=item_data.get("account_id"),
                game_ids=item_data.get("game_ids", []),
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )

            if oi.stock_item_id:
                StockItem.objects.filter(pk=oi.stock_item_id, status=StockItem.STATUS_AVAILABLE).update(status=StockItem.STATUS_SOLD)

            subtotal += total_price

        order.subtotal = subtotal
        order.total = subtotal - order.discount_amount + order.tax_amount
        order.save(update_fields=["subtotal", "total", "updated_at"])
        return order


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def save(self, **kwargs):
        order = self.context["order"]
        new_status = self.validated_data["status"]
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
        return order


class OrderCourierSerializer(serializers.Serializer):
    courier_name = serializers.CharField(max_length=100)
    courier_phone = serializers.CharField(max_length=20)
    courier_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, **kwargs):
        order = self.context["order"]
        order.courier_name = self.validated_data["courier_name"]
        order.courier_phone = self.validated_data["courier_phone"]
        order.courier_fee = self.validated_data["courier_fee"]
        order.save(update_fields=["courier_name", "courier_phone", "courier_fee", "updated_at"])
        return order


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")

    @transaction.atomic
    def save(self, **kwargs):
        order = self.context["order"]
        if order.status in {Order.STATUS_COMPLETED, Order.STATUS_CANCELLED}:
            raise serializers.ValidationError("Cannot cancel a completed or already cancelled order.")

        for item in order.items.select_related("stock_item").all():
            if item.stock_item_id:
                StockItem.objects.filter(pk=item.stock_item_id).update(status=StockItem.STATUS_AVAILABLE)

        order.status = Order.STATUS_CANCELLED
        order.notes = f"{order.notes}\nCancellation: {self.validated_data['reason']}".strip()
        order.save(update_fields=["status", "notes", "updated_at"])
        return order


class InvoiceSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id",
            "invoice_number",
            "order",
            "order_number",
            "issued_at",
            "tax_rate",
            "tax_amount",
            "total",
            "pdf_url",
            "created_at",
        )
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    paid_by_phone = serializers.CharField(source="paid_by.phone", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "order",
            "method",
            "amount",
            "status",
            "reference_code",
            "paid_by",
            "paid_by_phone",
            "paid_at",
            "note",
        )
        read_only_fields = ("id", "paid_by", "paid_by_phone", "paid_at")

    def create(self, validated_data):
        validated_data["paid_by"] = self.context["request"].user
        payment = Payment.objects.create(**validated_data)

        if payment.status == Payment.STATUS_COMPLETED:
            self._update_order_payment_status(payment.order)

        return payment

    def _update_order_payment_status(self, order):
        total_paid = sum(
            p.amount for p in order.payments.filter(status=Payment.STATUS_COMPLETED)
        )
        if total_paid >= order.total:
            order.payment_status = Order.PAYMENT_PAID
        elif total_paid > 0:
            order.payment_status = Order.PAYMENT_PARTIAL
        else:
            order.payment_status = Order.PAYMENT_UNPAID
        order.save(update_fields=["payment_status", "updated_at"])


class RefundSerializer(serializers.ModelSerializer):
    requested_by_phone = serializers.CharField(source="requested_by.phone", read_only=True)
    approved_by_phone = serializers.CharField(source="approved_by.phone", read_only=True, default="")
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = Refund
        fields = (
            "id",
            "order",
            "order_number",
            "requested_by",
            "requested_by_phone",
            "approved_by",
            "approved_by_phone",
            "reason",
            "amount",
            "status",
            "refund_method",
            "created_at",
            "completed_at",
        )
        read_only_fields = ("id", "requested_by", "requested_by_phone", "approved_by", "approved_by_phone", "order_number", "created_at", "completed_at")

    def create(self, validated_data):
        validated_data["requested_by"] = self.context["request"].user
        return Refund.objects.create(**validated_data)


class RefundActionSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def approve(self):
        refund = self.context["refund"]
        user = self.context["request"].user
        refund.status = Refund.STATUS_APPROVED
        refund.approved_by = user
        refund.save(update_fields=["status", "approved_by", "updated_at"])
        return refund

    def reject(self):
        refund = self.context["refund"]
        user = self.context["request"].user
        refund.status = Refund.STATUS_REJECTED
        refund.approved_by = user
        refund.save(update_fields=["status", "approved_by", "updated_at"])
        return refund

    def complete(self):
        refund = self.context["refund"]
        refund.status = Refund.STATUS_COMPLETED
        refund.completed_at = timezone.now()
        refund.save(update_fields=["status", "completed_at", "updated_at"])
        return refund


class ReturnPolicySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ReturnPolicy
        fields = ("id", "category", "category_name", "return_days", "is_returnable", "notes")
        read_only_fields = ("id", "category_name")
