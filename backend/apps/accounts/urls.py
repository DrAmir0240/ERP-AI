from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccountSaleViewSet, CalculatePriceView, GameAccountViewSet, GameViewSet

router = DefaultRouter()
router.register("games", GameViewSet, basename="accounts-game")
router.register("ps", GameAccountViewSet, basename="accounts-gameaccount")
router.register("sales", AccountSaleViewSet, basename="accounts-sale")
router.register("calculate-price", CalculatePriceView, basename="accounts-calculate-price")

urlpatterns = [
    path("", include(router.urls)),
]
