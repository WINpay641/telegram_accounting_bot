from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, Update
from aiogram.dispatcher.router import Router
from database import save_message
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

router = Router()
dp.include_router(router)

@router.message()
async def handle_all(message: Message):
    await save_message(message)
    await message.reply(f"收到：{message.text}")

async def handle_update(data):
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
