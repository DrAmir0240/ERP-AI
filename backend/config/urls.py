from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "drgame-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", health_check, name="health-check"),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/inventory/", include("apps.inventory.urls")),
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/repair/", include("apps.repair.urls")),
    path("api/v1/procurement/", include("apps.procurement.urls")),
]
