# Generated by Django 3.2.13 on 2023-08-15 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moment', '0005_alter_moment_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='moment',
            name='available_limit',
            field=models.DateTimeField(default='2008-10-03'),
        ),
        migrations.AlterField(
            model_name='moment',
            name='date',
            field=models.DateField(default='2008-10-03'),
        ),
    ]
