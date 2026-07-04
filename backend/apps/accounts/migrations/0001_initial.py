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
            name="Game",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("platform", models.CharField(choices=[("ps", "PlayStation"), ("xbox", "Xbox"), ("nintendo", "Nintendo")], max_length=20)),
                ("image_url", models.URLField(blank=True, max_length=500)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="GameAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=200, unique=True)),
                ("password", models.CharField(max_length=200)),
                ("account_type", models.CharField(choices=[("ps_online", "PS Online"), ("ps_offline", "PS Offline"), ("xbox", "Xbox"), ("nintendo", "Nintendo")], max_length=20)),
                ("total_capacity", models.PositiveIntegerField(blank=True, default=0)),
                ("sold_count", models.PositiveIntegerField(default=0)),
                ("notes", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AccountGame",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="account_games", to="accounts.gameaccount")),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="account_games", to="accounts.game")),
            ],
        ),
        migrations.CreateModel(
            name="AccountSale",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_id", models.PositiveBigIntegerField(blank=True, null=True)),
                ("sold_games", models.JSONField(default=list)),
                ("sold_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sales", to="accounts.gameaccount")),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="account_purchases", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-sold_at"],
            },
        ),
        migrations.AddIndex(
            model_name="game",
            index=models.Index(fields=["platform"], name="accounts_ga_platfor_idx"),
        ),
        migrations.AddIndex(
            model_name="game",
            index=models.Index(fields=["name"], name="accounts_ga_name_idx"),
        ),
        migrations.AddConstraint(
            model_name="game",
            constraint=models.UniqueConstraint(fields=("name", "platform"), name="unique_accounts_game_name_platform"),
        ),
        migrations.AddIndex(
            model_name="gameaccount",
            index=models.Index(fields=["account_type"], name="accounts_ga_account_idx"),
        ),
        migrations.AddIndex(
            model_name="gameaccount",
            index=models.Index(fields=["email"], name="accounts_ga_email_idx"),
        ),
        migrations.AddIndex(
            model_name="gameaccount",
            index=models.Index(fields=["is_active"], name="accounts_ga_is_acti_idx"),
        ),
        migrations.AddConstraint(
            model_name="accountgame",
            constraint=models.UniqueConstraint(fields=("account", "game"), name="unique_accounts_accountgame_account_game"),
        ),
        migrations.AddIndex(
            model_name="accountsale",
            index=models.Index(fields=["account"], name="accounts_ac_account_idx"),
        ),
        migrations.AddIndex(
            model_name="accountsale",
            index=models.Index(fields=["customer"], name="accounts_ac_custome_idx"),
        ),
        migrations.AddIndex(
            model_name="accountsale",
            index=models.Index(fields=["sold_at"], name="accounts_ac_sold_at_idx"),
        ),
    ]
