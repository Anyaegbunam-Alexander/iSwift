from django.db.models import Manager
from django.db.models.query import QuerySet


class NonStaffManager(Manager):
    """Return only non staff users"""

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(is_staff=False, is_superuser=False)
            .order_by("first_name")
        )
