import asyncio

import requests

from config import BOT_API, OUTPUT_CHAT_ID


async def send_transaction(*, token: str, signature: str, swap: float):
    text = f"Token: {token}"
    r = requests.get(f"https://api.telegram.org/bot{BOT_API}/sendMessage?chat_id={OUTPUT_CHAT_ID}&text={text}")


def send_startup_message():
    text = "Application successfully started."
    r = requests.get(f"https://api.telegram.org/bot{BOT_API}/sendMessage?chat_id={OUTPUT_CHAT_ID}&parse_mode=html&text=<b>{text}</b>")
