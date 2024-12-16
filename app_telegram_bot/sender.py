import requests


def send_msg(message, token, channel_id):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': channel_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    r = requests.post(url, data=params)
    if r.status_code == 200:
        return True
    else:
        return False


def send_as_photo(image_caption, image, token, channel_id):
    url = f'https://api.telegram.org/bot{token}/sendPhoto'
    params = {
        'chat_id': channel_id,
        'caption': image_caption,
        'parse_mode': 'HTML',
        'photo': image,
    }
    r = requests.post(url, data=params)
    if r.status_code != 200:
        return False, r.status_code
    else:
        return True, r.status_code
