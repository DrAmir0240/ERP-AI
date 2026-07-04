from django.db.models import Count
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly, IsEmployee

from .models import AccountSale, Game, GameAccount
from .serializers import (
    AccountSaleSerializer,
    CalculatePriceSerializer,
    GameAccountListSerializer,
    GameAccountSerializer,
    GameSerializer,
)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "platform", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        platform = self.request.query_params.get("platform")
        is_active = self.request.query_params.get("is_active")
        if platform:
            queryset = queryset.filter(platform=platform)
        if is_active in {"true", "false"}:
            queryset = queryset.filter(is_active=is_active == "true")
        return queryset


class GameAccountViewSet(viewsets.ModelViewSet):
    queryset = GameAccount.objects.all()
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "notes"]
    ordering_fields = ["name", "account_type", "sold_count", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return GameAccountListSerializer
        return GameAccountSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.annotate(game_count=Count("account_games"))
        account_type = self.request.query_params.get("type")
        is_active = self.request.query_params.get("is_active")
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        if is_active in {"true", "false"}:
            queryset = queryset.filter(is_active=is_active == "true")
        return queryset

    @action(detail=True, methods=["get"], url_path="sales")
    def sales(self, request, pk=None):
        account = self.get_object()
        sales = AccountSale.objects.filter(account=account).select_related("customer")
        serializer = AccountSaleSerializer(sales, many=True)
        return Response(serializer.data)


class AccountSaleViewSet(viewsets.ModelViewSet):
    queryset = AccountSale.objects.select_related("account", "customer")
    serializer_class = AccountSaleSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["account__name", "customer__phone", "customer__full_name"]
    ordering_fields = ["sold_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        account = self.request.query_params.get("account")
        customer = self.request.query_params.get("customer")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if account:
            queryset = queryset.filter(account_id=account)
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if date_from:
            queryset = queryset.filter(sold_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(sold_at__date__lte=date_to)
        return queryset


class CalculatePriceView(viewsets.ViewSet):
    permission_classes = [IsEmployee]

    def create(self, request):
        serializer = CalculatePriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.calculate()
        return Response(result, status=status.HTTP_200_OK)
