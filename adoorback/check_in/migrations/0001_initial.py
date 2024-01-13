# Generated by Django 3.2.13 on 2023-11-18 02:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0016_alter_friendgroup_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('mood', models.CharField(blank=True, max_length=1, null=True)),
                ('availability', models.CharField(choices=[('no_status', 'No Status'), ('not_available', 'Not Available'), ('may_be_slow', 'May Be Slow'), ('available', 'Available')], default='no_status', max_length=20)),
                ('description', models.CharField(blank=True, max_length=88, null=True)),
                ('share_everyone', models.BooleanField(default=True)),
                ('readers', models.ManyToManyField(related_name='read_check_ins', to=settings.AUTH_USER_MODEL)),
                ('share_friends', models.ManyToManyField(blank=True, related_name='shared_check_ins', to=settings.AUTH_USER_MODEL)),
                ('share_groups', models.ManyToManyField(blank=True, related_name='shared_check_ins', to='account.FriendGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='check_in_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
