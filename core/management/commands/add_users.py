from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from accounts.models import User

fake = Faker()


class Command(BaseCommand):
    help = "Create demo users"

    @transaction.atomic
    def handle(self, *args, **options):
        users = []

        for _ in range(10):
            users.append(
                User(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone_number=fake.numerify("###########"),
                    country_code=fake.numerify("###"),
                )
            )
        User.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS("Operation Success!!"))
