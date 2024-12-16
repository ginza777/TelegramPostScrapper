import datetime

from django.utils import timezone

from app_telegram_client.models import Message, Message_history
from app_telegram_client.models import PostChannel,GetPostChannel
from .views import get_media_files_json_data
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from celery import Celery, shared_task


def message_sent_status(message=None,status=False,channel_from=None,channel_to=None,type=None):
    try:
        message = Message_history.objects.get(message=message,from_channel=channel_from,to_channel=channel_to,type=type)
        message.sent_status = status
        message.time = timezone.now()
        message.save()
    except:
        Message_history.objects.create(message=message, sent_status=status,from_channel=channel_from,to_channel=channel_to,type=type)


def send_msg(data):
    message = Message.objects.get(message_id=data['message_id'])
    url = f"https://api.telegram.org/bot{data['token']}/sendMediaGroup"
    # Fayllarni to'g'ri ko'rsatish uchun
    files = {key: (f"file{index}", file, 'application/octet-stream') for index, (key, file) in
             enumerate(data['files'].items())}

    data['data']['disable_notification'] = True
    r = requests.post(url, data=data['data'], files=files,)
    current_time = datetime.datetime.fromtimestamp(time.time())

    channel_from = GetPostChannel.objects.get(channel_id=data['channel_from'])
    channel_to = PostChannel.objects.get(channel_id=data['data']['chat_id'])
    type = channel_from.type

    if r.status_code == 200:
        message_sent_status(message=message, status=True, channel_from=channel_from, channel_to=channel_to, type=type)

        print(
            f"200 - {data['channel_from']} dan  {data['data']['chat_id']} ga  {data['message_id']} xabar yuborildi  yuborildi time: {current_time}"
        )
        message.send_status = True
        message.save()

    if r.status_code == 400:
        message_sent_status(message=message, status=False, channel_from=channel_from, channel_to=channel_to, type=type)
        print(
            f"400 - {data['channel_from']} dan  {data['data']['chat_id']} ga  {data['message_id']} xabar yuborilmadi   error: {r.json()} time: {current_time}")

def send_message(message_id):
    time.sleep(2)
    data_list = get_media_files_json_data(message_id)
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(send_msg, data_list)
        executor.shutdown(wait=True)
