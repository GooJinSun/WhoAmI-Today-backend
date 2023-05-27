# Generated by Django 3.2.13 on 2023-05-27 10:56

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0006_auto_20230527_0834'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content', models.TextField(validators=[django.core.validators.MinLengthValidator(1, 'content length must be greater than 1')])),
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('selected_dates', django.contrib.postgres.fields.ArrayField(base_field=models.DateField(), blank=True, default=list, size=None)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.RemoveField(
            model_name='multiquestion',
            name='selected_date',
        ),
        migrations.AddField(
            model_name='multiquestion',
            name='topic',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='multi_question_set', to='feed.topic'),
        ),
    ]