# Generated by Django 3.2.13 on 2023-11-18 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('check_in', '0002_checkin_check_in_ch_is_acti_2283ae_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkin',
            name='mood',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
