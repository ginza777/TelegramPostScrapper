from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from telegram.error import TelegramError

from .functions import *  # noqa


class TelegramClient(models.Model):
    comment = models.TextField(blank=True)
    telegram_api_id = models.IntegerField(unique=True)
    telegram_api_hash = models.CharField(max_length=100, unique=True)
    phone_number = PhoneNumberField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.phone_number)

    def clean(self):
        """ Custom validation for phone number """
        if self.phone_number:
            phone_number = str(self.phone_number)  # Convert to string

            # Check if the phone number starts with +998 and has exactly 9 digits after it
            if not phone_number.startswith('+998') or len(phone_number) != 13:
                from django.core.exceptions import ValidationError
                raise ValidationError("Phone number must start with +998 and be followed by exactly 9 digits.")

    class Meta:
        db_table = 'telegram_client'
        ordering = ['-created_at']
        unique_together = ('telegram_api_id', 'telegram_api_hash')


class PostSenderBot(models.Model):
    bot_name = models.CharField(max_length=100, null=True, blank=True)
    bot_token = models.CharField(max_length=100, unique=True, null=False, blank=False)
    bot_link = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # If bot_token is provided, fetch bot info and populate the fields
        if self.bot_token:
            bot_info = get_bot_info(self.bot_token)
            if bot_info:
                self.bot_name = bot_info["name"]
                self.bot_link = bot_info["link"]

        # Call the original save method to store the object in the database
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return str(self.bot_name)

    class Meta:
        db_table = 'post_sender_bot'
        ordering = ['-created_at']


class Channel_type(models.Model):
    type = models.CharField(max_length=100, unique=True, null=False, blank=False)

    def __str__(self):
        return str(self.type)


class GetPostChannel(models.Model):
    channel_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    channel_link = models.CharField(max_length=100, null=False, blank=False)
    channel_id = models.CharField(unique=True, null=False, blank=False, max_length=30)
    type = models.ForeignKey(Channel_type, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not str(self.channel_id).startswith('-'):
            if str(self.channel_id).startswith('100'):
                self.channel_id = '-' + self.channel_id
            else:
                self.channel_id = '-100' + self.channel_id
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.channel_name)

    @staticmethod
    def get_channel_link_list():
        return GetPostChannel.objects.all().values_list('channel_link', flat=True)


class PostChannel(models.Model):
    channel_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    channel_link = models.CharField(max_length=100, null=False, blank=False)
    channel_id = models.IntegerField(unique=True, null=False, blank=False)
    manager_bot = models.ForeignKey(PostSenderBot, on_delete=models.CASCADE)
    sign=models.TextField(null=True,blank=True)
    type = models.ForeignKey(Channel_type, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Overriding save method to ensure channel_id is properly formatted before saving.
        """
        if not str(self.channel_id).startswith('-'):
            if str(self.channel_id).startswith('100'):
                self.channel_id = '-' + str(self.channel_id)
            else:
                self.channel_id = '-100' + str(self.channel_id)
        super().save(*args, **kwargs)

    def clean(self):
        """
        Custom validation method to check if the bot is an administrator in the channel.
        """
        try:
            is_admin = check_bot_status_admin(self.channel_id, self.manager_bot.bot_token)
            if not is_admin:
                raise ValidationError(
                    f"The bot with token {self.manager_bot.bot_token} is not an admin in the channel {self.channel_id}.")
        except TelegramError as e:
            raise ValidationError(f"Telegram API error occurred while checking admin status: {str(e)}")
        except Exception as e:
            raise ValidationError(f"An error occurred during validation: {str(e)}")


class Message(models.Model):
    message_id = models.CharField(max_length=500, unique=True)
    caption = models.BooleanField(default=False)
    photo = models.BooleanField(default=False)
    channel_from = models.ForeignKey(GetPostChannel, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='from_channel_messages')
    delete_status = models.BooleanField(default=True)
    single_photo = models.BooleanField(default=False)
    send_status = models.BooleanField(default=False)
    photo_count = models.IntegerField(default=0)
    end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.caption and self.photo:
            self.delete_status = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.message_id

    class Meta:
        db_table = 'message'


class Filename(models.Model):
    filename = models.TextField()
    message_id = models.CharField(max_length=100)
    is_photo = models.BooleanField(default=False)
    is_caption = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message_history(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    from_channel = models.ForeignKey(GetPostChannel, on_delete=models.CASCADE, related_name='from_channel', null=True,
                                     blank=True)
    to_channel = models.ForeignKey(PostChannel, on_delete=models.CASCADE, related_name='to_channel', null=True,
                                   blank=True,
                                   )
    type = models.ForeignKey(Channel_type, on_delete=models.CASCADE, null=True, blank=True)
    sent_status = models.BooleanField(default=False)
    time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message.message_id

    class Meta:
        db_table = 'client_message_history'


class KeywordChannelAds(models.Model):
    text = models.TextField()
    channel = models.ForeignKey(GetPostChannel, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'keywordchannelads'
        unique_together = ('text', 'channel')
        # app_label = 'setting_ads'

    def clean(self):
        if KeywordChannelAds.objects.filter(channel=self.channel).exclude(id=self.id).exists():
            raise ValidationError('This channel already has keyword')
