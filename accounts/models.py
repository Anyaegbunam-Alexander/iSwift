import random

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.model_abstracts import Model


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff being True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser, Model):
    email = models.EmailField(max_length=80, unique=True)
    username = None
    first_name = None
    last_name = None
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email


class OTP(Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10, unique=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2, default=settings.MAX_OTP_TRY)
    otp_max_out = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} - {self.user.email}"

    @classmethod
    def generate_otp(cls):
        """Generates a unique 6-digit number as OTP"""
        # TODO: modify to limit number of attempts
        otp = random.randint(100000, 999999)
        otp_exists = cls.objects.filter(otp=otp).exists()
        while otp_exists:
            otp = random.randint(999999, 999999)
            otp_exists = cls.objects.filter(otp=otp).exists()
        return otp
