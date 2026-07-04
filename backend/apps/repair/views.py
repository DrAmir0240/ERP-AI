from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdmin, IsEmployee

from .models import RepairOrder, RepairSettings
from .serializers import (
    CustomerDecisionSerializer,
    RepairAcceptSerializer,
    RepairCompleteSerializer,
    RepairOrderSerializer,
    RepairPriceSerializer,
    RepairSettingsSerializer,
    RepairStatusSerializer,
)


class RepairOrderViewSet(viewsets.ModelViewSet):
    queryset = RepairOrder.objects.select_related("order", "technician")
    serializer_class = RepairOrderSerializer
    permission_classes = [IsEmployee]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["order__order_number", "device_model", "issue_description", "technician__phone"]
    ordering_fields = ["created_at", "status", "final_price"]

    def get_queryset(self):
        queryset = super().get_queryset()
        repair_status = self.request.query_params.get("status")
        technician = self.request.query_params.get("technician")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if repair_status:
            queryset = queryset.filter(status=repair_status)
        if technician:
            queryset = queryset.filter(technician_id=technician)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset

    @action(detail=True, methods=["put"], url_path="accept")
    def accept(self, request, pk=None):
        repair = self.get_object()
        serializer = RepairAcceptSerializer(data=request.data, context={"request": request, "repair": repair})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RepairOrderSerializer(repair).data)

    @action(detail=True, methods=["put"], url_path="price")
    def set_price(self, request, pk=None):
        repair = self.get_object()
        serializer = RepairPriceSerializer(data=request.data, context={"request": request, "repair": repair})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RepairOrderSerializer(repair).data)

    @action(detail=True, methods=["put"], url_path="customer-decision")
    def customer_decision(self, request, pk=None):
        repair = self.get_object()
        serializer = CustomerDecisionSerializer(data=request.data, context={"request": request, "repair": repair})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RepairOrderSerializer(repair).data)

    @action(detail=True, methods=["put"], url_path="complete")
    def complete(self, request, pk=None):
        repair = self.get_object()
        serializer = RepairCompleteSerializer(data=request.data, context={"request": request, "repair": repair})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RepairOrderSerializer(repair).data)

    @action(detail=True, methods=["put"], url_path="status")
    def change_status(self, request, pk=None):
        repair = self.get_object()
        serializer = RepairStatusSerializer(data=request.data, context={"request": request, "repair": repair})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RepairOrderSerializer(repair).data)


class RepairSettingsViewSet(viewsets.ModelViewSet):
    queryset = RepairSettings.objects.all()
    serializer_class = RepairSettingsSerializer
    permission_classes = [IsAdmin]

    def list(self, request, *args, **kwargs):
        obj = RepairSettings.objects.first()
        if not obj:
            obj = RepairSettings.objects.create()
        return Response(RepairSettingsSerializer(obj).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(RepairSettingsSerializer(obj).data, status=status.HTTP_200_OK)
