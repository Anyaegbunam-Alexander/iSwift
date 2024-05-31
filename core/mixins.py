from rest_framework.permissions import IsAuthenticated

from core import permission_classes


class UnauthenticatedOnlyMixin:
    permission_classes = [permission_classes.IsUnauthenticated]


class AuthenticatedOnlyMixin:
    permission_classes = [IsAuthenticated]
