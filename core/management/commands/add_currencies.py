from django.core.management.base import BaseCommand
from django.db import transaction

from core.data import currencies
from finance.models import Currency
from finance.utils import update_rates


class Command(BaseCommand):
    help = "Create currencies if updated"

    @transaction.atomic
    def handle(self, *args, **options):
        # for key, value in currencies.items():
        #     Currency.objects.get_or_create(name=value, iso_code=key)
        update_rates()
        self.stdout.write(self.style.SUCCESS("Operation Success!!"))
