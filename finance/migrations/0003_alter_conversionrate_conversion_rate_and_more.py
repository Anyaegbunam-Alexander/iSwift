# Generated by Django 5.0.6 on 2024-06-03 09:28

import core.feilds
import django.core.validators
from decimal import Decimal
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_alter_conversionrate_conversion_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversionrate',
            name='conversion_rate',
            field=core.feilds.MoneyField(decimal_places=10, default=0.0, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='conversionrate',
            name='reverse_rate',
            field=core.feilds.MoneyField(decimal_places=10, default=0.0, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
    ]
