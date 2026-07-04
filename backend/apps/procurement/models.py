from django.conf import settings
from django.db import models

from apps.core.models import Branch, TimestampedModel


class Supplier(TimestampedModel):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["company_name"]
        indexes = [
            models.Index(fields=["company_name"]),
        ]

    def __str__(self):
        return self.company_name


class PurchaseRequest(TimestampedModel):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_PURCHASED = "purchased"
    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_PURCHASED, "Purchased"),
    )

    request_number = models.CharField(max_length=30, unique=True, editable=False)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="purchase_requests")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="purchase_requests")
    items = models.JSONField(default=list)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="approved_purchase_requests", null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.request_number:
            from django.utils import timezone
            now = timezone.now()
            year = now.strftime("%y%m")
            last = PurchaseRequest.objects.filter(request_number__startswith=f"PR-{year}").order_by("-request_number").values_list("request_number", flat=True).first()
            seq = 1
            if last:
                try:
                    seq = int(last.split("-")[-1]) + 1
                except ValueError:
                    pass
            self.request_number = f"PR-{year}-{seq:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_number


class PurchaseOrder(TimestampedModel):
    PAYMENT_CASH = "cash"
    PAYMENT_CREDIT = "credit"
    PAYMENT_CHEQUE = "cheque"
    PAYMENT_CHOICES = (
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_CREDIT, "Credit"),
        (PAYMENT_CHEQUE, "Cheque"),
    )

    purchase_number = models.CharField(max_length=30, unique=True, editable=False)
    request = models.ForeignKey(PurchaseRequest, on_delete=models.SET_NULL, related_name="purchase_orders", null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchase_orders")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="purchase_orders")
    items = models.JSONField(default=list)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    supplier_invoice_no = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    purchased_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="purchase_orders")
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]
        indexes = [
            models.Index(fields=["supplier"]),
            models.Index(fields=["purchased_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.purchase_number:
            from django.utils import timezone
            now = timezone.now()
            year = now.strftime("%y%m")
            last = PurchaseOrder.objects.filter(purchase_number__startswith=f"PO-{year}").order_by("-purchase_number").values_list("purchase_number", flat=True).first()
            seq = 1
            if last:
                try:
                    seq = int(last.split("-")[-1]) + 1
                except ValueError:
                    pass
            self.purchase_number = f"PO-{year}-{seq:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.purchase_number
