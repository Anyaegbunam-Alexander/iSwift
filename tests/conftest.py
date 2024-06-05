from pytest_factoryboy import register

from tests.factories.accounts import OTPFactory, UserFactory
from tests.factories.finance import (
    ConversionRateFactory,
    CreditTransactionFactory,
    CurrencyFactory,
    DebitTransactionFactory,
    iSwiftAccountFactory,
)

FACTORIES = [
    OTPFactory,
    UserFactory,
    CurrencyFactory,
    ConversionRateFactory,
    iSwiftAccountFactory,
    DebitTransactionFactory,
    CreditTransactionFactory,
]

for i in FACTORIES:
    register(i)

from tests.fixtures.anon_user import *  # noqa
from tests.fixtures.auth_user import *  # noqa
from tests.fixtures.finance import *  # noqa
