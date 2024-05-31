from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from core.feilds import MoneyField
from core.model_abstracts import Model


class iSwiftAccount(Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = MoneyField()


class TransactionActivity(Model):
    DEBIT = "debit"
    CREDIT = "credit"

    TYPE_CHOICES = (
        (DEBIT, _(DEBIT)),
        (CREDIT, _(CREDIT)),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    amount = MoneyField()
    description = models.CharField(max_length=500)
