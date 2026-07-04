from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class RepairSettings(models.Model):
    markup_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("20.00"))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "repair settings"

    def __str__(self):
        return f"Repair markup: {self.markup_percent}%"

    @classmethod
    def get_markup(cls):
        obj = cls.objects.first()
        if obj:
            return obj.markup_percent
        return Decimal("20.00")


class RepairOrder(TimestampedModel):
    DEVICE_CONSOLE = "console"
    DEVICE_CONTROLLER = "controller"
    DEVICE_OTHER = "other"
    DEVICE_CHOICES = (
        (DEVICE_CONSOLE, "Console"),
        (DEVICE_CONTROLLER, "Controller"),
        (DEVICE_OTHER, "Other"),
    )

    STATUS_PENDING = "pending"
    STATUS_RECEIVED = "received"
    STATUS_UNDER_REVIEW = "under_review"
    STATUS_PRICE_SET = "price_set"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_IN_REPAIR = "in_repair"
    STATUS_REPAIRED = "repaired"
    STATUS_DISPATCHED = "dispatched"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_RECEIVED, "Received"),
        (STATUS_UNDER_REVIEW, "Under review"),
        (STATUS_PRICE_SET, "Price set"),
        (STATUS_APPROVED, "Approved by customer"),
        (STATUS_REJECTED, "Rejected by customer"),
        (STATUS_IN_REPAIR, "In repair"),
        (STATUS_REPAIRED, "Repaired"),
        (STATUS_DISPATCHED, "Dispatched"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="repair_detail")
    device_type = models.CharField(max_length=50, choices=DEVICE_CHOICES)
    device_model = models.CharField(max_length=100)
    issue_description = models.TextField()
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="repair_assignments", null=True, blank=True)
    technician_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    markup_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customer_approved = models.NullBooleanField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["technician"]),
        ]

    def calculate_final_price(self):
        self.final_price = self.technician_price * (1 + self.markup_percent / 100)

    def __str__(self):
        return f"Repair #{self.id} - {self.device_model}"
