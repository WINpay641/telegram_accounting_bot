from fastapi import FastAPI, Request
from bot import bot, handle_update
import os

app = FastAPI()

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    await handle_update(data)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    from aiogram import Bot
    token = os.getenv("BOT_TOKEN")
    base_url = os.getenv("BASE_URL")
    if token and base_url:
        bot_instance = Bot(token=token)
        await bot_instance.set_webhook(url=base_url)
