import os
import shutil
from datetime import timedelta
from app_telegram_bot.sender_msg import send_message
from celery import shared_task, Celery
from django.db.models import Q
from django.utils import timezone

from app_telegram_client.models import Message, Filename


app = Celery('task', broker='redis://localhost:6379/0')


def check_photo_caption_with_count(message_id):
    message = Message.objects.get(message_id=message_id)
    if message.photo_count > 0:
        photo_file = Filename.objects.filter(message_id=message_id, is_photo=True)
        caption_file = Filename.objects.filter(message_id=message_id, is_caption=True)
        if photo_file.count() == message.photo_count and caption_file.count() == 1:
            return True
        else:
            print("error task.py 23")
            return False


def check_files_existence(message_id):
    # Fetch image and caption file paths from the database
    message = Message.objects.get(message_id=message_id)
    image_file_paths = Filename.objects.filter(message_id=message_id, is_photo=True).values_list('filename', flat=True)
    caption_file_paths = Filename.objects.filter(message_id=message_id, is_caption=True).values_list('filename',
                                                                                                     flat=True)

    # Check if all image files exist
    all_image_files_exist = all(os.path.exists(image_path) for image_path in image_file_paths)

    # Check if all caption files exist
    all_caption_files_exist = all(os.path.exists(caption_path) for caption_path in caption_file_paths)

    if not all_image_files_exist:
        missing_image = next((image_path for image_path in image_file_paths if not os.path.exists(image_path)), None)
        if missing_image:
                print("error task.py 43")
    if not all_caption_files_exist:
        missing_caption = next(
            (caption_path for caption_path in caption_file_paths if not os.path.exists(caption_path)), None)
        if missing_caption:
            print("error task.py 48")

    if all_image_files_exist and all_caption_files_exist:
        message.end = True
        message.save()
        return True

    return False


@shared_task
def send_message_task():
    messages = Message.objects.filter(
        send_status=False,
        delete_status=False,
        channel_from__isnull=False  # Filter qo'shildi
    )
    for message in messages:
        if check_photo_caption_with_count(message_id=message.message_id):
            if check_files_existence(message_id=message.message_id):
                send_message(message_id=message.message_id)


@shared_task
def delete_message_task():
    # Bugungi sana olish
    today = timezone.now()

    txt = f"delete_message: today={today}\n"
    txt_not = ''
    # Bir kun oldingi sana
    one_day_ago = today - timedelta(days=1)
    # Send_status=True yoki Delete_status=True va updated_at oldingi sana
    messages = Message.objects.filter(Q(send_status=True) | Q(delete_status=True), updated_at__lt=one_day_ago)
    for message_id in messages.values_list('message_id', flat=True):
        folder_name = f"media/{message_id}"
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
            txt += f"EXISTS    = {message_id}\n"
        else:
            txt_not += f"NOTEXISTS = {message_id}\n"
    txt += txt_not
    txt += f"delete_message count: {messages.count()}\n"
    print("error task.py 91",txt)
