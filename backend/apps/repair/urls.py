from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RepairOrderViewSet, RepairSettingsViewSet

router = DefaultRouter()
router.register("orders", RepairOrderViewSet, basename="repair-order")
router.register("settings", RepairSettingsViewSet, basename="repair-settings")

urlpatterns = [
    path("", include(router.urls)),
]
