# Generated by Django 3.2.18 on 2023-05-20 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moment', '0004_alter_moment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moment',
            name='date',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
