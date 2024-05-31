from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers.input import SignUpSerializer
from accounts.serializers.output import UserSerializer
from core.mixins import UnauthenticatedOnlyMixin
from core.permission_classes import IsUnauthenticated


class SignUpView(UnauthenticatedOnlyMixin, APIView):
    permission_classes = (IsUnauthenticated, AllowAny)
    """View to signup a new user"""

    @extend_schema(request=SignUpSerializer, responses=UserSerializer)
    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        out = UserSerializer(user)
        return Response(data=out.data, status=status.HTTP_201_CREATED)
