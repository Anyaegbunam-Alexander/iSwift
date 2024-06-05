import factory
from factory.django import DjangoModelFactory
from faker import Faker

from finance.models import (
    ConversionRate,
    CreditTransaction,
    Currency,
    DebitTransaction,
    iSwiftAccount,
)
from tests.factories.accounts import UserFactory

fake = Faker()


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency


class ConversionRateFactory(DjangoModelFactory):
    class Meta:
        model = ConversionRate

    base_currency = factory.Iterator(Currency.objects.all())
    target_currency = factory.Iterator(Currency.objects.all())


class iSwiftAccountFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    name = fake.words(nb=4, unique=True)
    currency = factory.Iterator(Currency.objects.all())
    is_default = True
    balance = factory.LazyAttribute(lambda _: fake.numerify("99###.##"))

    class Meta:
        model = iSwiftAccount


class DebitTransactionFactory(DjangoModelFactory):
    iswift_account = factory.SubFactory(iSwiftAccountFactory)
    currency = factory.Iterator(Currency.objects.all())
    description = fake.words(nb=5)
    recipient = factory.SubFactory(UserFactory)

    class Meta:
        model = DebitTransaction


class CreditTransactionFactory(DjangoModelFactory):
    iswift_account = factory.SubFactory(iSwiftAccountFactory)
    description = fake.words(nb=5)
    debit_transaction = factory.SubFactory(DebitTransactionFactory)
    currency_received = factory.Iterator(Currency.objects.all())
    sender = factory.SubFactory(UserFactory)
    currency_sent = factory.Iterator(Currency.objects.all())

    class Meta:
        model = CreditTransaction
