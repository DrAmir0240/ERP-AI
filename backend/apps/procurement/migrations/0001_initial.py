import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0003_auditlog"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("company_name", models.CharField(max_length=200)),
                ("contact_person", models.CharField(blank=True, max_length=100)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=200)),
                ("address", models.TextField(blank=True)),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("notes", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["company_name"],
            },
        ),
        migrations.AddIndex(
            model_name="supplier",
            index=models.Index(fields=["company_name"], name="procurement_supplier_name_idx"),
        ),
        migrations.CreateModel(
            name="PurchaseRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("request_number", models.CharField(editable=False, max_length=30, unique=True)),
                ("items", models.JSONField(default=list)),
                ("reason", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected"), ("purchased", "Purchased")], default="draft", max_length=20)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("requested_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_requests", to=settings.AUTH_USER_MODEL)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_purchase_requests", to=settings.AUTH_USER_MODEL)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_requests", to="core.branch")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="purchaserequest",
            index=models.Index(fields=["status"], name="procurement_pr_status_idx"),
        ),
        migrations.CreateModel(
            name="PurchaseOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("purchase_number", models.CharField(editable=False, max_length=30, unique=True)),
                ("items", models.JSONField(default=list)),
                ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("payment_method", models.CharField(choices=[("cash", "Cash"), ("credit", "Credit"), ("cheque", "Cheque")], default="cash", max_length=20)),
                ("supplier_invoice_no", models.CharField(blank=True, max_length=100)),
                ("notes", models.TextField(blank=True)),
                ("purchased_at", models.DateTimeField(auto_now_add=True)),
                ("request", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="purchase_orders", to="procurement.purchaserequest")),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_orders", to="procurement.supplier")),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_orders", to="core.branch")),
                ("purchased_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-purchased_at"],
            },
        ),
        migrations.AddIndex(
            model_name="purchaseorder",
            index=models.Index(fields=["supplier"], name="procurement_po_supplier_idx"),
        ),
        migrations.AddIndex(
            model_name="purchaseorder",
            index=models.Index(fields=["purchased_at"], name="procurement_po_date_idx"),
        ),
    ]
