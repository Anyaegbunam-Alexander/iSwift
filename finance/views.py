from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from accounts.serializers.output import PublicUserSerializer
from core.filters import UserFilter
from core.mixins import AuthenticatedOnlyMixin
from core.views import ListAPIView


class ListUsers(AuthenticatedOnlyMixin, ListAPIView):
    queryset = User.non_staff.all()
    serializer_class = PublicUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter


# class MakeTransfer(AuthenticatedOnlyMixin)
