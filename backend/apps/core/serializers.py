from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuditLog, Branch, Module, OTPCode, Permission, Role, UserRole
from .services.otp import send_otp

User = get_user_model()


class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def create(self, validated_data):
        otp = OTPCode.create_for_phone(validated_data["phone"])
        send_otp(otp.phone, otp.code)
        return otp


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6, min_length=4)

    def validate(self, attrs):
        otp = OTPCode.objects.filter(phone=attrs["phone"]).order_by("-created_at").first()
        if not otp or not otp.verify(attrs["code"]):
            raise serializers.ValidationError({"code": "Invalid or expired OTP code."})
        attrs["otp"] = otp
        return attrs

    def create(self, validated_data):
        user, _created = User.objects.get_or_create(phone=validated_data["phone"])
        refresh = RefreshToken.for_user(user)
        return {"user": user, "refresh": str(refresh), "access": str(refresh.access_token)}


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            self.context["token"] = RefreshToken(value)
        except Exception as exc:
            raise serializers.ValidationError("Invalid refresh token.") from exc
        return value

    def save(self, **kwargs):
        self.context["token"].blacklist()


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ("id", "name", "address", "phone", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("id", "name", "display_name")
        read_only_fields = ("id",)


class PermissionSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    module_id = serializers.PrimaryKeyRelatedField(source="module", queryset=Module.objects.all(), write_only=True)

    class Meta:
        model = Permission
        fields = ("id", "module", "module_id", "can_read", "can_write")
        read_only_fields = ("id",)


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ("id", "name", "display_name", "is_default", "created_at", "permissions")
        read_only_fields = ("id", "created_at")


class RolePermissionUpdateSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.DictField(), allow_empty=True)

    def validate_permissions(self, value):
        module_ids = set()
        normalized = []
        for item in value:
            module_id = item.get("module_id")
            if not module_id:
                raise serializers.ValidationError("module_id is required for every permission.")
            if module_id in module_ids:
                raise serializers.ValidationError("Duplicate module_id in permissions.")
            module = Module.objects.filter(id=module_id).first()
            if not module:
                raise serializers.ValidationError(f"Module {module_id} does not exist.")
            module_ids.add(module_id)
            normalized.append(
                {
                    "module": module,
                    "can_read": bool(item.get("can_read", False)),
                    "can_write": bool(item.get("can_write", False)),
                }
            )
        return normalized

    def save(self, **kwargs):
        role = self.context["role"]
        seen = []
        for item in self.validated_data["permissions"]:
            permission, _created = Permission.objects.update_or_create(
                role=role,
                module=item["module"],
                defaults={"can_read": item["can_read"], "can_write": item["can_write"]},
            )
            seen.append(permission.id)
        role.permissions.exclude(id__in=seen).delete()
        return role


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = UserRole
        fields = ("id", "role", "branch", "assigned_at")
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "phone", "full_name", "is_active", "is_admin", "created_at", "updated_at", "roles")
        read_only_fields = ("id", "phone", "is_active", "is_admin", "created_at", "updated_at", "roles")

    def get_roles(self, obj):
        return UserRoleSerializer(obj.user_roles.select_related("role", "branch"), many=True).data


class AuditLogSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = AuditLog
        fields = ("id", "user", "user_phone", "action", "model_name", "object_id", "before", "after", "ip_address", "created_at")
        read_only_fields = fields
