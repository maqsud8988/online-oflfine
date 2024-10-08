# Generated by Django 5.0 on 2024-09-09 17:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_tguser_last_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminOnlineOrOfflineCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(unique=True)),
                ('status', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline'), ('busy', 'Boshqasi bilan gaplashvoti')], default='offline', max_length=10)),
                ('current_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='online_or_offline_admin', to='bot.tguser')),
            ],
        ),
    ]
