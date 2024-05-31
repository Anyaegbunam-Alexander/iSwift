import secrets
from copy import deepcopy
from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APIClient

from core.tokens import password_reset_token
from tests.data import login_data, user_data

pytestmark = pytest.mark.django_db


class TestSignup:
    @pytest.mark.auth
    def test_signup(self, anon_user_api_client: APIClient):
        endpoint = reverse("accounts:signup")
        response: Response = anon_user_api_client.post(endpoint, data=user_data)
        assert response.status_code == 201


class TestLoginEndpoint:
    data = login_data

    @pytest.mark.auth
    def test_login(self, anon_user_api_client: APIClient, user_factory):
        user = user_factory()
        data = self.data.copy()
        data["email"] = user.email
        response: Response = anon_user_api_client.post(reverse("accounts:login"), data=data)
        assert response.status_code == 200

    def test_login_failed_inactive_user(self, anon_user_api_client: APIClient, user_factory):
        user = user_factory()
        user.is_active = False
        user.save()
        data = self.data.copy()
        data["email"] = user.email
        response: Response = anon_user_api_client.post(reverse("accounts:login"), data=data)
        assert response.status_code == 401
        assert response.content == b'{"message":"Please verify your phone number","extra":{}}'

    @pytest.mark.auth
    def test_login_failed_invalid_email(self, anon_user_api_client: APIClient, user_factory):
        data = self.data.copy()
        data["email"] = "invalid@test.com"
        response: Response = anon_user_api_client.post(reverse("accounts:login"), data=data)
        assert response.status_code == 401

    @pytest.mark.auth
    def test_login_failed_invalid_password(self, anon_user_api_client: APIClient, user_factory):
        user = user_factory()
        data = self.data.copy()
        data["email"] = user.email
        data["password"] = "invalid_password"
        response: Response = anon_user_api_client.post(reverse("accounts:login"), data=data)
        assert response.status_code == 401

    class TestVerifyOTPEndpoint:
        otp = {"otp": 123456}

        @pytest.mark.auth
        def test_verify_otp_success(
            self,
            anon_user_api_client: APIClient,
            otp_factory,
            user_factory,
        ):
            user = user_factory()
            phone_number = user.phone_number
            otp_factory(user=user)
            user.is_active = False
            user.save()
            data = self.otp.copy()
            data["phone_number"] = phone_number
            response: Response = anon_user_api_client.post(
                reverse("accounts:verify_otp"),
                data=data,
            )
            assert response.status_code == 200

        @pytest.mark.auth
        def test_verify_otp_fail_expired_otp(
            self,
            anon_user_api_client: APIClient,
            otp_factory,
            user_factory,
        ):
            user = user_factory()
            phone_number = user.phone_number
            otp = otp_factory(user=user)
            expiry = settings.OTP_EXPIRY_MINUTES
            otp.otp_expiry = timezone.now() - timedelta(minutes=expiry + 1)
            otp.save()
            user.is_active = False
            user.save()
            data = self.otp.copy()
            data["phone_number"] = phone_number
            response: Response = anon_user_api_client.post(
                reverse("accounts:verify_otp"),
                data=data,
            )
            assert response.status_code == 400

        @pytest.mark.auth
        def test_verify_otp_fail_active_user(
            self, anon_user_api_client: APIClient, otp_factory, user_factory
        ):
            user = user_factory()
            phone_number = user.phone_number
            otp_factory(user=user)
            data = self.otp.copy()
            data["phone_number"] = phone_number
            response: Response = anon_user_api_client.post(
                reverse("accounts:verify_otp"),
                data=data,
            )
            assert response.status_code == 400

        @pytest.mark.auth
        def test_verify_otp_fail_wrong_otp(
            self, anon_user_api_client: APIClient, otp_factory, user_factory
        ):
            user = user_factory()
            phone_number = user.phone_number
            otp_factory(user=user)
            data = self.otp.copy()
            data["phone_number"] = phone_number
            data["otp"] = 432177
            response: Response = anon_user_api_client.post(
                reverse("accounts:verify_otp"),
                data=data,
            )
            assert response.status_code == 400

        @pytest.mark.auth
        def test_verify_otp_fail_no_phone_number(
            self,
            anon_user_api_client: APIClient,
        ):
            response: Response = anon_user_api_client.post(
                reverse("accounts:verify_otp"),
                data=self.otp,
            )
            assert response.status_code == 400


class TestRegrateOTPEndpoint:
    @pytest.mark.auth
    def test_regenerate_otp_success(
        self,
        anon_user_api_client: APIClient,
        otp_factory,
        user_factory,
    ):
        user = user_factory()
        user.is_active = False
        user.save()
        otp_factory(user=user)
        phone_number = user.phone_number
        response: Response = anon_user_api_client.post(
            reverse("accounts:regenerate_otp"), data={"phone_number": phone_number}
        )
        assert response.status_code == 200

    @pytest.mark.auth
    def test_regenerate_otp_fail_active_user(
        self,
        anon_user_api_client: APIClient,
        user_factory,
        otp_factory,
    ):
        user = user_factory()
        otp_factory(user=user)
        phone_number = user.phone_number
        response: Response = anon_user_api_client.post(
            reverse("accounts:regenerate_otp"), data={"phone_number": phone_number}
        )
        assert response.status_code == 403

    @pytest.mark.auth
    def test_regenerate_otp_fail_max_try_reached(
        self,
        anon_user_api_client: APIClient,
        otp_factory,
        user_factory,
    ):
        user = user_factory()
        user.is_active = False
        user.save()
        otp_factory(user=user, max_otp_try=0, otp_max_out=timezone.now() + timedelta(minutes=20))
        phone_number = user.phone_number
        response: Response = anon_user_api_client.post(
            reverse("accounts:regenerate_otp"), data={"phone_number": phone_number}
        )
        assert response.status_code == 400


class TestGenerateOTPPasswordReset:
    @pytest.mark.auth
    def test_otp_generation_success(
        self,
        anon_user_api_client: APIClient,
        otp_factory,
        user_factory,
    ):
        user = user_factory()
        otp_factory(user=user)
        phone_number = user.phone_number
        response: Response = anon_user_api_client.post(
            reverse("accounts:password_reset_get_otp"), data={"phone_number": phone_number}
        )
        assert response.status_code == 200

    @pytest.mark.auth
    def test_otp_generation_fail_no_phone_number(
        self,
        anon_user_api_client: APIClient,
        otp_factory,
        user_factory,
    ):
        user = user_factory()
        otp_factory(user=user)
        response: Response = anon_user_api_client.post(reverse("accounts:password_reset_get_otp"))
        assert response.status_code == 400


class TestOTPVerification:
    otp = {"otp": 123456}

    @pytest.mark.auth
    def test_verification_success(
        self,
        anon_user_api_client: APIClient,
        otp_factory,
        user_factory,
    ):
        user = user_factory()
        phone_number = user.phone_number
        otp_factory(user=user)
        user.is_active = False
        user.save()
        data = self.otp.copy()
        data["phone_number"] = phone_number
        response: Response = anon_user_api_client.post(
            reverse("accounts:password_reset_verify_otp"),
            data=data,
        )
        assert response.status_code == 200


class TestTokenVerification:
    @pytest.mark.auth
    def test_verification_success(
        self,
        anon_user_api_client: APIClient,
        user_factory,
    ):
        user = user_factory()
        token = password_reset_token.make_token(user)
        data = {
            "uid": user.uid,
            "token": token,
            "password": "password",
            "confirm_password": "password",
        }
        response: Response = anon_user_api_client.post(
            reverse("accounts:reset_password_from_otp"), data=data
        )
        assert response.status_code == 200

    @pytest.mark.auth
    def test_verification_fail_no_password(
        self,
        anon_user_api_client: APIClient,
        user_factory,
    ):
        user = user_factory()
        token = password_reset_token.make_token(user)
        data = {
            "uid": user.uid,
            "token": token,
        }
        response: Response = anon_user_api_client.post(
            reverse("accounts:reset_password_from_otp"), data=data
        )
        assert response.status_code == 400

    @pytest.mark.auth
    def test_verification_fail_wrong_user_token(
        self,
        anon_user_api_client: APIClient,
        user_factory,
    ):
        user = user_factory()
        wrong_user = user_factory()
        token = password_reset_token.make_token(user)
        data = {
            "uid": wrong_user.uid,
            "token": token,
            "password": "password",
            "confirm_password": "password",
        }
        response: Response = anon_user_api_client.post(
            reverse("accounts:reset_password_from_otp"), data=data
        )
        assert response.status_code == 400

    @pytest.mark.auth
    def test_verification_fail_invalid_token(
        self,
        anon_user_api_client: APIClient,
        user_factory,
    ):
        user = user_factory()
        token = secrets.token_urlsafe(40)
        data = {
            "uid": user.uid,
            "token": token,
            "password": "password",
            "confirm_password": "password",
        }
        response: Response = anon_user_api_client.post(
            reverse("accounts:reset_password_from_otp"), data=data
        )
        assert response.status_code == 400


class TestPasswordReset:
    data = {
        "current_password": "password",
        "new_password": "new_password",
        "confirm_new_password": "new_password",
    }

    @pytest.mark.auth
    def test_auth_user_password_reset_successful(self, auth_user_api_client):
        response: Response = auth_user_api_client.post(
            reverse("accounts:password_reset"), data=self.data
        )
        assert response.status_code == 200

    @pytest.mark.auth
    def test_auth_user_password_reset_fail_wrong_password(self, auth_user_api_client):
        data = deepcopy(self.data)
        data["current_password"] = "wrong_password"
        response: Response = auth_user_api_client.post(
            reverse("accounts:password_reset"), data=data
        )
        assert response.status_code == 400

    @pytest.mark.auth
    def test_auth_user_password_reset_fail_passwords_do_not_match(self, auth_user_api_client):
        data = deepcopy(self.data)
        data["confirm_new_password"] = "wrong_password"
        response: Response = auth_user_api_client.post(
            reverse("accounts:password_reset"), data=data
        )
        assert response.status_code == 400
