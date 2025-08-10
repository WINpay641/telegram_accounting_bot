# config.py
import os
from datetime import datetime, timezone
import pytz

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7908773608:AAFFqLmGkJ9zbsuymQTFzJxy5IyeN1E9M-U")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5001))
    BOT_PORT = int(os.getenv("PORT", 10000))
    RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")
    INITIAL_ADMIN_USERNAME = "WinPay06_Thomason"
    TIMEZONE = pytz.timezone("Asia/Shanghai")

    @staticmethod
    def get_timestamp():
        """返回格式化的当前时间"""
        return datetime.now(Config.TIMEZONE).strftime("%H:%M:%S")

    @staticmethod
    def get_formatted_datetime(utc_time):
        """转换UTC时间为北京时间"""
        beijing_time = utc_time.replace(tzinfo=timezone.utc).astimezone(Config.TIMEZONE)
        return {
            "timestamp": beijing_time.strftime("%H:%M"),
            "date": beijing_time.strftime("%Y-%m-%d")
        }
