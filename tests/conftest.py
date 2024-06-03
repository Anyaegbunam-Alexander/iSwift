from pytest_factoryboy import register

from tests.factories.accounts import OTPFactory, UserFactory
from tests.factories.finance import CurrencyFactory

FACTORIES = [OTPFactory, UserFactory, CurrencyFactory]

for i in FACTORIES:
    register(i)

from tests.fixtures.anon_user import *  # noqa
from tests.fixtures.auth_user import *  # noqa
