# Generated by Django 4.2.6 on 2024-12-16 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_telegram_client', '0004_alter_filename_message_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel_type',
            old_name='channel_name',
            new_name='type',
        ),
    ]
