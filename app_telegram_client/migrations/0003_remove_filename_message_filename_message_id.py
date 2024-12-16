# Generated by Django 4.2.6 on 2024-12-15 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_telegram_client', '0002_alter_filename_filename_alter_message_channel_from'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filename',
            name='message',
        ),
        migrations.AddField(
            model_name='filename',
            name='message_id',
            field=models.CharField(default=1, max_length=100, unique=True),
            preserve_default=False,
        ),
    ]
