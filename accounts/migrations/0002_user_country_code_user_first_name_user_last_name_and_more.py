# Generated by Django 5.0.6 on 2024-05-30 12:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country_code',
            field=models.IntegerField(default=123, validators=[django.core.validators.MaxValueValidator(9999), django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(default=123, max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(default=123, max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.IntegerField(default=1, unique=True, validators=[django.core.validators.MaxValueValidator(99999999999), django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
    ]
