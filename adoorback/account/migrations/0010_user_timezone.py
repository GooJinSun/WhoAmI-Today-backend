# Generated by Django 3.2.13 on 2023-08-15 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_auto_20230506_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=models.CharField(default='America/Los_Angeles', max_length=50),
        ),
    ]