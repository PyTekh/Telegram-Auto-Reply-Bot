import os
from telethon import TelegramClient, events
from telethon.tl.types import UserStatusOnline
from datetime import datetime, timedelta, date
import pytz
import asyncio
from dotenv import load_dotenv

# ----------------- ЗАГРУЗКА .env -----------------
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

if not api_id or not api_hash:
    raise ValueError("API_ID или API_HASH не найдены в .env файле")

# ----------------- НАСТРОЙКИ -----------------
TIMEZONE = "Asia/Tashkent"
WORK_START = 9
WORK_END = 18
WEEKENDS = [5, 6]  # Суббота, воскресенье
RESET_AFTER = timedelta(hours=1)

# ----------------- ПРАЗДНИКИ -----------------
HOLIDAYS = [
    date(2026, 1, 1),   # Новый год
    date(2026, 3, 8),    # Международный женский день
    date(2026, 3, 9),    # Перенос выходного дня
    date(2026, 3, 21),   # Навруз
    date(2026, 3, 22),   # Навруз (дополнительный выходной)
    date(2026, 5, 1),    # День труда
    date(2026, 5, 9),    # День памяти и почестей
    date(2026, 5, 25),   # Курбан Хаит
    date(2026, 9, 1),    # День независимости
    date(2026, 12, 8),   # День Конституции
]

# ----------------- ОТПУСК -----------------
START_VAC = date(2026, 11, 4)
END_VAC = date(2026, 11, 23)

# ----------------- СООБЩЕНИЯ -----------------
OFFTIME_TEXT = (
    "Assalomu alaykum! "
    "Hozir men tarmoqda emasman. "
    "Yaqin ish vaqti ichida sizga albatta javob beraman.\n"
    "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
    "Здравствуйте! "
    "Сейчас я не в сети. "
    "В ближайшее рабочее время я обязательно вам отвечу.\n"
)

WEEKEND_TEXT = (
    "Assalomu alaykum! "
    "Bugun dam olish kuni. "
    "Ish vaqtida men bilan dushanbadan jumagacha, 09:00-18:00 bog‘laning.\n"
    "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
    "Здравствуйте! "
    "Сегодня выходной день. "
    "Свяжитесь со мной в рабочее время с понедельника по пятницу, 09:00-18:00.\n" 
)

NIGHT_TEXT = (
    "Assalomu alaykum! "
    "IT xizmatning ish vaqti: dushanbadan jumagacha, 09:00-18:00. "
    "Ish vaqtida men bilan bog‘laning.\n"
    "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
    "Здравствуйте! " 
    "Рабочее время ИТ-службы: с понедельника по пятницу, 09:00-18:00. " 
    "Свяжитесь со мной в рабочее время.\n"
)

VACATION_TEXT = (
    "Assalomu alaykum! "
    "Hozir men ta'tildaman. "
    "Ishga qaytgach, albatta sizga javob beraman.\n"
    "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
    "Здравствуйте! "
    "Сейчас я в отпуске. "
    "После возвращения на работу обязательно отвечу.\n"
)

# ----------------- КЛИЕНТ -----------------
client = TelegramClient("session", api_id, api_hash)

reply_data = {}

# ----------------- ЛОГИКА ВЫБОРА СООБЩЕНИЯ -----------------
def get_reply_text():
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)

    if START_VAC <= now.date() <= END_VAC:
        return VACATION_TEXT

    if now.date() in HOLIDAYS or now.weekday() in WEEKENDS:
        return WEEKEND_TEXT

    if WORK_START <= now.hour < WORK_END:
        return OFFTIME_TEXT

    return NIGHT_TEXT

# ----------------- ОБРАБОТЧИК -----------------
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private or event.out:
        return

    me = await client.get_me()
    if isinstance(me.status, UserStatusOnline):
        return

    sender = await event.get_sender()
    user_id = sender.id

    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)

    if user_id in reply_data:
        if now - reply_data[user_id]["last_reply"] >= RESET_AFTER:
            reply_data[user_id] = {"count": 0, "last_reply": now}

    if reply_data.get(user_id, {}).get("count", 0) >= 2:
        return

    await event.reply(get_reply_text())

    reply_data[user_id] = {
        "count": reply_data.get(user_id, {}).get("count", 0) + 1,
        "last_reply": now
    }

# ----------------- ЗАПУСК -----------------
async def main():
    await client.start()
    await client.run_until_disconnected()

asyncio.run(main())