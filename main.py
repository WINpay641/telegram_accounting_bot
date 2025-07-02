from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from config import TOKEN, ADMIN_USERNAMES
from handlers import handle_message

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def all_messages_handler(message: Message):
    await handle_message(message, bot)

if name == '__main__':
    executor.start_polling(dp)
