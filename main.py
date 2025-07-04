from fastapi import FastAPI, Request
from bot import bot, handle_update
import os

app = FastAPI()

@app.post("/")
async def root(request: Request):
    data = await request.json()
    await handle_update(data)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    # 设置 webhook 到 Render 提供的 URL
    base_url = os.getenv("BASE_URL")
    token = os.getenv("BOT_TOKEN")
    if base_url and token:
        from aiogram import Bot
        b = Bot(token=token)
        await b.set_webhook(f"{base_url}")
