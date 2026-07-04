from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PurchaseOrderViewSet, PurchaseRequestViewSet, SupplierViewSet

router = DefaultRouter()
router.register("suppliers", SupplierViewSet, basename="procurement-supplier")
router.register("requests", PurchaseRequestViewSet, basename="procurement-request")
router.register("orders", PurchaseOrderViewSet, basename="procurement-order")

urlpatterns = [
    path("", include(router.urls)),
]
