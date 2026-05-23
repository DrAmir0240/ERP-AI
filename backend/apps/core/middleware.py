import json

from django.forms.models import model_to_dict
from django.utils.deprecation import MiddlewareMixin

from .models import AuditLog


class AuditLogMiddleware(MiddlewareMixin):
    tracked_methods = {"POST": AuditLog.ACTION_CREATE, "PUT": AuditLog.ACTION_UPDATE, "PATCH": AuditLog.ACTION_UPDATE, "DELETE": AuditLog.ACTION_DELETE}

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.audit_before = None
        if request.method in {"PUT", "PATCH", "DELETE"}:
            instance = self._get_view_instance(view_func, view_kwargs)
            if instance is not None:
                request.audit_before = self._serialize_instance(instance)
        return None

    def process_response(self, request, response):
        if request.method not in self.tracked_methods or response.status_code >= 400:
            return response
        model_name = None
        object_id = None
        before = getattr(request, "audit_before", None)
        after = None
        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match and resolver_match.url_name:
            model_name = resolver_match.url_name.replace("-", "_")
        if response.get("content-type", "").startswith("application/json") and response.content:
            try:
                payload = json.loads(response.content.decode(response.charset or "utf-8"))
                if isinstance(payload, dict):
                    after = payload
                    object_id = str(payload.get("id") or payload.get("pk") or "")
            except (TypeError, ValueError, UnicodeDecodeError):
                after = None
        object_id = object_id or str(getattr(request, "parser_context", {}).get("kwargs", {}).get("pk", ""))
        if not model_name and not object_id:
            return response
        AuditLog.objects.create(
            user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
            action=self.tracked_methods[request.method],
            model_name=model_name or "unknown",
            object_id=object_id,
            before=before,
            after=after,
            ip_address=self._get_client_ip(request),
        )
        return response

    def _get_view_instance(self, view_func, view_kwargs):
        view_class = getattr(view_func, "view_class", None)
        if not view_class or not hasattr(view_class, "queryset"):
            return None
        pk = view_kwargs.get("pk")
        if not pk:
            return None
        queryset = view_class.queryset
        if queryset is None:
            return None
        return queryset.filter(pk=pk).first()

    def _serialize_instance(self, instance):
        data = model_to_dict(instance)
        return {key: str(value) for key, value in data.items()}

    def _get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
