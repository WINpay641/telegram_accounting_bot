import re
from aiogram import Bot
from aiogram.types import Message
from config import ADMIN_USERNAMES
from models import (
    load_data, save_data, new_session, add_income, set_rate, show_bill
)
from utils import parse_amount

async def handle_message(message: Message, bot: Bot):
    username = f"@{message.from_user.username or message.from_user.id}"
    if username not in ADMIN_USERNAMES:
        await message.reply("你没有权限执行此操作。")
        return

    text = message.text.strip()

    if text.startswith("开始"):
        new_session()
        await message.reply("已开始新账单日。")
    elif text.startswith("+"):
        amount = parse_amount(text)
        if amount:
            add_income(amount)
            await message.reply(f"入款成功：{amount:.2f}")
        else:
            await message.reply("格式错误：请使用 +金额")
    elif text.startswith("设置入款汇率"):
        try:
            rate = float(text.replace("设置入款汇率", "").strip())
            set_rate("in_exchange", rate)
            await message.reply(f"设置成功：入款汇率{rate}")
        except:
            await message.reply("格式错误：请输入数字")
    elif text in ("账单", "+0"):
        await message.reply(show_bill())
    else:
        await message.reply("无法识别指令")
