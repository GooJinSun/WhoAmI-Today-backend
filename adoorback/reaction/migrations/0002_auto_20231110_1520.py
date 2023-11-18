# Generated by Django 3.2.13 on 2023-11-10 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reaction', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reaction',
            options={'ordering': ['created_at']},
        ),
        migrations.RemoveConstraint(
            model_name='reaction',
            name='unique_reaction',
        ),
        migrations.AddConstraint(
            model_name='reaction',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted__isnull', True)), fields=('user', 'emoji', 'content_type', 'object_id'), name='unique_reaction'),
        ),
    ]
