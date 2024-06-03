from django.core.management.base import BaseCommand
from django.db import transaction

from finance.data import currencies
from finance.models import Currency


class Command(BaseCommand):
    help = "Update currencies from dict"

    @transaction.atomic
    def handle(self, *args, **options):
        for key, value in currencies.items():
            Currency.objects.get_or_create(name=value, iso_code=key.lower())
        self.stdout.write(self.style.SUCCESS("Operation Success!!"))
