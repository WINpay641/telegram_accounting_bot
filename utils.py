# utils.py
import logging
from config import Config

def format_amount(amount):
    """格式化金额，去除末尾.00或保留两位小数"""
    formatted = f"{amount:.2f}"
    if formatted.endswith(".00"):
        return str(int(amount))
    return formatted

def format_exchange_rate(rate):
    """格式化汇率，保留三位或两位小数"""
    formatted = f"{rate:.3f}"
    if formatted.endswith("0"):
        return f"{rate:.2f}"
    return formatted

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
