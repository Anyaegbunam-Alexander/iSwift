from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers.output import PublicUserSerializer
from core.filters import UserFilter
from core.mixins import AuthenticatedOnlyMixin
from core.views import ListAPIView
from finance.models import Currency, iSwiftAccount
from finance.serializers.input import CreateAccountSerializer, MakeTransferSerializer
from finance.serializers.output import (
    CurrencySerializer,
    DebitTransactionSerializer,
    iSwiftAccountSerializer,
)


class ListUsers(AuthenticatedOnlyMixin, ListAPIView):
    queryset = User.non_staff.all()
    serializer_class = PublicUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter


class Currencies(ListAPIView):
    queryset = Currency.objects.active().order_by("iso_code")
    serializer_class = CurrencySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "iso_code"]
    permission_classes = [AllowAny]


class MakeTransfer(AuthenticatedOnlyMixin, APIView):

    @extend_schema(request=MakeTransferSerializer, responses=DebitTransactionSerializer)
    def post(self, request: Request) -> Response:
        in_serializer = MakeTransferSerializer(data=request.data, context={"user": request.user})
        in_serializer.is_valid(raise_exception=True)
        debit = in_serializer.save()
        out_serializer = DebitTransactionSerializer(debit)
        return Response(out_serializer.data, status.HTTP_201_CREATED)


class iSwiftAccountsListCreateView(AuthenticatedOnlyMixin, ListAPIView):
    serializer_class = iSwiftAccountSerializer
    pagination_class = None
    filter_backends = []
    search_fields = None

    def get_queryset(self):
        user = self.request.user
        return iSwiftAccount.objects.filter(user=user)

    @extend_schema(request=CreateAccountSerializer, responses=iSwiftAccountSerializer)
    def post(self, request: Request) -> Response:
        in_serializer = CreateAccountSerializer(data=request.data, context={"user": request.user})
        in_serializer.is_valid(raise_exception=True)
        account = in_serializer.save()
        out_serializer = iSwiftAccountSerializer(account)
        return Response(out_serializer.data, status.HTTP_201_CREATED)
