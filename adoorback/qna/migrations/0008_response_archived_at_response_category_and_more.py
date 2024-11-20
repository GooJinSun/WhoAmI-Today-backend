# Generated by Django 4.2.14 on 2024-11-19 04:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
        ('qna', '0007_response_is_edited'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='archived_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='response',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='category.category'),
        ),
        migrations.AddField(
            model_name='response',
            name='sharing_scope',
            field=models.CharField(default='private', max_length=255),
        ),
    ]
