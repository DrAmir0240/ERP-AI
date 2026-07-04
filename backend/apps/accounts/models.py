from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class GameAccount(TimestampedModel):
    TYPE_PS_ONLINE = "ps_online"
    TYPE_PS_OFFLINE = "ps_offline"
    TYPE_XBOX = "xbox"
    TYPE_NINTENDO = "nintendo"
    TYPE_CHOICES = (
        (TYPE_PS_ONLINE, "PS Online"),
        (TYPE_PS_OFFLINE, "PS Offline"),
        (TYPE_XBOX, "Xbox"),
        (TYPE_NINTENDO, "Nintendo"),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    total_capacity = models.PositiveIntegerField(default=0, blank=True)
    sold_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["account_type"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


class Game(TimestampedModel):
    PLATFORM_PS = "ps"
    PLATFORM_XBOX = "xbox"
    PLATFORM_NINTENDO = "nintendo"
    PLATFORM_CHOICES = (
        (PLATFORM_PS, "PlayStation"),
        (PLATFORM_XBOX, "Xbox"),
        (PLATFORM_NINTENDO, "Nintendo"),
    )

    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    image_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["platform"]),
            models.Index(fields=["name"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["name", "platform"], name="unique_accounts_game_name_platform"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"


class AccountGame(models.Model):
    account = models.ForeignKey(GameAccount, on_delete=models.CASCADE, related_name="account_games")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="account_games")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["account", "game"], name="unique_accounts_accountgame_account_game"),
        ]

    def __str__(self):
        return f"{self.account.name} - {self.game.name}"


class AccountSale(models.Model):
    account = models.ForeignKey(GameAccount, on_delete=models.PROTECT, related_name="sales")
    order_id = models.PositiveBigIntegerField(null=True, blank=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="account_purchases")
    sold_games = models.JSONField(default=list)
    sold_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sold_at"]
        indexes = [
            models.Index(fields=["account"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["sold_at"]),
        ]

    def __str__(self):
        return f"Sale #{self.id} - {self.account.name}"
