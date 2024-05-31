from rest_framework import permissions

from core.exceptions import UnauthenticatedOnly


class IsUnauthenticated(permissions.BasePermission):
    """
    Allows access only to unauthenticated users.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
        else:
            raise UnauthenticatedOnly()
