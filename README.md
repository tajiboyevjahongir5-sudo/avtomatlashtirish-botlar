# ⚡ Telegram Avtomatlashtirish Bot & Web App

Ushbu tizim Telegram bot orqali ochiladigan zamonaviy Web App (Mini App) bo'lib, shaxsiy akkaunt nomidan turli botlarga kirish, kunlik bonuslarni yig'ish va inline tugmalarni avtomatik bosish imkoniyatini beradi.

---

## 🚀 Texnologiyalar
- **Backend:** FastAPI (Python 3.10+)
- **Telegram Klient:** Telethon (MTProto API)
- **Telegram Bot:** Aiogram 3.x
- **Frontend:** Telegram Web App (HTML5 / Vanilla JS / CSS3)

---

## ⚙️ O'rnatish va Sozlash

### 1. Repozitoriyani yuklab olish va paketlarni o'rnatish
```bash
git clone https://github.com/tajiboyevjahongir5-sudo/avtomatlashtirish-botlar.git
cd avtomatlashtirish-botlar
python -m venv venv
# Windows uchun:
venv\Scripts\activate
# Linux/Mac uchun:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Sozlamalar (`.env`)
`.env.example` faylini nusxalab `.env` nomiga o'tkazing va kerakli kalitlarni kiriting:
```ini
API_ID=12345678              # my.telegram.org dan olinadi
API_HASH=your_api_hash_here  # my.telegram.org dan olinadi
BOT_TOKEN=your_bot_token     # @BotFather dan olinadi
WEBAPP_URL=https://...       # Web App manzili (ngrok yoki doimiy domen)
```

### 3. Ishga tushirish

1. **Web App serverini ishga tushirish:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

2. **Telegram botni ishga tushirish:**
```bash
python bot.py
```

3. Agar lokal test qilmoqchi bo'lsangiz, `ngrok` orqali 8000-portni tashqariga chiqaring:
```bash
ngrok http 8000
```
Chiqqan HTTPS manzilni `.env` dagi `WEBAPP_URL` ga yozing.
