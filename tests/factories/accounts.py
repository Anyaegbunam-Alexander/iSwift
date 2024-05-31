from datetime import timedelta

import factory
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from factory import LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker

from accounts.models import OTP, User

fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = LazyAttribute(lambda _: fake.email())
    password = make_password("password")
    first_name = fake.first_name()
    last_name = fake.first_name()
    phone_number = LazyAttribute(lambda _: fake.numerify("###########"))
    country_code = LazyAttribute(lambda _: fake.numerify("###"))
    is_active = True


class OTPFactory(DjangoModelFactory):
    class Meta:
        model = OTP

    user = factory.SubFactory(UserFactory)
    otp = 123456
    otp_expiry = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    max_otp_try = settings.MAX_OTP_TRY
