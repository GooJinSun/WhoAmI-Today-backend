# Generated by Django 3.2.13 on 2023-06-03 09:17

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0004_auto_20230318_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='selected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='question',
            name='selected_dates',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.DateField(), blank=True, default=list, size=None),
        ),
    ]