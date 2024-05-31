from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from drf_spectacular.utils import extend_schema_field


class MoneyField(models.DecimalField):
    # TODO: confirm if this decorator works
    @extend_schema_field({"type": "number", "format": "float", "example": "1234.56"})
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", 0.00)
        kwargs.setdefault("decimal_places", 2)
        kwargs.setdefault("max_digits", 10)
        kwargs.setdefault("validators", [MinValueValidator(Decimal("0.00"))])
        super().__init__(*args, **kwargs)
