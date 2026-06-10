from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from apps.core.models import Branch, TimestampedModel


class Category(TimestampedModel):
    MAX_LEVEL = 3

    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=1)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True)

    class Meta:
        ordering = ["level", "name"]
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(fields=["parent", "name"], name="unique_inventory_category_parent_name"),
            models.CheckConstraint(check=models.Q(level__gte=1) & models.Q(level__lte=3), name="inventory_category_level_1_3"),
        ]

    def clean(self):
        if self.parent and self.parent_id == self.id:
            raise ValidationError({"parent": "A category cannot be its own parent."})
        parent_level = self.parent.level if self.parent else 0
        if parent_level >= self.MAX_LEVEL:
            raise ValidationError({"parent": "Categories support a maximum depth of three levels."})
        self.level = parent_level + 1
        duplicate = Category.objects.filter(parent=self.parent, name=self.name).exclude(pk=self.pk).exists()
        if duplicate:
            raise ValidationError({"name": "A category with this parent and name already exists."})

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or "category"
            slug = base_slug
            suffix = 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(TimestampedModel):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    barcode_prefix = models.CharField(max_length=50, blank=True)
    buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["barcode_prefix"]),
        ]

    def __str__(self):
        return self.name


class StockItem(TimestampedModel):
    STATUS_AVAILABLE = "available"
    STATUS_SOLD = "sold"
    STATUS_RETURNED = "returned"
    STATUS_TRANSFERRED = "transferred"
    STATUS_DAMAGED = "damaged"
    STATUS_CHOICES = (
        (STATUS_AVAILABLE, "Available"),
        (STATUS_SOLD, "Sold"),
        (STATUS_RETURNED, "Returned"),
        (STATUS_TRANSFERRED, "Transferred"),
        (STATUS_DAMAGED, "Damaged"),
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_items")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="stock_items")
    barcode = models.CharField(max_length=100, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["barcode"]),
            models.Index(fields=["product", "status"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.barcode}"


class StockMovement(models.Model):
    TYPE_PURCHASE = "purchase"
    TYPE_SALE = "sale"
    TYPE_RETURN = "return"
    TYPE_TRANSFER_OUT = "transfer_out"
    TYPE_TRANSFER_IN = "transfer_in"
    TYPE_ADJUSTMENT = "adjustment"
    TYPE_CHOICES = (
        (TYPE_PURCHASE, "Purchase"),
        (TYPE_SALE, "Sale"),
        (TYPE_RETURN, "Return"),
        (TYPE_TRANSFER_OUT, "Transfer out"),
        (TYPE_TRANSFER_IN, "Transfer in"),
        (TYPE_ADJUSTMENT, "Adjustment"),
    )

    item = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    from_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="outgoing_stock_movements", null=True, blank=True)
    to_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="incoming_stock_movements", null=True, blank=True)
    order_id = models.PositiveBigIntegerField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="stock_movements", null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["movement_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["from_branch", "to_branch"]),
        ]

    def __str__(self):
        return f"{self.movement_type} - {self.item.barcode}"


class BranchTransfer(TimestampedModel):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_IN_TRANSIT = "in_transit"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_IN_TRANSIT, "In transit"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    from_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="outgoing_transfers")
    to_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="incoming_transfers")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requested_stock_transfers")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="approved_stock_transfers", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    items = models.JSONField(default=list)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["from_branch", "to_branch"]),
        ]

    def clean(self):
        if self.from_branch_id and self.to_branch_id and self.from_branch_id == self.to_branch_id:
            raise ValidationError({"to_branch": "Transfer destination must be different from origin."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_branch} → {self.to_branch} ({self.status})"
