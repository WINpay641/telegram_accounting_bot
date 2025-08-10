# transaction_parser.py
import re
from utils import format_amount, format_exchange_rate
from config import Config

def parse_transaction(message_text, chat_id, operator_name, utc_time, exchange_rates):
    """解析交易命令，返回格式化的交易记录"""
    try:
        time_info = Config.get_formatted_datetime(utc_time)
        timestamp, date = time_info["timestamp"], time_info["date"]
        
        if message_text.startswith("入款") or message_text.startswith("+"):
            amount_str = message_text.replace("入款", "").replace("+", "").strip()
            exchange_rate = exchange_rates[chat_id]["deposit"]
            fee_rate = exchange_rates[chat_id]["deposit_fee"]
            if amount_str.lower().endswith('u'):
                amount = float(amount_str.rstrip('uU'))
                return f"入款 {format_amount(amount)}u {timestamp} {date} [operator={operator_name}]"
            amount = float(amount_str)
            adjusted_amount = amount * (1 - fee_rate) / exchange_rate
            return f"入款 {format_amount(amount)} {timestamp} {date} -> {format_amount(adjusted_amount)}u [rate={format_exchange_rate(exchange_rate)}, fee={fee_rate}, operator={operator_name}]"
        
        elif message_text.startswith("下发"):
            amount_str = message_text.replace("下发", "").strip()
            exchange_rate = exchange_rates[chat_id]["withdraw"]
            fee_rate = exchange_rates[chat_id]["withdraw_fee"]
            if amount_str.lower().endswith('u'):
                amount = float(amount_str.rstrip('uU'))
                return f"下发 {format_amount(amount)}u {timestamp} {date} [operator={operator_name}]"
            amount = float(amount_str)
            adjusted_amount = amount * (1 + fee_rate) / exchange_rate
            return f"下发 {format_amount(amount)} {timestamp} {date} -> {format_amount(adjusted_amount)}u [rate={format_exchange_rate(exchange_rate)}, fee={fee_rate}, operator={operator_name}]"
        
        return None
    except ValueError:
        return None
