# Generated by Django 4.2.15 on 2024-09-14 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_user_options_user_account_use_id_ef0f90_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.CharField(max_length=118, null=True),
        ),
    ]
