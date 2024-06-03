import logging
from decimal import Decimal, getcontext

import requests
from django.db import transaction

from finance.models import ConversionRate, Currency

logger = logging.getLogger(__name__)
getcontext().prec = 8


def update_rates():
    currencies = Currency.objects.filter(status=Currency.ACTIVE_STATUS)

    with transaction.atomic():
        try:
            for i, base in enumerate(currencies):
                url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base.iso_code}.json"  # noqa
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # fmt:off
                    for target in currencies[i + 1:]:
                        # fmt:on
                        data = response.json()
                        rate = data.get(base.iso_code, {}).get(target.iso_code)
                        if rate:
                            rate_str = "{:.8f}".format(rate)
                            rate_decimal = Decimal(rate_str)
                            if rate_decimal != 0:
                                c_rate, _ = ConversionRate.objects.get_or_create(
                                    base_currency=base, target_currency=target
                                )
                                c_rate.conversion_rate = rate_decimal
                                c_rate.reverse_rate = Decimal("1") / rate_decimal
                                c_rate.save()
                            else:
                                logger.error(
                                    f"Invalid rate received for {base.iso_code} to {target.iso_code}"  # noqa
                                )

        except Exception as e:
            print(e)
