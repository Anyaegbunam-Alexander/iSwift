from decimal import Decimal

from rest_framework.serializers import DecimalField as DRFDecimalField


class DecimalField(DRFDecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("decimal_places", 2)
        kwargs.setdefault("max_digits", 10)
        kwargs.setdefault("min_value", Decimal(1.00))
        kwargs.setdefault("max_value", Decimal(10_000_000.00))
        super().__init__(*args, **kwargs)
