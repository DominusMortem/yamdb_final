from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        check_method = request.method in SAFE_METHODS
        check_admin = (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_staff
        )
        if 'users' in request.META.get('PATH_INFO'):
            return bool(check_admin)
        return bool(check_method or check_admin)

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_staff
        )


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_moderator
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_moderator
        )


class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
