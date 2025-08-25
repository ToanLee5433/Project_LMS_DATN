from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return u.is_authenticated and u.role in ("teacher", "admin")


class IsOwnerTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        """Check permission for list and create actions"""
        if request.method in SAFE_METHODS:
            return True
        # For create/update/delete, user must be teacher or admin
        u = request.user
        return u.is_authenticated and u.role in ("teacher", "admin")

    def has_object_permission(self, request, view, obj):
        """Check permission for specific object (update/delete)"""
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        if not u.is_authenticated or u.role not in ("teacher", "admin"):
            return False
        # chỉ owner hoặc admin mới chỉnh sửa course (nếu obj có owner)
        if hasattr(obj, "owner"):
            return obj.owner_id == u.id or u.role == "admin"
        return True
