# Generated by Django 4.2.6 on 2024-12-16 11:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_telegram_client', '0005_rename_channel_name_channel_type_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='postchannel',
            name='sign',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='message_history',
            name='from_channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_channel', to='app_telegram_client.getpostchannel'),
        ),
        migrations.AlterField(
            model_name='message_history',
            name='to_channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_channel', to='app_telegram_client.postchannel'),
        ),
    ]
