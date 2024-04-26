from abc import ABC, abstractmethod

from telethon import TelegramClient, events

from loguru import logger

from src.source_parsing.token_extractor import (
    FirstChannelTokenExtractor,
    SecondChannelTokenExtractor,
    ThirdChannelTokenExtractor
)
from src.userbot.exceptions import TokenNotFoundInMessage
from src.storage.database import MongoTokenStorage
from config import DB_CONNECTION_STRING, DB_COLLECTION_NAME


class AbstractHandlersContainer(ABC):
    def __init__(self, client: TelegramClient):
        self._client = client

    @abstractmethod
    def register_handlers(self):
        """ Contains handlers definitions. """
        raise NotImplementedError("Method register_handlers() not implemented.")


class ChannelsHandlersContainer(AbstractHandlersContainer):
    def __init__(self, client: TelegramClient):
        super().__init__(client)
        self.mongo_token_storage = MongoTokenStorage(
            connection_string=DB_CONNECTION_STRING,
            collection_name=DB_COLLECTION_NAME
        )

    def register_handlers(self) -> None:
        @self._client.on(events.NewMessage(chats=[-1002089113352]))
        async def on_new_message_from_first_channel(event):
            """
            Handles new message event
            in first channel & extracts
            token from message text.
            """
            try:
                token = await FirstChannelTokenExtractor().get_token_from_message(event.message.text)
                await self.mongo_token_storage.add_token(token)
            except TokenNotFoundInMessage:
                logger.error("Can't find token in message text from FIRST channel.")

        @self._client.on(events.NewMessage(chats=[-1002013265959]))
        async def on_new_message_from_second_channel(event):
            try:
                token = await SecondChannelTokenExtractor().get_token_from_message(event.message.text)
                await self.mongo_token_storage.add_token(token)
            except TokenNotFoundInMessage:
                logger.error("Can't find token in message text from SECOND channel.")

        logger.success("ChannelsHandlersContainer's handlers registered.")
