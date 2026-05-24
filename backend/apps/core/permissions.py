from rest_framework import permissions


EMPLOYEE_ROLE_NAMES = {
    "admin",
    "cashier",
    "account_setter",
    "accountant",
    "warehouse",
    "repair_technician",
}


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_admin))


class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_admin:
            return True
        return request.user.user_roles.filter(role__name__in=EMPLOYEE_ROLE_NAMES).exists()


class IsBranchMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_admin:
            return True
        branch_id = view.kwargs.get("branch_pk") or view.kwargs.get("branch_id") or request.query_params.get("branch")
        if not branch_id:
            return request.user.user_roles.filter(branch__isnull=False).exists()
        return request.user.user_roles.filter(branch_id=branch_id).exists()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return IsAdmin().has_permission(request, view)
