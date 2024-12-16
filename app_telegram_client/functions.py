import requests
from telegram import Bot
from telegram.error import TelegramError
import random
import string

def get_bot_info(token: str):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    data = response.json()

    if data["ok"]:
        bot_info = {
            "name": data["result"]["first_name"],
            "username": data["result"]["username"],
            "link": f"https://t.me/{data['result']['username']}"  # Construct the link to the bot
        }
        return bot_info
    else:
        print("Failed to retrieve bot information")
        return None


def check_bot_status_admin(channel_id: int, telegram_token: str) -> bool:
    try:
        # Initialize the bot using the provided token
        bot = Bot(telegram_token)

        # Get the list of administrators for the channel
        admins = bot.get_chat_administrators(channel_id)

        # Get the bot's own ID
        bot_id = bot.get_me().id

        # Check if the bot is an admin
        bot_is_admin = any(admin.user.id == bot_id for admin in admins)

        return bot_is_admin

    except TelegramError as e:
        # Handle specific Telegram API errors
        print(f"Error in check_bot_status_admin: Telegram API error: {e}")
    except Exception as e:
        # Handle general exceptions
        print(f"Error in check_bot_status_admin: {e}")

    return False

def random_string(length):
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


__all__ = ["get_bot_info", "check_bot_status_admin", "random_string"]
