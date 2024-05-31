import pytest

pytestmark = pytest.mark.django_db


class TestUserModel:
    @pytest.mark.accounts_models
    def test_str_method(self, user_factory):
        user = user_factory()
        assert user.__str__() == str(user)


class TestOTPModel:
    @pytest.mark.accounts_models
    def test_str_method(self, otp_factory):
        otp = otp_factory()
        assert otp.__str__() == str(otp)
