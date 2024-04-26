from aiogram import Router
from aiogram.filters import CommandStart
from aiogram import types

base_router = Router()


@base_router.message(CommandStart)
async def cmd_start(msg: types.Message):
    await msg.answer("Solana tokens bot!")


