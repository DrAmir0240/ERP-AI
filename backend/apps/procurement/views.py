from django.db.models import Count
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdmin, IsEmployee

from .models import PurchaseOrder, PurchaseRequest, Supplier
from .serializers import (
    CreatePurchaseOrderSerializer,
    PurchaseOrderSerializer,
    PurchaseRequestSerializer,
    PurchaseRequestStatusSerializer,
    SupplierListSerializer,
    SupplierSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company_name", "contact_person", "phone"]
    ordering_fields = ["company_name", "balance", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return SupplierListSerializer
        return SupplierSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.annotate(order_count=Count("purchase_orders"))
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        return queryset


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.select_related("requested_by", "approved_by", "branch")
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["request_number", "reason"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        pr_status = self.request.query_params.get("status")
        branch = self.request.query_params.get("branch")
        if pr_status:
            queryset = queryset.filter(status=pr_status)
        if branch:
            queryset = queryset.filter(branch_id=branch)
        return queryset

    @action(detail=True, methods=["put"], url_path="status")
    def change_status(self, request, pk=None):
        pr = self.get_object()
        serializer = PurchaseRequestStatusSerializer(data=request.data, context={"request": request, "purchase_request": pr})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PurchaseRequestSerializer(pr).data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related("supplier", "branch", "request", "purchased_by")
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["purchase_number", "supplier__company_name", "supplier_invoice_no"]
    ordering_fields = ["purchased_at", "total_amount"]

    def get_queryset(self):
        queryset = super().get_queryset()
        supplier = self.request.query_params.get("supplier")
        branch = self.request.query_params.get("branch")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        if branch:
            queryset = queryset.filter(branch_id=branch)
        if date_from:
            queryset = queryset.filter(purchased_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(purchased_at__date__lte=date_to)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CreatePurchaseOrderSerializer
        return PurchaseOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreatePurchaseOrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        po = serializer.save()
        return Response(PurchaseOrderSerializer(po).data, status=status.HTTP_201_CREATED)
