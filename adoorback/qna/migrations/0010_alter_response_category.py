# Generated by Django 4.2.14 on 2024-11-26 22:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_remove_subscription_category_su_sharing_ac1f89_idx_and_more'),
        ('qna', '0009_alter_response_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='category.category'),
        ),
    ]
