from telethon import TelegramClient
from telethon.sessions import StringSession

from loguru import logger

from src.userbot.handlers import ChannelsHandlersContainer

from config import API_ID, API_HASH, SESSION_STRING


def run_userbot() -> None:
    client = TelegramClient(session=StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH)
    client.start()

    container = ChannelsHandlersContainer(client)
    container.register_handlers()

    logger.success("Userbot started successfuly")

    client.run_until_disconnected()


if __name__ == '__main__':
    run_userbot()
