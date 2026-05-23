from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, BranchViewSet, LogoutView, MeView, MyRolesView, RequestOTPView, RoleViewSet, TokenRefresh, VerifyOTPView

router = DefaultRouter()
router.register("branches", BranchViewSet, basename="branch")
router.register("roles", RoleViewSet, basename="role")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("auth/request-otp/", RequestOTPView.as_view(), name="request-otp"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/token/refresh/", TokenRefresh.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/me/roles/", MyRolesView.as_view(), name="me-roles"),
    path("", include(router.urls)),
]
