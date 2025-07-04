from fastapi import FastAPI, Request
from bot import handle_update

app = FastAPI()

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    await handle_update(data)
    return {"ok": True}

@app.get("/")
async def root():
    feturn{"message":"Telrgram accounting bot is running."}
