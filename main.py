from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Telegram accounting bot is running."}

@app.post("/")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        print("Webhook received:", data)
        return {"ok": True}
    except Exception as e:
        print("Webhook error:", e)
        return {"ok": False, "error": str(e)}
