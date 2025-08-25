from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTeacherOrAdmin(BasePermission):
    """
    Permission để chỉ teacher hoặc admin mới được thực hiện write operations.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.role in ("teacher", "admin")
        )


class IsQuizOwnerOrAdmin(BasePermission):
    """
    Permission để chỉ chủ sở hữu quiz hoặc admin mới được thực hiện write operations.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user.is_authenticated or user.role not in ("teacher", "admin"):
            return False

        # Lấy owner_id từ obj hoặc obj.quiz
        owner_id = getattr(obj, "owner_id", None) or getattr(
            obj.quiz, "owner_id", None
        )
        return owner_id == user.id or user.role == "admin"

    def has_permission(self, request, view):
        """
        Permission cho list/create actions
        """
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.role in ("teacher", "admin")
        )
