# Generated by Django 4.2.11 on 2024-07-13 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0006_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
