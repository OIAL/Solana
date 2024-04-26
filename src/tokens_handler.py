import asyncio
import subprocess

import atexit

from loguru import logger
import psutil

from src.storage.database import AbstractTokenStorage, MongoTokenStorage
from config import INTERPRETER_PATH, SCANNER_FILE_PATH, TRANSACTIONS_SCANNING_TIME_MINUTES


class TokenHandler:
    def __init__(self, token_storage: AbstractTokenStorage, limit: int = 10):
        self.__token_storage = token_storage
        self.__limit = limit
        self.__tokens_in_work: dict[str, subprocess.Popen] = {}

        atexit.register(self.kill_all_process)

    def kill_all_process(self):
        """ Kill all token scanner process """
        for p in self.__tokens_in_work.values():
            p.kill()

    async def start_handle(self):
        while True:
            new_tokens = await self.__get_new_tokens()
            await self.__add_tokens(new_tokens)
            await self.__remove_used_tokens()

            await asyncio.sleep(10)

    async def __add_tokens(self, tokens: list[str]):
        for t in tokens:
            if len(self.__tokens_in_work) >= self.__limit:
                return
            if t in self.__tokens_in_work.keys():
                continue
            process = subprocess.Popen([INTERPRETER_PATH,
                                        SCANNER_FILE_PATH,
                                        str(t),
                                        TRANSACTIONS_SCANNING_TIME_MINUTES])
            logger.debug(f"Start transaction handler in process {process.pid}")
            self.__tokens_in_work[t] = process

    async def __get_new_tokens(self) -> list[str]:
        all_tokens = await self.__token_storage.get_all_tokens()

        new_tokens = []

        for t in all_tokens:
            if t in self.__tokens_in_work:
                continue
            new_tokens.append(t)

        return new_tokens

    async def __remove_used_tokens(self):
        items = self.__tokens_in_work.items()
        tokens_to_remove = []
        for t, p in items:
            if psutil.pid_exists(p.pid):
                tokens_to_remove.append(t)
        for t in tokens_to_remove:
            self.__tokens_in_work.pop(t)
            await self.__token_storage.remove_token(t)


if __name__ == '__main__':
    asyncio.run(TokenHandler(token_storage=MongoTokenStorage(collection_name="tests",
                                                             connection_string="mongodb://localhost:27017")).start_handle())
