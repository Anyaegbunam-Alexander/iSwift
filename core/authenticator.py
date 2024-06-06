from typing import Any, Dict, Union

from django.contrib.auth import authenticate
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers.input import LoginSerializer
from accounts.serializers.output import UserSerializer
from core.exceptions import Unauthorized


def authenticate_user(request: Request, inactive=False) -> User:
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(request, **serializer.validated_data, allow_inactive_user=True)

    if not inactive and user is not None and not user.is_active:
        raise Unauthorized("Please verify your phone number")

    if not user:
        raise Unauthorized("Invalid email or password")

    return user


def get_user_data(request: Request) -> Union[Dict[str, Any], Response]:
    user = request.user
    serializer = UserSerializer(user)

    content = serializer.data if user.is_authenticated else str(user)
    return content
