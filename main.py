import asyncio
import multiprocessing
import atexit

from loguru import logger

from src.userbot.userbot import run_userbot
from src.tokens_handler import TokenHandler
from src.storage.database import MongoTokenStorage
from src.tg_bot.bot import send_startup_message
from config import DB_CONNECTION_STRING, DB_COLLECTION_NAME, TOKENS_LIMIT


mongo_token_storage = MongoTokenStorage(connection_string=DB_CONNECTION_STRING, collection_name=DB_COLLECTION_NAME)
tokens_handler = TokenHandler(token_storage=mongo_token_storage, limit=TOKENS_LIMIT)


def start_userbot() -> None:
    run_userbot()


def start_tokens_handler() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tokens_handler.start_handle())


userbot_process = multiprocessing.Process(target=start_userbot)
tokens_handler_process = multiprocessing.Process(target=start_tokens_handler)


def kill_processes() -> None:
    userbot_process.kill()
    tokens_handler_process.kill()
    tokens_handler.kill_all_process()


if __name__ == '__main__':
    send_startup_message()
    atexit.register(kill_processes)
    userbot_process.start()
    tokens_handler_process.start()
    logger.success("All done.")
