from django.db.models import Q, QuerySet
from django_filters import rest_framework as df_filters

from accounts.models import User


class UserFilter(df_filters.FilterSet):
    search = df_filters.CharFilter(method="custom_filter")

    class Meta:
        model = User
        fields = []  # We don't need to define any fields here since we are using a custom method

    def custom_filter(self, queryset: QuerySet, name: str, value: str):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(phone_number__icontains=value)
            | Q(last_name__icontains=value)
        ).distinct()
