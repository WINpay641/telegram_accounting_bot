# main.py
import threading
import asyncio
from flask import Flask
from flask_cors import CORS
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from dotenv import load_dotenv
import os
from config import Config
from transaction_manager import handle_bill
from user_manager import welcome_new_member, handle_message
from api_routes import register_api_routes
from utils import setup_logging

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

def run_flask():
    """启动Flask服务"""
    setup_logging()
    flask_port = Config.FLASK_PORT
    print(f"[{Config.get_timestamp()}] 启动Flask服务，端口 {flask_port}")
    from gunicorn.app.base import BaseApplication

    class FlaskApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key, value)

        def load(self):
            return self.application

    options = {
        'bind': f'0.0.0.0:{flask_port}',
        'workers': 2,
        'timeout': 120,
        'accesslog': '-',
        'errorlog': '-',
    }
    FlaskApplication(app, options).run()

def run_bot():
    """启动Telegram机器人"""
    setup_logging()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_bot = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app_bot.run_webhook(
        listen="0.0.0.0",
        port=Config.BOT_PORT,
        url_path=f"/{Config.BOT_TOKEN}",
        webhook_url=f"{Config.RENDER_EXTERNAL_URL}/{Config.BOT_TOKEN}"
    )
    print(f"[{Config.get_timestamp()}] 机器人Webhook启动，端口 {Config.BOT_PORT}")
    loop.run_forever()

if __name__ == "__main__":
    register_api_routes(app)  # 注册API路由
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    run_bot()
