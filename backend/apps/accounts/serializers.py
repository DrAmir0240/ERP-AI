from django.db import transaction
from rest_framework import serializers

from .models import AccountGame, AccountSale, Game, GameAccount


class GameSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source="get_platform_display", read_only=True)

    class Meta:
        model = Game
        fields = (
            "id",
            "name",
            "platform",
            "platform_display",
            "image_url",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "platform_display", "created_at", "updated_at")


class GameAccountSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source="get_account_type_display", read_only=True)
    games = serializers.SerializerMethodField()
    game_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = GameAccount
        fields = (
            "id",
            "name",
            "email",
            "password",
            "account_type",
            "account_type_display",
            "total_capacity",
            "sold_count",
            "notes",
            "is_active",
            "games",
            "game_ids",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "account_type_display", "sold_count", "created_at", "updated_at")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def get_games(self, obj):
        account_games = obj.account_games.select_related("game").all()
        return [
            {"id": ag.game.id, "name": ag.game.name, "platform": ag.game.platform}
            for ag in account_games
        ]

    def validate_game_ids(self, value):
        if value:
            existing = set(Game.objects.filter(id__in=value, is_active=True).values_list("id", flat=True))
            missing = sorted(set(value) - existing)
            if missing:
                raise serializers.ValidationError(f"Games not found or inactive: {missing}")
        return value

    @transaction.atomic
    def create(self, validated_data):
        game_ids = validated_data.pop("game_ids", [])
        account = GameAccount.objects.create(**validated_data)
        if game_ids:
            AccountGame.objects.bulk_create(
                [AccountGame(account=account, game_id=gid) for gid in game_ids]
            )
        return account

    @transaction.atomic
    def update(self, instance, validated_data):
        game_ids = validated_data.pop("game_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if game_ids is not None:
            instance.account_games.all().delete()
            AccountGame.objects.bulk_create(
                [AccountGame(account=instance, game_id=gid) for gid in game_ids]
            )
        return instance


class GameAccountListSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source="get_account_type_display", read_only=True)
    game_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = GameAccount
        fields = (
            "id",
            "name",
            "email",
            "account_type",
            "account_type_display",
            "total_capacity",
            "sold_count",
            "is_active",
            "game_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AccountSaleSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = AccountSale
        fields = (
            "id",
            "account",
            "account_name",
            "order_id",
            "customer",
            "customer_phone",
            "customer_name",
            "sold_games",
            "sold_at",
        )
        read_only_fields = ("id", "account_name", "customer_phone", "customer_name", "sold_at")


class CalculatePriceSerializer(serializers.Serializer):
    game_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    account_type = serializers.ChoiceField(
        choices=[GameAccount.TYPE_PS_ONLINE, GameAccount.TYPE_PS_OFFLINE],
        default=GameAccount.TYPE_PS_ONLINE,
    )

    def validate_game_ids(self, value):
        existing = set(Game.objects.filter(id__in=value, is_active=True).values_list("id", flat=True))
        missing = sorted(set(value) - existing)
        if missing:
            raise serializers.ValidationError(f"Games not found or inactive: {missing}")
        return value

    def calculate(self):
        game_ids = self.validated_data["game_ids"]
        account_type = self.validated_data["account_type"]
        games = Game.objects.filter(id__in=game_ids, is_active=True)

        accounts = GameAccount.objects.filter(
            account_type=account_type,
            is_active=True,
            account_games__game_id__in=game_ids,
        ).distinct().prefetch_related("account_games__game")

        result_accounts = []
        for account in accounts:
            account_game_ids = set(account.account_games.values_list("game_id", flat=True))
            covered = set(game_ids) & account_game_ids
            if covered:
                result_accounts.append({
                    "account_id": account.id,
                    "account_name": account.name,
                    "covered_game_ids": sorted(covered),
                    "covered_count": len(covered),
                    "total_capacity": account.total_capacity,
                    "sold_count": account.sold_count,
                })

        return {
            "requested_games": [{"id": g.id, "name": g.name} for g in games],
            "matching_accounts": sorted(result_accounts, key=lambda a: -a["covered_count"]),
            "total_games_requested": len(game_ids),
        }
