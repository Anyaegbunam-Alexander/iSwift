from decimal import Decimal, InvalidOperation

from django.db import models, transaction
from django.db.models import Q
from django_extensions.db.models import ActivatorModel

from accounts.models import User
from core.exceptions import InsufficientFunds, SameAccountOperation
from core.feilds import MoneyField
from core.model_abstracts import Model


class Currency(Model, ActivatorModel):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=6)

    def __str__(self) -> str:
        return self.iso_code

    def get_conversion_rate(self, target: "Currency"):
        if self == target:
            # incase trying to convert from eg. usd to usd
            return Decimal(1), self

        try:
            rate = ConversionRate.objects.get(
                Q(base_currency=self, target_currency=target)
                | Q(base_currency=target, target_currency=self)
            )
            # Determine the correct rate based on the order it was saved
            if rate.base_currency == self:
                # The rate is already self to target
                return rate.conversion_rate, rate

            # The rate is target to self, so return the reciprocal
            return rate.reverse_rate, rate

        except ConversionRate.DoesNotExist:
            # TODO raise error here?
            rate = None, None

    def convert_currency(self, target: "Currency", amount: Decimal) -> Decimal:
        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(amount)
            except InvalidOperation as e:
                raise e

        rate = self.get_conversion_rate(target)[0]
        return (amount * rate).__round__(2)


class ConversionRate(Model):
    base_currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="base_currencies"
    )
    target_currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="target_currencies"
    )
    conversion_rate = MoneyField(decimal_places=10, max_digits=20)
    reverse_rate = MoneyField(decimal_places=10, max_digits=20)


class iSwiftAccount(Model, ActivatorModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="iswift_accounts")
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = MoneyField()
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "iSwift Account"

    @transaction.atomic
    def record_transfer(self, recipients: list, description: str):
        total_amount = sum(re["amount"] for re in recipients)
        if Decimal(total_amount) > self.balance:
            raise InsufficientFunds()

        debit = DebitTransaction(
            description=description,
            iswift_account=self,
            currency=self.currency,
            amount_sent=total_amount,
        )
        if len(recipients) == 1:
            user = recipients[0]["recipient"]
            amount = recipients[0]["amount"]
            debit.recipient = user
            debit.save()
            iswift_account = user.iswift_accounts.get(is_default=True)
            if iswift_account == self:
                raise SameAccountOperation()

            iswift_account.record_credit(debit, amount)
            self.balance -= amount
            self.save()
            return debit

        debit.save()
        for re in recipients:
            user = re["recipient"]
            amount = re["amount"]
            user.iswift_accounts.get(is_default=True).record_credit(debit, amount)
            self.balance -= amount

        self.save()
        return debit

    @transaction.atomic
    def record_credit(self, debit_transaction: "DebitTransaction", amount):

        if self == debit_transaction.iswift_account:
            raise SameAccountOperation()

        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(amount)
            except InvalidOperation as e:
                raise e

        amount_received = debit_transaction.iswift_account.currency.convert_currency(
            self.currency, amount
        )

        credit = CreditTransaction(
            iswift_account=self,
            description=debit_transaction.description,
            debit_transaction=debit_transaction,
            sender=debit_transaction.iswift_account.user,
            amount_sent=amount,
            currency_sent=debit_transaction.iswift_account.currency,
            currency_received=self.currency,
            amount_received=amount_received,
        )
        self.balance += amount_received
        credit.save()
        self.save()

        return credit

    @transaction.atomic
    def set_default(self):
        # Lock the rows to prevent race conditions
        accounts = iSwiftAccount.objects.select_for_update().filter(user=self.user)
        accounts.exclude(pk=self.pk).update(is_default=False)
        self.is_default = True
        self.save(update_fields=["is_default"])
        return self


class DebitTransaction(Model):
    iswift_account = models.ForeignKey(
        iSwiftAccount, on_delete=models.PROTECT, related_name="debit_transactions"
    )
    description = models.CharField(max_length=500)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    recipient = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    amount_sent = MoneyField()

    def save(self, **kwargs):
        data = super().save(**kwargs)
        # TODO send notification
        return data


class CreditTransaction(Model):
    iswift_account = models.ForeignKey(
        iSwiftAccount, on_delete=models.PROTECT, related_name="credit_transactions"
    )
    description = models.CharField(max_length=500)

    debit_transaction = models.ForeignKey(
        DebitTransaction,
        on_delete=models.CASCADE,
        related_name="credit_transactions",
        null=True,
        blank=True,
    )
    amount_received = MoneyField()
    currency_received = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="currency_received",
    )
    sender = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    amount_sent = MoneyField()
    currency_sent = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="currency_sent"
    )

    def save(self, **kwargs):
        data = super().save(**kwargs)
        # TODO send notification
        return data
