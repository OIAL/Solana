import asyncio
from abc import ABC, abstractmethod

from loguru import logger

from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_COLLECTION_NAME, DB_CONNECTION_STRING

TIME_OFFSET = 6


class AbstractTokenStorage(ABC):
    @abstractmethod
    async def add_token(self, token: str) -> None:
        ...

    @abstractmethod
    async def remove_token(self, token: str) -> None:
        ...

    @abstractmethod
    async def get_all_tokens(self) -> list[str]:
        ...


class AbstractTransactionStorage(ABC):

    @abstractmethod
    async def add_transaction(self, *, token: str, signature: str) -> None:
        ...

    @abstractmethod
    async def get_transaction_and_delete(self) -> str:
        ...


class MongoTransactionStorage(AbstractTransactionStorage):
    def __init__(self, *, connection_string: str, db_name: str, collection_name: str):
        self.__connection_string: str = connection_string

        self.__mongo_client = AsyncIOMotorClient(self.__connection_string)

        self.__collection = self.__mongo_client[db_name][collection_name]

    async def add_transaction(self, *, token: str, signature: str) -> None:
        await self.__collection.update_one(filter={"token": token, "signature": signature},
                                           update={"$setOnInsert": {"token": token, "signature": signature}},
                                           upsert=True)

    async def get_transaction_and_delete(self) -> dict | None:
        document = await self.__collection.find_one_and_delete({"token": {"$exists": True},
                                                                "signature": {"$exists": True}})

        if not document:
            return

        return {"signature": document["signature"],
                "token": document["token"]}


class MongoTokenStorage(AbstractTokenStorage):
    def __init__(self, *, connection_string: str, collection_name: str):
        self.__connection_string: str = connection_string  # String to connect to mongodb

        # MongoDB client to save tokens, and work with them
        self.__mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(self.__connection_string)
        self.__collection_name: str = collection_name

    @property
    def __database(self):

        return self.__mongo_client["TokensDatabase"]

    @property
    def __token_collection(self):
        return self.__database[self.__collection_name]

    async def add_token(self, token: str) -> None:
        """ Add SOL token to mongoDB """
        tokens = self.__token_collection
# <<<<<<< HEAD
#         await tokens.insert_one({
#             "token": token
#         })
# =======

        await tokens.update_one(filter={"token": token},
                                update={"$setOnInsert": {"token": token}},
                                upsert=True)
# >>>>>>> f24b2126b5ba65d90ac0dbc63e0160965fdb7fd7

        logger.success(f"New token ({token}) was successfuly inserted to database.")

    async def remove_token(self, token: str):
        tokens = self.__token_collection
        await tokens.delete_one({"token": token})

    async def get_all_tokens(self) -> list[str]:
        """ Get all tokens from collection """
        tokens = self.__token_collection

        all_documents = tokens.find({})
        all_tokens = []

        async for d in all_documents:
            if "token" not in d.keys():
                continue
            all_tokens.append(d["token"])

        return all_tokens


if __name__ == '__main__':
    mts = MongoTokenStorage(connection_string=DB_CONNECTION_STRING,
                            collection_name=DB_COLLECTION_NAME)

    # mtrs = MongoTransactionStorage(connection_string="mongodb://localhost:27017",
    #                                collection_name="tests",
    #                                db_name="TokensDatabase")

    asyncio.run(mts.add_token("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"))

