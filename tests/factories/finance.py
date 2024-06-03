
from factory.django import DjangoModelFactory
from faker import Faker

from finance.models import Currency

fake = Faker()


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency
