from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, RefundViewSet, ReturnPolicyViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders-order")
router.register("refunds", RefundViewSet, basename="orders-refund")
router.register("return-policies", ReturnPolicyViewSet, basename="orders-returnpolicy")

urlpatterns = [
    path("", include(router.urls)),
]
