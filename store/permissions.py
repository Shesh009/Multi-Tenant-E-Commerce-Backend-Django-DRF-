from rest_framework import permissions
from store.models import Product, Order

class IsTenantMatch(permissions.BasePermission):
    def has_permission(self, request, view):
        token = getattr(request, "auth", None)
        tenant = getattr(request, "tenant", None)
        if token is None:
            return False
        token_tenant_id = token.payload.get("tenant_id")
        if tenant is None:
            return True
        return str(token_tenant_id) == str(tenant.id)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            getattr(request.user, "role", None) == "owner" and
            getattr(request.user, "vendor_id", None) == getattr(request.tenant, "id", None)
        )


class IsStaffOrOwnerForWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(user, "role", None)
        method = request.method

        if role == "owner":
            return obj.vendor_id == user.vendor_id

        if role == "staff":
            if isinstance(obj, Product):
                if method in permissions.SAFE_METHODS:
                    return obj.vendor_id == user.vendor_id
                return obj.assigned_to_id == user.id
            if isinstance(obj, Order):
                if method in permissions.SAFE_METHODS:
                    return obj.vendor_id == user.vendor_id
                return obj.assigned_to_id == user.id
            return False

        if role == "customer":
            if method in permissions.SAFE_METHODS:
                return getattr(obj, "customer_id", None) == user.id
            if method == "POST":
                return True
            return False

        return False
