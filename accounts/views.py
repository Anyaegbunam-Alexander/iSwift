from django.contrib.auth import authenticate, login, logout
from drf_spectacular.utils import extend_schema
from knox.models import AuthToken
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.schema import VerifyOTPPasswordResetSchema
from accounts.serializers.input import (
    AuthPasswordResetSerializer,
    ConfirmTokenSerializer,
    LoginSerializer,
    OTPInputSerializer,
    PasswordResetSerializer,
    PhoneNumberInputSerializer,
    SignUpSerializer,
)
from accounts.serializers.output import UserLoginSerializer, UserSerializer
from core.authenticator import authenticate_user
from core.exceptions import BadRequestException
from core.helpers import get_object_or_404, response_dict
from core.mixins import AuthenticatedOnlyMixin, UnauthenticatedOnlyMixin
from core.otp import OTPGenerator, OTPVerifier
from core.permission_classes import IsUnauthenticated
from core.schema import ResponseDictSchema
from core.tokens import password_reset_token


class LoginView(UnauthenticatedOnlyMixin, APIView):
    """Login view"""

    serializer_class = UserSerializer

    @extend_schema(request=LoginSerializer, responses=UserLoginSerializer)
    def post(self, request: Request) -> Response:
        user = authenticate_user(request)
        AuthToken.objects.filter(user=user).delete()
        login(request, user)
        serializer = self.serializer_class(user)
        response_data = serializer.data
        token = AuthToken.objects.create(user)
        response_data["authentication"] = {
            "object": "token",
            "expiry": token[0].expiry,
            "token": token[1],
        }
        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )

    def get(self, request: Request) -> Response:
        """Get the details of the logged in user.
        This method requires authentication
        """
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status.HTTP_200_OK)


class LogoutView(APIView):
    """Logout any user"""

    @extend_schema(request=None, responses=None)
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(data=response_dict("Logged out successfully"), status=status.HTTP_200_OK)


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


class VerifyOTPView(UnauthenticatedOnlyMixin, APIView):
    """View for a user to verify an OTP during registration"""

    input_serializer_class = OTPInputSerializer

    @extend_schema(
        request=input_serializer_class,
        responses=ResponseDictSchema,
    )
    def post(self, request: Request) -> Response:
        serializer = self.input_serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            verify = OTPVerifier(data=serializer.validated_data, activate_user=True)
            if verify.verify_otp():
                return Response(
                    response_dict("Successfully verified phone number"),
                    status=status.HTTP_200_OK,
                )
            raise BadRequestException("Unable to verify otp please try again")


class RegenerateOTPViewSignup(UnauthenticatedOnlyMixin, APIView):

    input_serializer_class = PhoneNumberInputSerializer

    @extend_schema(
        request=input_serializer_class,
        responses=ResponseDictSchema,
    )
    def post(self, request: Request) -> Response:
        serializer = self.input_serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            otp_generator = OTPGenerator(data=serializer.validated_data, activate_user=True)
            response = otp_generator.generate_otp()
            return Response(**response)


class GenerateOTPForPasswordReset(UnauthenticatedOnlyMixin, APIView):
    """View to generate and
    receive an otp for password reset"""

    input_serializer_class = PhoneNumberInputSerializer

    @extend_schema(
        request=input_serializer_class,
        responses=ResponseDictSchema,
    )
    def post(self, request: Request) -> Response:
        data = request.data
        input_serializer = self.input_serializer_class(data=data)
        if input_serializer.is_valid(raise_exception=True):
            otp_generator = OTPGenerator(data=input_serializer.validated_data, activate_user=False)
            response = otp_generator.generate_otp()
            return Response(**response)


class VerifyOTPPasswordReset(UnauthenticatedOnlyMixin, APIView):
    """View to verify the otp from password reset"""

    input_serializer_class = OTPInputSerializer

    @extend_schema(
        request=input_serializer_class,
        responses=VerifyOTPPasswordResetSchema,
    )
    def post(self, request: Request) -> Response:
        data = request.data
        serializer = self.input_serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            verify = OTPVerifier(data=serializer.data, activate_user=False)
            user = verify.verify_otp()
            if user:
                token = password_reset_token.make_token(user)
                data = {"uid": user.uid, "token": token}
                return Response(data, status=status.HTTP_200_OK)
            raise BadRequestException("Unable to verify otp please try again")


class ResetPasswordFromOTP(UnauthenticatedOnlyMixin, APIView):
    """Reset password for a user with a valid token"""

    @extend_schema(request=ConfirmTokenSerializer, responses=ResponseDictSchema)
    def post(self, request: Request) -> Response:
        data = request.data
        confirm_token_serializer = ConfirmTokenSerializer(data=data)
        confirm_token_serializer.is_valid(raise_exception=True)
        token = confirm_token_serializer.validated_data["token"]
        uid = confirm_token_serializer.validated_data["uid"]
        user = get_object_or_404(User, uid=uid)

        if not password_reset_token.check_token(user, token):
            raise BadRequestException("Invalid or expired token")

        password_reset_serializer = PasswordResetSerializer(data=data)
        if password_reset_serializer.is_valid(raise_exception=True):
            password = password_reset_serializer.validated_data["password"]
            user.set_password(password)
            user.save()
            return Response(response_dict("Password reset successful"), status.HTTP_200_OK)


class AuthUserResetPasswordView(AuthenticatedOnlyMixin, APIView):
    """Reset password for an authenticated user"""

    @extend_schema(request=AuthPasswordResetSerializer, responses=ResponseDictSchema)
    def post(self, request: Request) -> Response:
        serializer = AuthPasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            current_password = serializer.validated_data["current_password"]
            user = authenticate(request, password=current_password, email=request.user.email)
            if user is None:
                raise BadRequestException("Invalid current password")

            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            login(request, user)
            return Response(response_dict("Password reset successful"), status.HTTP_200_OK)
