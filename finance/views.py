from uuid import UUID

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers.output import PublicUserSerializer
from core.exceptions import BadRequest
from core.filters import UserFilter
from core.helpers import get_object_or_404
from core.mixins import AuthenticatedOnlyMixin
from core.schema import uid_parameter
from core.views import ListAPIView
from finance.models import CreditTransaction, Currency, DebitTransaction, iSwiftAccount
from finance.serializers.input import (
    CreateAccountSerializer,
    MakeTransferSerializer,
    iSwiftAccountUpdateSerializer,
)
from finance.serializers.output import (
    CurrencySerializer,
    DebitTransactionSerializer,
    PrivateCreditTransactionSerializer,
    iSwiftAccountDetailSerializer,
    iSwiftAccountSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            description="Search by either first name, last name, or phone number",
            location=OpenApiParameter.QUERY,
        ),
    ]
)
class UsersListView(AuthenticatedOnlyMixin, ListAPIView):
    queryset = User.non_staff.all()
    serializer_class = PublicUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter


class CurrenciesListView(ListAPIView):
    queryset = Currency.objects.active().order_by("iso_code")
    serializer_class = CurrencySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "iso_code"]
    permission_classes = [AllowAny]
    pagination_class = None


class MakeTransferView(AuthenticatedOnlyMixin, APIView):

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

    @extend_schema(
        request=CreateAccountSerializer,
        responses=iSwiftAccountSerializer,
    )
    def post(self, request: Request) -> Response:
        in_serializer = CreateAccountSerializer(data=request.data, context={"user": request.user})
        in_serializer.is_valid(raise_exception=True)
        account = in_serializer.save()
        out_serializer = iSwiftAccountSerializer(account)
        return Response(out_serializer.data, status.HTTP_201_CREATED)


class iSwiftAccountDetailView(AuthenticatedOnlyMixin, APIView):
    serializer_class = iSwiftAccountDetailSerializer

    @extend_schema(
        responses=serializer_class,
        parameters=[uid_parameter("iSwift account")],
    )
    def get(self, request: Request, uid: UUID) -> Response:
        account = get_object_or_404(iSwiftAccount, uid=uid, user=request.user)
        serializer = self.serializer_class(account)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        request=iSwiftAccountUpdateSerializer,
        operation_id="finance_iswift_accounts_update",
    )
    def post(self, request: Request, uid: UUID) -> Response:
        account = get_object_or_404(iSwiftAccount, uid=uid, user=request.user)
        in_serializer = iSwiftAccountUpdateSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        account = in_serializer.update(account, in_serializer.validated_data)
        out_serializer = iSwiftAccountSerializer(account)
        return Response(out_serializer.data, status.HTTP_200_OK)


class TransactionDetail(AuthenticatedOnlyMixin, APIView):
    types = ["credit-transaction", "debit-transaction"]

    @extend_schema(
        responses={
            "credit-transaction": PrivateCreditTransactionSerializer,
            "debit-transaction": DebitTransactionSerializer,
        },
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                description=f"to get either of {types}",
                enum=types,
                location=OpenApiParameter.PATH,
            ),
            uid_parameter("Transaction"),
        ],
    )
    def get(self, request: Request, uid: UUID, type: str) -> Response:
        """This endpoint returns details of
        a credit or debit transaction based on the type provided."""
        if type not in self.types:
            raise BadRequest(f"type not part of {self.types}")

        if type == self.types[0]:
            Klass = CreditTransaction
            SerializerKlass = PrivateCreditTransactionSerializer
        else:
            Klass = DebitTransaction
            SerializerKlass = DebitTransactionSerializer

        transaction = get_object_or_404(Klass, uid=uid, iswift_account__user=request.user)
        serializer = SerializerKlass(transaction)
        return Response(serializer.data, status.HTTP_200_OK)
