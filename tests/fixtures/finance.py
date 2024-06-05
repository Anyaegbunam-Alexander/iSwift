import pytest
from django.db.models import QuerySet

from finance.data import currencies
from finance.models import ConversionRate, Currency
from tests.data import conversion_rates
from tests.factories.finance import iSwiftAccountFactory


@pytest.fixture
def iswift_account_factory():
    return iSwiftAccountFactory


class CurrencyFixtures:
    @pytest.fixture(autouse=True)
    def create_currencies(self, currency_factory) -> QuerySet[Currency]:
        currency_instances = [
            currency_factory.build(iso_code=key, name=value) for key, value in currencies.items()
        ]
        Currency.objects.bulk_create(currency_instances)
        pks = [currency.pk for currency in currency_instances]
        self.currencies_queryset = Currency.objects.filter(pk__in=pks)
        return self.currencies_queryset

    @pytest.fixture(autouse=True)
    def create_conversion_rates(
        self, conversion_rate_factory, create_currencies
    ) -> QuerySet[ConversionRate]:
        assert self.currencies_queryset.exists()
        rates_instances = [
            conversion_rate_factory.build(
                base_currency=self.currencies_queryset.get(iso_code=rate["base_currency"]),
                target_currency=self.currencies_queryset.get(iso_code=rate["target_currency"]),
                conversion_rate=rate["conversion_rate"],
                reverse_rate=rate["reverse_rate"],
            )
            for rate in conversion_rates
        ]
        ConversionRate.objects.bulk_create(rates_instances)
        pks = [rate.pk for rate in rates_instances]
        self.conversion_rates_queryset = ConversionRate.objects.filter(pk__in=pks)
        return self.conversion_rates_queryset
