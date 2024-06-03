from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import ActivatorModel

from accounts.models import User
from core.feilds import MoneyField
from core.model_abstracts import Model


class Currency(Model, ActivatorModel):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=5)


class ConversionRate(Model):
    base_currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="base_currencies"
    )
    target_currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="target_currencies"
    )
    conversion_rate = MoneyField()
    reverse_rate = MoneyField()


class iSwiftAccount(Model, ActivatorModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="iswift_accounts")
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = MoneyField()


class TransactionActivity(Model):
    DEBIT = "debit"
    CREDIT = "credit"

    TYPE_CHOICES = (
        (DEBIT, _(DEBIT)),
        (CREDIT, _(CREDIT)),
    )
    iswift_account = models.ForeignKey(iSwiftAccount, on_delete=models.PROTECT)
    type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    amount = MoneyField()
    description = models.CharField(max_length=500)
