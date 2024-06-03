from django.contrib import admin

from finance.models import (
    ConversionRate,
    CreditTransaction,
    Currency,
    DebitTransaction,
    iSwiftAccount,
)

admin.site.register(iSwiftAccount)
admin.site.register(Currency)
admin.site.register(ConversionRate)
admin.site.register(DebitTransaction)
admin.site.register(CreditTransaction)
