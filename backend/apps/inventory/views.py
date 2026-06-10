from django.db.models import Count, Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly, IsEmployee

from .models import BranchTransfer, Category, Product, StockItem, StockMovement
from .serializers import (
    BranchTransferSerializer,
    BranchTransferStatusSerializer,
    BulkStockItemSerializer,
    CategorySerializer,
    ProductSerializer,
    StockItemSerializer,
    StockMovementSerializer,
    StockStatusUpdateSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(children_count=Count("children")).select_related("parent")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "level", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        parent = self.request.query_params.get("parent")
        level = self.request.query_params.get("level")
        if parent:
            queryset = queryset.filter(parent_id=parent)
        if level:
            queryset = queryset.filter(level=level)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").annotate(
        available_count=Count("stock_items", filter=Q(stock_items__status=StockItem.STATUS_AVAILABLE)),
        total_stock_count=Count("stock_items"),
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "barcode_prefix", "description", "category__name"]
    ordering_fields = ["name", "sell_price", "buy_price", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        branch = self.request.query_params.get("branch")
        stock_status = self.request.query_params.get("status")
        is_active = self.request.query_params.get("is_active")
        if category:
            queryset = queryset.filter(category_id=category)
        if branch:
            queryset = queryset.filter(stock_items__branch_id=branch)
        if stock_status:
            queryset = queryset.filter(stock_items__status=stock_status)
        if is_active in {"true", "false"}:
            queryset = queryset.filter(is_active=is_active == "true")
        return queryset.distinct()


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.select_related("product", "branch")
    serializer_class = StockItemSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["barcode", "serial_number", "product__name", "branch__name"]
    ordering_fields = ["created_at", "barcode", "status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        product = self.request.query_params.get("product")
        branch = self.request.query_params.get("branch")
        stock_status = self.request.query_params.get("status")
        if product:
            queryset = queryset.filter(product_id=product)
        if branch:
            queryset = queryset.filter(branch_id=branch)
        if stock_status:
            queryset = queryset.filter(status=stock_status)
        return queryset

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk(self, request):
        serializer = BulkStockItemSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        items = serializer.save()
        return Response(StockItemSerializer(items, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"], url_path="status")
    def status(self, request, pk=None):
        item = self.get_object()
        serializer = StockStatusUpdateSerializer(data=request.data, context={"request": request, "item": item})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(StockItemSerializer(item).data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related("item__product", "from_branch", "to_branch", "user")
    serializer_class = StockMovementSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["item__barcode", "item__product__name", "note"]
    ordering_fields = ["created_at", "movement_type"]

    def get_queryset(self):
        queryset = super().get_queryset()
        branch = self.request.query_params.get("branch")
        movement_type = self.request.query_params.get("type")
        product = self.request.query_params.get("product")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if branch:
            queryset = queryset.filter(Q(from_branch_id=branch) | Q(to_branch_id=branch) | Q(item__branch_id=branch))
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        if product:
            queryset = queryset.filter(item__product_id=product)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset


class BranchTransferViewSet(viewsets.ModelViewSet):
    queryset = BranchTransfer.objects.select_related("from_branch", "to_branch", "requested_by", "approved_by")
    serializer_class = BranchTransferSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["from_branch__name", "to_branch__name", "requested_by__phone", "notes"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        branch = self.request.query_params.get("branch")
        transfer_status = self.request.query_params.get("status")
        if branch:
            queryset = queryset.filter(Q(from_branch_id=branch) | Q(to_branch_id=branch))
        if transfer_status:
            queryset = queryset.filter(status=transfer_status)
        return queryset

    @action(detail=True, methods=["put"], url_path="status")
    def status(self, request, pk=None):
        transfer = self.get_object()
        serializer = BranchTransferStatusSerializer(data=request.data, context={"request": request, "transfer": transfer})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(BranchTransferSerializer(transfer).data)
