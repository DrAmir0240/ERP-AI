import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("orders", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RepairSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("markup_percent", models.DecimalField(decimal_places=2, default=Decimal("20.00"), max_digits=5)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name_plural": "repair settings",
            },
        ),
        migrations.CreateModel(
            name="RepairOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("device_type", models.CharField(choices=[("console", "Console"), ("controller", "Controller"), ("other", "Other")], max_length=50)),
                ("device_model", models.CharField(max_length=100)),
                ("issue_description", models.TextField()),
                ("technician_price", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("markup_percent", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("final_price", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("customer_approved", models.NullBooleanField()),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("received", "Received"), ("under_review", "Under review"), ("price_set", "Price set"), ("approved", "Approved by customer"), ("rejected", "Rejected by customer"), ("in_repair", "In repair"), ("repaired", "Repaired"), ("dispatched", "Dispatched"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="pending", max_length=30)),
                ("notes", models.TextField(blank=True)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="repair_detail", to="orders.order")),
                ("technician", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="repair_assignments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="repairorder",
            index=models.Index(fields=["status"], name="repair_repairorder_status_idx"),
        ),
        migrations.AddIndex(
            model_name="repairorder",
            index=models.Index(fields=["technician"], name="repair_repairorder_tech_idx"),
        ),
    ]
