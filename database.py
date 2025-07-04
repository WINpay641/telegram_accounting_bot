import os
from motor.motor_asyncio import AsyncIOMotorClient

mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_uri) if mongo_uri else None

if client:
    db = client["telegram_bot"]
    messages = db["messages"]

async def save_message(message):
    if client:
        await messages.insert_one({
            "user_id": message.from_user.id,
            "text": message.text,
            "timestamp": message.date.isoformat()
        })
    else:
        # 无数据库时跳过保存
        pass
