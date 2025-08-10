# main.py
import asyncio
from flask import Flask, request
from flask_cors import CORS
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
import os
import json
from config import Config
from transaction_manager import handle_bill
from user_manager import welcome_new_member, handle_message
from api_routes import register_api_routes
from utils import setup_logging

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

# 全局 Telegram 应用程序实例
bot_app = None

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
async def webhook():
    """处理 Telegram Webhook 请求"""
    global bot_app
    try:
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        print(f"[{Config.get_timestamp()}] 收到Webhook请求: {request.get_json()}")
        await bot_app.process_update(update)
        return "", 200
    except Exception as e:
        print(f"[{Config.get_timestamp()}] Webhook处理错误: {str(e)}")
        return "", 500

@app.route("/health")
def health():
    """健康检查端点"""
    return "OK", 200

async def start_bot():
    """异步启动Telegram机器人"""
    global bot_app
    setup_logging()
    print(f"[{Config.get_timestamp()}] 检查环境变量: BOT_TOKEN={Config.BOT_TOKEN}, RENDER_EXTERNAL_URL={Config.RENDER_EXTERNAL_URL}")
    if not Config.BOT_TOKEN or not Config.RENDER_EXTERNAL_URL:
        print(f"[{Config.get_timestamp()}] 错误: BOT_TOKEN 或 RENDER_EXTERNAL_URL 未设置")
        return
    try:
        bot_app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        bot_app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
        webhook_url = f"{Config.RENDER_EXTERNAL_URL}/{Config.BOT_TOKEN}"
        print(f"[{Config.get_timestamp()}] 尝试设置Webhook: {webhook_url}")
        await bot_app.bot.set_webhook(
            url=webhook_url,
            allowed_updates=Update.ALL_TYPES
        )
        print(f"[{Config.get_timestamp()}] 机器人Webhook启动")
    except Exception as e:
        print(f"[{Config.get_timestamp()}] Webhook设置失败: {str(e)}")

if __name__ == "__main__":
    register_api_routes(app)  # 注册API路由
    setup_logging()
    print(f"[{Config.get_timestamp()}] 启动Flask服务，端口 {Config.FLASK_PORT}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    app.run(host="0.0.0.0", port=Config.FLASK_PORT)  # 本地运行
