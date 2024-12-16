import asyncio
import datetime
from asyncio import Queue, create_task
from concurrent.futures import ThreadPoolExecutor
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from telethon import events, TelegramClient
from telethon.tl.types import Message, MessageMediaPhoto
from app_telegram_client.functions import *
from app_telegram_client.models import Message as MessageModel
from app_telegram_client.models import TelegramClient as Telegram_user_client, GetPostChannel, Filename
import random
import string

message_queue = Queue()
is_processing = False
executor = ThreadPoolExecutor(max_workers=5)


async def process_queue(client):
    global is_processing
    while not message_queue.empty():
        is_processing = True
        event = await message_queue.get()

        if isinstance(event.message, Message) and hasattr(event.message, 'media'):
            import datetime

            print(f"new message {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            # Handling Media and Caption
            if isinstance(event.message.media, MessageMediaPhoto):
                if event.message.grouped_id is not None:
                    if event.message.grouped_id and event.message.raw_text != '':
                        await process_grouped_media_with_caption(event, client)
                    elif event.message.grouped_id and event.message.raw_text == '':
                        await process_grouped_media_without_caption(event, client)
                else:
                    if event.message.raw_text != '':
                        await process_single_media_with_caption(event, client)
                message_queue.task_done()
        is_processing = False


async def main(phone_number, api_id, api_hash, channel_list):
    session_name = "telegram_client_session"
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start(phone=phone_number)

    # Ensure channel list is properly formatted
    channel_list = [link.replace("https://t.me/", "") for link in channel_list]

    @client.on(events.NewMessage(chats=channel_list))
    async def my_event_handler(event):
        if not is_processing:
            create_task(process_queue(client))
        await message_queue.put(event)

    await client.run_until_disconnected()


async def process_grouped_media_with_caption(event, client):
    photo = event.media.photo
    group_id = event.message.grouped_id
    channel_id = event.message.peer_id.channel_id
    caption = event.message.raw_text
    caption_file = f'media/{group_id}/{group_id}-{random_string(7)}.txt'
    photo_file = f'media/{group_id}/{group_id}-{random_string(7)}.jpeg'

    await client.download_media(photo, file=photo_file)
    await write_caption_to_file(caption_file, caption)
    await crate_message(message_id=group_id, channel_id=channel_id, single_photo=False, caption=caption_file,
                        photo_file=photo_file)


async def process_grouped_media_without_caption(event, client):
    photo = event.media.photo
    group_id = event.message.grouped_id
    channel_id = event.message.peer_id.channel_id
    file_path = f'media/{group_id}/{group_id}-{random_string(7)}.jpeg'
    await client.download_media(photo, file=file_path)
    await crate_message(message_id=group_id, channel_id=channel_id, single_photo=False, caption=None,
                        photo_file=file_path)


async def process_single_media_with_caption(event, client):
    photo = event.media.photo
    message_id = event.message.id
    channel_id = event.message.peer_id.channel_id
    caption = event.message.raw_text
    file_path = f'media/{message_id}/{message_id}-{random_string(7)}.jpeg'
    caption_file = f'media/{message_id}/{message_id}-{random_string(7)}.txt'
    await client.download_media(photo, file=file_path)
    await write_caption_to_file(caption_file, caption)
    await crate_message(message_id=message_id, channel_id=channel_id, single_photo=True, caption=caption_file,
                        photo_file=file_path)


@sync_to_async
def crate_message(message_id, channel_id=None, single_photo=False, photo_file=None, caption=None):
    message, created = MessageModel.objects.get_or_create(message_id=message_id)

    if channel_id is not None:
        try:
            channel = GetPostChannel.objects.get(channel_id=f"-100{channel_id}")
            message.channel_from = channel
            message.save()

        except Exception as e:
            print("error ", e)

    if photo_file is not None:
        try:
            file = Filename.objects.create(filename=photo_file, message_id=message_id, is_photo=True)
            file.save()
            message.photo = True
            message.photo_count += 1
            message.save()

        except Exception as e:
            print("error", e)

    if caption is not None:
        try:
            file = Filename.objects.create(filename=caption, message_id=message_id, is_caption=True)
            message.caption = True
            file.save()
            message.save()

        except Exception as e:
            print("error", e)

    if single_photo:
        try:
            message.single_photo = True
            message.photo_count = 1
            message.photo = True
            message.save()

        except Exception as e:
            print("error", e)


async def write_caption_to_file(file_path, caption_text):
    try:
        with open(file_path, 'w') as f:
            f.write(caption_text)
        return True
    except Exception as e:
        print("error writing caption to file - ", e)


def random_string(length=7):
    """Generates a random string of fixed length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class Command(BaseCommand):
    help = 'Starts the Telegram listener'
    channels = GetPostChannel.get_channel_link_list()
    phonenumber = ''
    api_id = ''
    api_hash = ''

    def get_phone(self):
        """
        This method prompts the user to enter a valid phone number and returns the validated phone number.
        It ensures the phone number is 9 digits long and starts with +998.
        """
        print("User phone number not found. Please provide a new phone number.")

        def validate_phone_number(phone_number: int) -> bool:
            return len(str(phone_number)) == 9

        new_phone_number = None
        while new_phone_number is None or not validate_phone_number(new_phone_number):
            try:
                new_phone_number = int(input("Enter new phone number (e.g., 991234567): "))
                if validate_phone_number(new_phone_number):
                    print("Phone number is valid!")
                else:
                    print("Invalid phone number! It should be 9 digits.")
            except ValueError:
                print("Invalid input! Please enter only numeric values.")

        return new_phone_number

    def get_api_details(self):
        """
        This method collects API ID and API Hash from the user.
        """
        while True:
            try:
                api_id = int(input("Enter your Telegram API ID (integer only): ").strip())
                print(f"API ID {api_id} is valid!")
                break
            except ValueError:
                print("Invalid input! API ID should be an integer.")

        api_hash = input("Enter your Telegram API Hash: ").strip()

        return api_id, api_hash

    def save_client_data(self, phone_number, api_id, api_hash):
        """
        This method saves the provided phone number and API details to the database.
        """
        Telegram_user_client.objects.create(
            phone_number='+998' + str(phone_number),
            telegram_api_id=api_id,
            telegram_api_hash=api_hash
        )
        print("Data successfully saved to the database.")

    def orchestrate_phone_and_api(self):
        """
        This method orchestrates the process of getting the phone number, API details, and saving them.
        """
        new_phone_number = self.get_phone()

        store_phone = input(f"Do you want to store the phone number {new_phone_number}? (yes/no): ").strip().lower()
        if store_phone == 'yes':
            api_id, api_hash = self.get_api_details()

            print("\n\n--- Data Summary ---")
            print(f"Phone Number: {new_phone_number}")
            print(f"API ID: {api_id}")
            print(f"API Hash: {api_hash}")

            save_data = input("Do you want to save these details to the database? (yes/no): ").strip().lower()
            if save_data == 'yes':
                self.save_client_data(new_phone_number, api_id, api_hash)
            else:
                print("Data not saved.")
        else:
            print("Phone number was not saved.")

    def handle(self, *args, **options):
        """
        Main handler for the management command.
        """
        try:
            self.channels = list(GetPostChannel.get_channel_link_list().values_list('channel_link', flat=True))

            if Telegram_user_client.objects.exists():
                telegram_client = Telegram_user_client.objects.first()
                self.phonenumber = telegram_client.phone_number
                self.api_id = telegram_client.telegram_api_id
                self.api_hash = telegram_client.telegram_api_hash

                print("\n\n--- Using Existing Client Details ---")
                print(f"Phone Number: {self.phonenumber}")
                print(f"API ID: {self.api_id}")
                print(f"API Hash: {self.api_hash}")
                print(f"Channel_list: {self.channels}")
            else:
                self.orchestrate_phone_and_api()
                self.channels = list(GetPostChannel.get_channel_link_list().values_list('channel_link', flat=True))

            if not self.channels:
                raise ValueError("Channel list is empty. Please add channels to the database.")

            print("Starting Telegram listener...")
            asyncio.run(main(self.phonenumber, self.api_id, self.api_hash, self.channels))

        except Exception as e:
            print(f"An error occurred: {e}")
