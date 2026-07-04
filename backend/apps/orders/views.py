from django.db.models import Count
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdmin, IsAdminOrReadOnly, IsEmployee

from .models import Invoice, Order, Payment, Refund, ReturnPolicy
from .serializers import (
    CancelOrderSerializer,
    CreateOrderSerializer,
    InvoiceSerializer,
    OrderCourierSerializer,
    OrderListSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    PaymentSerializer,
    RefundActionSerializer,
    RefundSerializer,
    ReturnPolicySerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("branch", "customer", "cashier")
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["order_number", "customer__phone", "customer__full_name", "notes"]
    ordering_fields = ["created_at", "total", "status"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "create":
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.annotate(item_count=Count("items"))
        order_type = self.request.query_params.get("type")
        order_status = self.request.query_params.get("status")
        channel = self.request.query_params.get("channel")
        branch = self.request.query_params.get("branch")
        customer = self.request.query_params.get("customer")
        payment_status = self.request.query_params.get("payment_status")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        if order_status:
            queryset = queryset.filter(status=order_status)
        if channel:
            queryset = queryset.filter(channel=channel)
        if branch:
            queryset = queryset.filter(branch_id=branch)
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"], url_path="status")
    def change_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(data=request.data, context={"request": request, "order": order})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["put"], url_path="courier")
    def courier(self, request, pk=None):
        order = self.get_object()
        serializer = OrderCourierSerializer(data=request.data, context={"request": request, "order": order})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        order = self.get_object()
        serializer = CancelOrderSerializer(data=request.data, context={"request": request, "order": order})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["get"], url_path="invoice")
    def invoice(self, request, pk=None):
        order = self.get_object()
        inv, created = Invoice.objects.get_or_create(
            order=order,
            defaults={
                "tax_rate": order.tax_amount,
                "tax_amount": order.tax_amount,
                "total": order.total,
            },
        )
        return Response(InvoiceSerializer(inv).data)

    @action(detail=True, methods=["get", "post"], url_path="payments")
    def payments(self, request, pk=None):
        order = self.get_object()
        if request.method == "GET":
            payments = order.payments.all()
            return Response(PaymentSerializer(payments, many=True).data)
        serializer = PaymentSerializer(data={**request.data, "order": order.id}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="refund")
    def refund(self, request, pk=None):
        order = self.get_object()
        serializer = RefundSerializer(data={**request.data, "order": order.id}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RefundViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Refund.objects.select_related("order", "requested_by", "approved_by")
    serializer_class = RefundSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["order__order_number", "requested_by__phone", "reason"]
    ordering_fields = ["created_at", "amount", "status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        refund_status = self.request.query_params.get("status")
        if refund_status:
            queryset = queryset.filter(status=refund_status)
        return queryset

    @action(detail=True, methods=["put"], url_path="approve")
    def approve(self, request, pk=None):
        refund = self.get_object()
        serializer = RefundActionSerializer(data=request.data, context={"request": request, "refund": refund})
        serializer.is_valid(raise_exception=True)
        serializer.approve()
        return Response(RefundSerializer(refund).data)

    @action(detail=True, methods=["put"], url_path="reject")
    def reject(self, request, pk=None):
        refund = self.get_object()
        serializer = RefundActionSerializer(data=request.data, context={"request": request, "refund": refund})
        serializer.is_valid(raise_exception=True)
        serializer.reject()
        return Response(RefundSerializer(refund).data)


class ReturnPolicyViewSet(viewsets.ModelViewSet):
    queryset = ReturnPolicy.objects.select_related("category")
    serializer_class = ReturnPolicySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["category__name"]
