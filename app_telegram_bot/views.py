import json
import os
import random
import string
from app_telegram_client import models
from app_telegram_client import models as setting_models


def random_string(length):
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def check_caption_file_exist(message_id):
    file_path = models.Filename.objects.get(message_id=message_id, is_caption=True).filename
    if os.path.exists(file_path):
        return True
    return False


def filter_caption(message_id: str, channel_to_id: str):
    message = models.Message.objects.get(message_id=message_id)

    if models.Message.objects.get(message_id=message_id).caption:
        if check_caption_file_exist(message_id=message_id):
            caption_file_path = models.Filename.objects.get(message_id=message.message_id, is_caption=True).filename

            channel_from = models.Message.objects.get(message_id=message_id).channel_from
            channel_to = setting_models.PostChannel.objects.get(channel_id=channel_to_id)

            keyword_texts = setting_models.KeywordChannelAds.objects.filter(channel=channel_from)
            keyword_text_list = [keyword.text for keyword in keyword_texts]

            my_channel_text = channel_to.sign

            with open(caption_file_path, 'r') as f:
                caption = f.read()
                caption = '\n'.join(line for line in caption.splitlines() if line.strip())
                for key_word in keyword_text_list:
                    caption = caption.replace(key_word, '')
                caption = caption + '\n' + my_channel_text
            return caption
        else:
            caption_file_path = models.Filename.objects.get(message_id=message.message_id, is_caption=True).filename
            with open(caption_file_path, 'r') as f:
                caption = f.read()
                caption = '\n'.join(line for line in caption.splitlines() if line.strip())
            return caption
    return None


def get_photo_filenames_by_message_id(message_id):
    messages = models.Filename.objects.filter(message_id=message_id, is_photo=True)
    photo_filenames = [message.filename for message in messages]
    return photo_filenames


def get_media_files_json_data(message_id):
    media_files = get_photo_filenames_by_message_id(message_id)
    media, files = [], {}
    for media_file in media_files:
        if media_file is not None:
            random_name = os.path.basename(media_file)
            media.append(
                {
                    'type': 'photo',
                    'media': f"attach://{random_name}",
                }
            )
            # Faylni byte ma'lumotga o'qish
            with open(media_file, 'rb') as f:
                file_data = f.read()
            files[random_name] = file_data

    from_channel = models.Message.objects.get(message_id=message_id).channel_from
    from_channel_type = from_channel.type
    my_channels_id_list = models.PostChannel.objects.filter(type=from_channel_type).values_list(
        'channel_id', flat=True)

    data_list = []
    for ch_id in my_channels_id_list:
        caption = filter_caption(message_id, ch_id)
        media[0]['caption'] = f"#{message_id}\n" + caption
        media[0]['parse_mode'] = 'HTML'
        if caption is not None:
            models.Message_history.objects.create(
                message=models.Message.objects.get(message_id=message_id),
                from_channel=from_channel,
                to_channel=models.PostChannel.objects.get(channel_id=ch_id),
                type=from_channel_type,
                sent_status=False
            ).save()
            data_list.append(
                {
                    'data': {'chat_id': ch_id, 'media': json.dumps(media)},
                    'files': files,
                    'token': models.PostChannel.objects.get(channel_id=ch_id).manager_bot.bot_token,
                    'channel_from': from_channel.channel_id,
                    'message_id': message_id,
                    'disable_notification': True
                }
            )

    return data_list


async def write_caption(file_path, caption_text):
    try:
        with open(file_path, 'w') as f:
            f.write(caption_text)
        return True
    except:
        return False
