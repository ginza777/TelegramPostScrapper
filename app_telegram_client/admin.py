from .models import TelegramClient, PostSenderBot, Channel_type, PostChannel, GetPostChannel, Filename, Message, \
    Message_history, KeywordChannelAds
from django.contrib import admin
from django.contrib import admin

from .models import TelegramClient, PostSenderBot, Channel_type, PostChannel, GetPostChannel, Filename, Message, \
    Message_history, KeywordChannelAds


@admin.register(TelegramClient)
class TelegramClientAdmin(admin.ModelAdmin):
    list_display = (
        'telegram_api_id',
        'phone_number',
        'created_at'
    )


@admin.register(PostSenderBot)
class PostSenderBotAdmin(admin.ModelAdmin):
    list_display = (
        'bot_name',
        'bot_token',
        'created_at'
    )


# Registering Channel_Type model
@admin.register(Channel_type)
class Channel_TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')  # Adjust based on your model fields


# Registering PostChannel model
@admin.register(PostChannel)
class PostChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_name', 'channel_link', 'channel_id', 'manager_bot', 'created_at', 'updated_at')


# Registering GetPostChannel model
@admin.register(GetPostChannel)
class GetPostChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_name', 'channel_link', 'channel_id', 'type', 'created_at')


@admin.register(Filename)
class FilenameAdmin(admin.ModelAdmin):
    list_display = ('filename',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id',
                    'caption',
                    'channel_from',
                    'single_photo',
                    'photo_count',
                    'end',
                    'delete_status',
                    'photo',

                    )


@admin.register(Message_history)
class Message_historyAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at',)


@admin.register(KeywordChannelAds)
class KeywordChannelAdsAdmin(admin.ModelAdmin):
    list_display = ("text",)
