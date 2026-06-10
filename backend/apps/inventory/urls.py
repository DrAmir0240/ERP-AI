from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BranchTransferViewSet, CategoryViewSet, ProductViewSet, StockItemViewSet, StockMovementViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="inventory-category")
router.register("products", ProductViewSet, basename="inventory-product")
router.register("stock", StockItemViewSet, basename="inventory-stock")
router.register("movements", StockMovementViewSet, basename="inventory-movement")
router.register("transfers", BranchTransferViewSet, basename="inventory-transfer")

urlpatterns = [
    path("", include(router.urls)),
]
