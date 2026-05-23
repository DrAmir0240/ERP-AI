from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .models import AuditLog, Branch, Role
from .serializers import (
    AuditLogSerializer,
    BranchSerializer,
    LogoutSerializer,
    RequestOTPSerializer,
    RolePermissionUpdateSerializer,
    RoleSerializer,
    UserRoleSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_admin))


class RequestOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "OTP sent if the phone number is valid."}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response({"access": data["access"], "refresh": data["refresh"], "user": UserSerializer(data["user"]).data})


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MyRolesView(APIView):
    def get(self, request):
        roles = request.user.user_roles.select_related("role", "branch")
        return Response(UserRoleSerializer(roles, many=True).data)


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "phone", "address"]
    ordering_fields = ["name", "created_at"]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related("permissions__module")
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "display_name"]
    ordering_fields = ["name", "created_at"]

    @action(detail=True, methods=["get", "put"], url_path="permissions")
    def permissions(self, request, pk=None):
        role = self.get_object()
        if request.method == "GET":
            return Response(RoleSerializer(role).data["permissions"])
        self.check_permissions(request)
        serializer = RolePermissionUpdateSerializer(data=request.data, context={"role": role})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RoleSerializer(role).data["permissions"])


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["model_name", "object_id", "user__phone"]
    ordering_fields = ["created_at", "model_name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        model_name = self.request.query_params.get("model")
        user = self.request.query_params.get("user")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        if user:
            queryset = queryset.filter(user_id=user)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset


TokenRefresh = TokenRefreshView
