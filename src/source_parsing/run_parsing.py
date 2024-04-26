from telethon import TelegramClient, events
from telethon.sessions import StringSession

from token_.contract_getter import FirstChannelContractGetter
from config import API_ID, API_HASH, SESSION_STRING


client = TelegramClient(session=StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH)
client.start()

first_channel_contract_getter = FirstChannelContractGetter()


@client.on(events.NewMessage())
async def new_message(event):
    print(await first_channel_contract_getter.get_contract_from_message(event.message.text))


def run():
    client.run_until_disconnected()

