# transaction_manager.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import format_amount, format_exchange_rate

transactions = {}  # 内存存储，建议替换为数据库

def initialize_chat_transactions(chat_id):
    """初始化群组交易存储"""
    if chat_id not in transactions:
        transactions[chat_id] = []

async def handle_bill(update, context, exchange_rates):
    """生成并发送账单"""
    chat_id = str(update.message.chat_id)
    initialize_chat_transactions(chat_id)
    
    recent_transactions = transactions[chat_id][-6:] if len(transactions[chat_id]) >= 6 else transactions[chat_id]
    deposit_count = sum(1 for t in transactions[chat_id] if t.startswith("入款"))
    withdraw_count = sum(1 for t in transactions[chat_id] if t.startswith("下发"))
    bill = "当前账单\n"

    exchange_rate_deposit = exchange_rates[chat_id]["deposit"]
    deposit_fee_rate = exchange_rates[chat_id]["deposit_fee"]
    exchange_rate_withdraw = exchange_rates[chat_id]["withdraw"]
    withdraw_fee_rate = exchange_rates[chat_id]["withdraw_fee"]

    if deposit_count > 0:
        bill += f"入款（{deposit_count}笔）\n"
        for t in reversed([t for t in recent_transactions if t.startswith("入款")]):
            parts = t.split(" -> ")
            timestamp = parts[0].split()[2]
            if len(parts) == 1:
                amount = float(parts[0].split()[1].rstrip('u'))
                bill += f"{timestamp}  {format_amount(amount)}u\n"
            else:
                amount = float(parts[0].split()[1].rstrip('u'))
                adjusted = float(parts[1].split()[0].rstrip('u'))
                rate_info = parts[1].split("[rate=")[1].rstrip("]").split(", fee=")
                historical_rate = float(rate_info[0])
                historical_fee = float(rate_info[1].split(",")[0])
                effective_rate = 1 - historical_fee
                bill += f"{timestamp}  {format_amount(amount)}*{effective_rate:.2f}/{format_exchange_rate(historical_rate)}={format_amount(adjusted)}u\n"

    if withdraw_count > 0:
        if deposit_count > 0:
            bill += "\n"
        bill += f"出款（{withdraw_count}笔）\n"
        for t in reversed([t for t in recent_transactions if t.startswith("下发")]):
            parts = t.split(" -> ")
            timestamp = parts[0].split()[2]
            if len(parts) == 1:
                amount = float(parts[0].split()[1].rstrip('u'))
                bill += f"{timestamp}  {format_amount(amount)}u\n"
            else:
                amount = float(parts[0].split()[1].rstrip('u'))
                adjusted = float(parts[1].split()[0].rstrip('u'))
                rate_info = parts[1].split("[rate=")[1].rstrip("]").split(", fee=")
                historical_rate = float(rate_info[0])
                historical_fee = float(rate_info[1].split(",")[0])
                effective_rate = 1 + historical_fee
                bill += f"{timestamp}  {format_amount(amount)}*{effective_rate:.2f}/{format_exchange_rate(historical_rate)}={format_amount(adjusted)}u\n"

    if deposit_count > 0 or withdraw_count > 0:
        if deposit_count > 0 or withdraw_count > 0:
            bill += "\n"
        if deposit_count > 0:
            bill += f"入款汇率：{format_exchange_rate(exchange_rate_deposit)}  |  费率：{int(deposit_fee_rate*100)}%\n"
        if withdraw_count > 0:
            bill += f"出款汇率：{format_exchange_rate(exchange_rate_withdraw)}  |  费率：{int(withdraw_fee_rate*100)}%\n"
        if deposit_count > 0 or withdraw_count > 0:
            bill += "\n"
        total_deposit = sum(float(t.split()[1].rstrip('u')) for t in transactions[chat_id] if t.startswith("入款"))
        total_deposit_adjusted = sum(float(t.split(" -> ")[1].split()[0].rstrip('u')) if "->" in t else float(t.split()[1].rstrip('u')) for t in transactions[chat_id] if t.startswith("入款"))
        total_withdraw = sum(float(t.split()[1].rstrip('u')) for t in transactions[chat_id] if t.startswith("下发"))
        total_withdraw_adjusted = sum(float(t.split(" -> ")[1].split()[0].rstrip('u')) if "->" in t else float(t.split()[1].rstrip('u')) for t in transactions[chat_id] if t.startswith("下发"))
