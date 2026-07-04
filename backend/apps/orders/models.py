import uuid

from django.conf import settings
from django.db import models

from apps.core.models import Branch, TimestampedModel
from apps.inventory.models import Category


class Order(TimestampedModel):
    TYPE_PHYSICAL_SALE = "physical_sale"
    TYPE_ACCOUNT_SALE = "account_sale"
    TYPE_REPAIR = "repair"
    TYPE_XBOX_SALE = "xbox_sale"
    TYPE_CHOICES = (
        (TYPE_PHYSICAL_SALE, "Physical sale"),
        (TYPE_ACCOUNT_SALE, "Account sale"),
        (TYPE_REPAIR, "Repair"),
        (TYPE_XBOX_SALE, "Xbox sale"),
    )

    CHANNEL_ONLINE = "online"
    CHANNEL_IN_STORE = "in_store"
    CHANNEL_CHOICES = (
        (CHANNEL_ONLINE, "Online"),
        (CHANNEL_IN_STORE, "In-store"),
    )

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PROCESSING = "processing"
    STATUS_READY = "ready"
    STATUS_DISPATCHED = "dispatched"
    STATUS_DELIVERED = "delivered"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_READY, "Ready"),
        (STATUS_DISPATCHED, "Dispatched"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PARTIAL = "partial"
    PAYMENT_PAID = "paid"
    PAYMENT_CHOICES = (
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PARTIAL, "Partial"),
        (PAYMENT_PAID, "Paid"),
    )

    order_number = models.CharField(max_length=30, unique=True, editable=False)
    order_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="orders")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="cashier_orders", null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_note = models.TextField(blank=True)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_UNPAID)
    courier_name = models.CharField(max_length=100, blank=True)
    courier_phone = models.CharField(max_length=20, blank=True)
    courier_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["branch", "created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["order_type"]),
            models.Index(fields=["payment_status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            from django.utils import timezone
            now = timezone.now()
            year = now.strftime("%y%m")
            last = Order.objects.filter(order_number__startswith=f"ORD-{year}").order_by("-order_number").values_list("order_number", flat=True).first()
            seq = 1
            if last:
                try:
                    seq = int(last.split("-")[-1]) + 1
                except ValueError:
                    pass
            self.order_number = f"ORD-{year}-{seq:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    ITEM_TYPE_PRODUCT = "product"
    ITEM_TYPE_GAME_ACCOUNT = "game_account"
    ITEM_TYPE_GAME = "game"
    ITEM_TYPE_REPAIR = "repair"
    ITEM_TYPE_CHOICES = (
        (ITEM_TYPE_PRODUCT, "Product"),
        (ITEM_TYPE_GAME_ACCOUNT, "Game account"),
        (ITEM_TYPE_GAME, "Game"),
        (ITEM_TYPE_REPAIR, "Repair"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=30, choices=ITEM_TYPE_CHOICES)
    product = models.ForeignKey("inventory.Product", on_delete=models.PROTECT, related_name="order_items", null=True, blank=True)
    stock_item = models.ForeignKey("inventory.StockItem", on_delete=models.PROTECT, related_name="order_items", null=True, blank=True)
    account = models.ForeignKey("accounts.GameAccount", on_delete=models.PROTECT, related_name="order_items", null=True, blank=True)
    game_ids = models.JSONField(default=list, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Item #{self.id} - {self.order.order_number}"


class Invoice(TimestampedModel):
    invoice_number = models.CharField(max_length=30, unique=True, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    issued_at = models.DateTimeField(auto_now_add=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pdf_url = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-issued_at"]

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            now = timezone.now()
            year = now.strftime("%y%m")
            last = Invoice.objects.filter(invoice_number__startswith=f"INV-{year}").order_by("-invoice_number").values_list("invoice_number", flat=True).first()
            seq = 1
            if last:
                try:
                    seq = int(last.split("-")[-1]) + 1
                except ValueError:
                    pass
            self.invoice_number = f"INV-{year}-{seq:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class Payment(models.Model):
    METHOD_ONLINE = "online"
    METHOD_WALLET = "wallet"
    METHOD_CASH = "cash"
    METHOD_POS = "pos"
    METHOD_CHOICES = (
        (METHOD_ONLINE, "Online"),
        (METHOD_WALLET, "Wallet"),
        (METHOD_CASH, "Cash"),
        (METHOD_POS, "POS"),
    )

    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_REFUNDED, "Refunded"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reference_code = models.CharField(max_length=100, blank=True)
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    paid_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-paid_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.order.order_number}"


class Refund(TimestampedModel):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_COMPLETED, "Completed"),
    )

    METHOD_WALLET = "wallet"
    METHOD_BANK_TRANSFER = "bank_transfer"
    METHOD_CASH = "cash"
    METHOD_CHOICES = (
        (METHOD_WALLET, "Wallet"),
        (METHOD_BANK_TRANSFER, "Bank transfer"),
        (METHOD_CASH, "Cash"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="refund_requests")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="refund_approvals", null=True, blank=True)
    reason = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    refund_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default=METHOD_WALLET)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"Refund #{self.id} - {self.order.order_number}"


class ReturnPolicy(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name="return_policy")
    return_days = models.PositiveIntegerField(default=7)
    is_returnable = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "return policies"

    def __str__(self):
        return f"{self.category.name} - {self.return_days} days"
