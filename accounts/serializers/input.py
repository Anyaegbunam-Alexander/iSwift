import random
from datetime import timedelta

from django.conf import settings
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import ValidationError

from accounts.models import OTP, User
from core.otp import send_otp
from core.validators import country_code_regex, otp_regex, phone_regex


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=80, validators=[validate_email])
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    country_code = serializers.IntegerField(validators=[country_code_regex])
    phone_number = serializers.IntegerField(validators=[phone_regex])

    def validate(self, attrs):
        email_exists = User.objects.filter(email=attrs["email"]).exists()
        if email_exists:
            raise ValidationError({"email": "Email already exists!"})

        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError(
                {
                    "password": "Passwords do not match",
                    "confirm_password": "Passwords do not match",
                }
            )
        phone_number_exists = User.objects.filter(phone_number=attrs["phone_number"]).exists()
        if phone_number_exists:
            raise ValidationError({"phone_number": "Phone Number already exists!"})

        return super().validate(attrs)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "phone_number",
            "country_code",
        ]

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        otp = random.randint(100000, 999999)
        otp_expiry = timezone.now() + timedelta(minutes=10)
        user = super().create(validated_data)
        user.set_password(password)
        user_otp = OTP.objects.create(user=user)
        user_otp.otp = otp
        user_otp.otp_expiry = otp_expiry
        user_otp.max_otp_try = settings.MAX_OTP_TRY
        user_otp.save()
        send_otp(phone_number=validated_data["phone_number"], otp=otp)
        user.save()
        return user


class PhoneNumberInputSerializer(serializers.Serializer):
    """Serializer for phone_number input"""

    phone_number = serializers.CharField(max_length=11, validators=[phone_regex])


class OTPInputSerializer(PhoneNumberInputSerializer):
    """Serializer for otp input"""

    otp = serializers.CharField(validators=[otp_regex])


class ConfirmTokenSerializer(serializers.Serializer):
    uid = serializers.UUIDField()
    token = serializers.CharField()

    class Meta:
        fields = ["token", "uid"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=80)
    password = serializers.CharField(
        min_length=8, write_only=True, style={"input_type": "password"}
    )


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError(
                {
                    "password": "Passwords do not match",
                    "confirm_password": "Passwords do not match",
                }
            )
        return attrs


class AuthPasswordResetSerializer(serializers.Serializer):
    current_password = serializers.CharField(min_length=8, write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise ValidationError(
                {
                    "new_password": "Passwords do not match",
                    "confirm_new_password": "Passwords do not match",
                }
            )
        return attrs
