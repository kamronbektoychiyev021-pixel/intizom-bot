import requests
import time
import json
import sqlite3
from datetime import datetime

# ================= CONFIG =================
TOKEN = "SENING_BOT_TOKEN"
URL = f"https://api.telegram.org/bot{TOKEN}"

CHANNEL_NAME = "nuriddinovic_m"
CHANNEL_LINK = "https://t.me/nuriddinovic_m"

ADMIN_ID = 123456789  # <-- o'zingni ID qo'y

DAILY_TASK = "📚 30 min English + 10 vocab"

# ================= DATABASE =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    score INTEGER DEFAULT 0,
    task TEXT,
    streak INTEGER DEFAULT 0,
    last_day TEXT,
    ref_by INTEGER
)
""")
conn.commit()

# ================= HELPERS =================
def today():
    return datetime.now().strftime("%Y-%m-%d")

def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.get(URL + "/sendMessage", params=data)

def kb():
    return {
        "keyboard": [
            [{"text": "🚀 Start"}, {"text": "📝 Challenge"}],
            [{"text": "🔥 Done"}, {"text": "🏆 Leaderboard"}],
            [{"text": "👤 Profile"}]
        ],
        "resize_keyboard": True
    }

# ================= USER =================
def get_user(user_id, name):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    data = cur.fetchone()

    if not data:
        cur.execute("""
            INSERT INTO users (user_id, name, score, task, streak, last_day, ref_by)
            VALUES (?, ?, 0, '', 0, '', 0)
        """, (user_id, name))
        conn.commit()
        return {"name": name, "score": 0, "task": "", "streak": 0, "last_day": "", "ref_by": 0}

    return {
        "name": data[1],
        "score": data[2],
        "task": data[3],
        "streak": data[4],
        "last_day": data[5],
        "ref_by": data[6]
    }

def add_score(user_id, points):
    cur.execute("UPDATE users SET score = score + ? WHERE user_id=?", (points, user_id))
    conn.commit()

def save_task(user_id, task):
    cur.execute("UPDATE users SET task=? WHERE user_id=?", (task, user_id))
    conn.commit()

def update_streak(user_id):
    u = get_user(user_id, "")
    if u["last_day"] != today():
        new = u["streak"] + 1 if u["last_day"] else 1
        cur.execute("UPDATE users SET streak=?, last_day=? WHERE user_id=?", (new, today(), user_id))
        conn.commit()

# ================= BOT =================
last_update = 0
print("BOT STARTED...")

while True:
    try:
        res = requests.get(URL + "/getUpdates", params={"offset": last_update + 1}).json()

        for upd in res.get("result", []):
            last_update = upd["update_id"]

            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")
            name = msg["from"].get("first_name", "User")

            user = get_user(chat_id, name)

            # ================= START =================
            if text.startswith("🚀 Start"):
                send(chat_id,
                    f"🚀 Welcome {user['name']}!\n\n"
                    f"📢 @{CHANNEL_NAME}\n{CHANNEL_LINK}\n\n"
                    f"📅 Task:\n{DAILY_TASK}",
                    kb()
                )

            # ================= CHALLENGE =================
            elif text == "📝 Challenge":
                send(chat_id, "📝 Send your task:")

            # ================= SAVE TASK =================
            elif text not in ["🚀 Start", "📝 Challenge", "🔥 Done", "🏆 Leaderboard", "👤 Profile"]:
                save_task(chat_id, text)
                send(chat_id, f"📋 Saved:\n{text}", kb())

            # ================= DONE =================
            elif text == "🔥 Done":
                add_score(chat_id, 10)
                update_streak(chat_id)

                u = get_user(chat_id, name)

                send(chat_id,
