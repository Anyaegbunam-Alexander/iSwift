import logging

import requests
from django.conf import settings
from django.db import transaction

from finance.models import ConversionRate, Currency

logger = logging.getLogger(__name__)


def update_rates():
    currencies = Currency.objects.filter(status=Currency.ACTIVE_STATUS)
    app_id = settings.OPEN_EXCHANGE_APP_ID

    with transaction.atomic():
        try:
            for i, base in enumerate(currencies):
                url = f"https://openexchangerates.org/api/latest.json?app_id={app_id}&base={base.iso_code}&prettyprint=false"  # noqa
                response = requests.get(url, timeout=10)
                print(response.json())
                if response.status_code == 200:
                    for target in currencies[i + 1:]:
                        data = response.json()
                        rate = data.get("rates", {}).get(target.iso_code)
                        if rate and rate != 0:
                            c_rate, _ = ConversionRate.objects.get_or_create(
                                base_currency=base, target_currency=target
                            )
                            c_rate.conversion_rate = rate
                            c_rate.reverse_rate = 1 / rate
                            c_rate.save()
                        else:
                            logger.error(
                                f"Invalid rate received for {base.iso_code} to {target.iso_code}"
                            )
        except Exception as e:
            logger.error(f"An error occurred: {e}")
