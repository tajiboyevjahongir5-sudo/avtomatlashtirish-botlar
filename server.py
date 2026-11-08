import os
import json
import asyncio
import random
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

load_dotenv()

API_ID = int(os.getenv("API_ID", "12345678"))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOTS_FILE = "bots.json"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

app = FastAPI(title="TeleAuto WebApp Backend")

# Telethon mijozini yaratish
client = TelegramClient("user_session", API_ID, API_HASH)

class SendCodeRequest(BaseModel):
    phone: str

class VerifyCodeRequest(BaseModel):
    phone: str
    code: str
    phone_code_hash: str
    password: Optional[str] = None

class BotTask(BaseModel):
    username: str
    command: str = "/start"
    button_text: Optional[str] = None

def load_bots() -> List[dict]:
    if os.path.exists(BOTS_FILE):
        try:
            with open(BOTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_bots(bots: List[dict]):
    with open(BOTS_FILE, "w", encoding="utf-8") as f:
        json.dump(bots, f, ensure_ascii=False, indent=2)

@app.on_event("startup")
async def startup_event():
    await client.connect()
    logging.info("Telethon mijoziga ulanish o'rnatildi.")

@app.get("/api/status")
async def get_status():
    if not client.is_connected():
        await client.connect()
    is_auth = await client.is_user_authorized()
    user_name = "Noma'lum"
    if is_auth:
        me = await client.get_me()
        user_name = me.username or me.first_name or "Ulangan"
    return {"connected": is_auth, "user": user_name}

@app.post("/api/auth/send-code")
async def send_code(req: SendCodeRequest):
    if not client.is_connected():
        await client.connect()
    try:
        sent = await client.send_code_request(req.phone)
        return {"ok": True, "phone_code_hash": sent.phone_code_hash}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/verify-code")
async def verify_code(req: VerifyCodeRequest):
    if not client.is_connected():
        await client.connect()
    try:
        await client.sign_in(req.phone, req.code, phone_code_hash=req.phone_code_hash)
        return {"ok": True, "message": "Muvaffaqiyatli ulandi"}
    except SessionPasswordNeededError:
        if req.password:
            try:
                await client.sign_in(password=req.password)
                return {"ok": True, "message": "2FA bilan muvaffaqiyatli ulandi"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"2FA xatosi: {e}")
        else:
            raise HTTPException(status_code=401, detail="2FA paroli talab qilinadi")
    except PhoneCodeInvalidError:
        raise HTTPException(status_code=400, detail="Tasdiqlash kodi noto'g'ri")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/bots")
async def get_bots():
    return load_bots()

@app.post("/api/bots")
async def add_bot(task: BotTask):
    bots = load_bots()
    bots.append(task.dict())
    save_bots(bots)
    return {"ok": True, "bots": bots}

@app.delete("/api/bots/{index}")
async def delete_bot(index: int):
    bots = load_bots()
    if 0 <= index < len(bots):
        bots.pop(index)
        save_bots(bots)
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Bot topilmadi")

async def run_bot_cycle_task():
    if not await client.is_user_authorized():
        logging.warning("Foydalanuvchi hali ulanmagan.")
        return

    bots = load_bots()
    logging.info(f"Avtomatik sikl boshlandi. Jami botlar: {len(bots)}")
    for b in bots:
        try:
            uname = b["username"]
            cmd = b.get("command", "/start")
            btn_txt = b.get("button_text")

            logging.info(f"Botga yuborilmoqda: {uname} -> {cmd}")
            await client.send_message(uname, cmd)
            await asyncio.sleep(3.0)

            messages = await client.get_messages(uname, limit=2)
            for msg in messages:
                if msg.buttons and btn_txt:
                    for row in msg.buttons:
                        for button in row:
                            if btn_txt.lower() in button.text.lower():
                                await asyncio.sleep(random.uniform(1.5, 3.0))
                                await button.click()
                                logging.info(f"Tugma bosildi: {button.text}")
                                break
            await asyncio.sleep(random.uniform(4.0, 8.0))
        except Exception as e:
            logging.error(f"Botda xatolik: {e}")

@app.post("/api/run-now")
async def run_now(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_bot_cycle_task)
    return {"ok": True, "message": "Avtomatik vazifalar fonda ishga tushirildi"}

# Statik fayllarni ulash
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.py:app", host="0.0.0.0", port=8000, reload=True)
