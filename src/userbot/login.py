from telethon import TelegramClient
from telethon.sessions import StringSession

from config import API_ID, API_HASH


if __name__ == '__main__':
    with TelegramClient(session=StringSession(), api_id=API_ID, api_hash=API_HASH) as client:
        print(f"Here's your session string: {client.session.save()}")
        print("Put it in .env file.")
