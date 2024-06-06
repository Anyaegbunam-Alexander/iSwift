from decimal import Decimal

import pytest

from finance.models import (
    ConversionRate,
    CreditTransaction,
    Currency,
    DebitTransaction,
    iSwiftAccount,
)
from tests.fixtures.finance import CurrencyFixtures

pytestmark = pytest.mark.django_db


class TestCurrency(CurrencyFixtures):
    @pytest.mark.finance_models
    def test_get_conversion_rate(self):
        first = Currency.objects.filter(iso_code="usd").first()
        second = Currency.objects.filter(iso_code="eur").first()
        rate = ConversionRate.objects.filter(base_currency=first, target_currency=second).first()
        assert rate
        assert first.get_conversion_rate(second) == (rate.conversion_rate, rate)
        assert second.get_conversion_rate(first) == (rate.reverse_rate, rate)

    @pytest.mark.finance_models
    def test_convert_currency(self):
        first = Currency.objects.filter(iso_code="usd").first()
        second = Currency.objects.filter(iso_code="eur").first()
        amount = Decimal(100)
        rate = ConversionRate.objects.filter(base_currency=first, target_currency=second).first()
        assert rate
        assert (first.get_conversion_rate(second)[0] * amount).__round__(
            2
        ) == first.convert_currency(second, amount)


class TestiSwiftAccount(CurrencyFixtures):
    @pytest.mark.finance_models
    def test_bulk_record_transfer(self, iswift_account_factory):
        sender: iSwiftAccount = iswift_account_factory()
        original_balance = sender.balance
        receivers: list[iSwiftAccount] = [iswift_account_factory() for _ in range(3)]
        recipients = [{"recipient": i.user, "amount": 100} for i in receivers]
        debit = sender.record_transfer(recipients, "Bulk Transfer")
        assert isinstance(debit, DebitTransaction)
        for r in receivers:
            account = iSwiftAccount.objects.filter(pk=r.pk).first()
            conversion_rate = sender.currency.get_conversion_rate(r.currency)[0]
            expected_balance = (r.balance + (conversion_rate * 100)).__round__(2)
            assert account.balance == expected_balance

        assert (
            iSwiftAccount.objects.filter(pk=sender.pk).first().balance
            == (original_balance - 300)
            == sender.balance
        )

    @pytest.mark.finance_models
    def test_single_record_transfer(self, iswift_account_factory):
        sender: iSwiftAccount = iswift_account_factory()
        original_balance = sender.balance
        receiver: iSwiftAccount = iswift_account_factory()
        recipients = [{"recipient": receiver.user, "amount": 100}]
        debit = sender.record_transfer(recipients, "Bulk Transfer")
        assert isinstance(debit, DebitTransaction)
        r_account = iSwiftAccount.objects.filter(pk=receiver.pk).first()
        expected_balance = receiver.balance + sender.currency.convert_currency(
            receiver.currency, 100
        )
        assert r_account.balance == expected_balance

        assert (
            iSwiftAccount.objects.filter(pk=sender.pk).first().balance
            == (original_balance - 100)
            == sender.balance
        )

    @pytest.mark.finance_models
    def test_record_credit(self, iswift_account_factory, debit_transaction_factory):
        account: iSwiftAccount = iswift_account_factory()
        original_balance = account.balance
        debit: DebitTransaction = debit_transaction_factory()
        credit = account.record_credit(debit, debit.amount_sent)
        amount_received = debit.iswift_account.currency.convert_currency(
            account.currency, debit.amount_sent
        )
        assert isinstance(credit, CreditTransaction)
        assert (
            iSwiftAccount.objects.filter(pk=account.pk).first().balance
            == (original_balance + amount_received)
            == account.balance
        )
        assert amount_received == credit.amount_received

    @pytest.mark.finance_models
    def test_set_default(self, iswift_account_factory):
        acc = iswift_account_factory(is_default=False)
        [iswift_account_factory(user=acc.user) for _ in range(3)]
        assert acc.set_default().is_default
        assert acc.is_default
        accs = iSwiftAccount.objects.filter(user=acc.user).exclude(pk=acc.pk)
        for i in accs:
            assert not i.is_default
