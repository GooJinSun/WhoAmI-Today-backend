# Generated by Django 3.2.13 on 2024-02-21 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qna', '0003_auto_20240211_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='share_everyone',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]