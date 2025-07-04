from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import os
from database import save_message

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

async def handle_update(data):
    update = types.Update(**data)
    await dp.feed_update(bot, update)

@dp.message()
async def handle_message(message: Message):
    await save_message(message)
    await message.reply(f"收到：{message.text}")
