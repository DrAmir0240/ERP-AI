import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0003_auditlog"),
        ("inventory", "0001_initial"),
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_number", models.CharField(editable=False, max_length=30, unique=True)),
                ("order_type", models.CharField(choices=[("physical_sale", "Physical sale"), ("account_sale", "Account sale"), ("repair", "Repair"), ("xbox_sale", "Xbox sale")], max_length=30)),
                ("channel", models.CharField(choices=[("online", "Online"), ("in_store", "In-store")], max_length=20)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("processing", "Processing"), ("ready", "Ready"), ("dispatched", "Dispatched"), ("delivered", "Delivered"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="pending", max_length=30)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("discount_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("discount_note", models.TextField(blank=True)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("payment_status", models.CharField(choices=[("unpaid", "Unpaid"), ("partial", "Partial"), ("paid", "Paid")], default="unpaid", max_length=20)),
                ("courier_name", models.CharField(blank=True, max_length=100)),
                ("courier_phone", models.CharField(blank=True, max_length=20)),
                ("courier_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("notes", models.TextField(blank=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="core.branch")),
                ("cashier", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="cashier_orders", to=settings.AUTH_USER_MODEL)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["customer"], name="orders_order_custome_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["branch", "created_at"], name="orders_order_branch__idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["status"], name="orders_order_status_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["order_type"], name="orders_order_order_t_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["payment_status"], name="orders_order_payment_idx"),
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("item_type", models.CharField(choices=[("product", "Product"), ("game_account", "Game account"), ("game", "Game"), ("repair", "Repair")], max_length=30)),
                ("game_ids", models.JSONField(blank=True, default=list)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="order_items", to="inventory.product")),
                ("stock_item", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="order_items", to="inventory.stockitem")),
                ("account", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="order_items", to="accounts.gameaccount")),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invoice_number", models.CharField(editable=False, max_length=30, unique=True)),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                ("tax_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("pdf_url", models.CharField(blank=True, max_length=500)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="invoice", to="orders.order")),
            ],
            options={
                "ordering": ["-issued_at"],
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("method", models.CharField(choices=[("online", "Online"), ("wallet", "Wallet"), ("cash", "Cash"), ("pos", "POS")], max_length=30)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed"), ("refunded", "Refunded")], default="pending", max_length=20)),
                ("reference_code", models.CharField(blank=True, max_length=100)),
                ("paid_at", models.DateTimeField(auto_now_add=True)),
                ("note", models.TextField(blank=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="orders.order")),
                ("paid_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-paid_at"],
            },
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["order"], name="orders_payment_order_idx"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["status"], name="orders_payment_status_idx"),
        ),
        migrations.CreateModel(
            name="Refund",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reason", models.TextField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("completed", "Completed")], default="pending", max_length=20)),
                ("refund_method", models.CharField(choices=[("wallet", "Wallet"), ("bank_transfer", "Bank transfer"), ("cash", "Cash")], default="wallet", max_length=30)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="refunds", to="orders.order")),
                ("requested_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="refund_requests", to=settings.AUTH_USER_MODEL)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="refund_approvals", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="refund",
            index=models.Index(fields=["status"], name="orders_refund_status_idx"),
        ),
        migrations.AddIndex(
            model_name="refund",
            index=models.Index(fields=["order"], name="orders_refund_order_idx"),
        ),
        migrations.CreateModel(
            name="ReturnPolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("return_days", models.PositiveIntegerField(default=7)),
                ("is_returnable", models.BooleanField(default=True)),
                ("notes", models.TextField(blank=True)),
                ("category", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="return_policy", to="inventory.category")),
            ],
            options={
                "verbose_name_plural": "return policies",
            },
        ),
    ]
