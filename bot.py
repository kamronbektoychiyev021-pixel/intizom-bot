import requests
import time
import json
import sqlite3
from datetime import datetime

# ================= CONFIG =================
TOKEN = "8786803798:AAF8LAeHpccjJozrPfeSkA81a5vy84KuvnU"
URL = f"https://api.telegram.org/bot{TOKEN}"

CHANNEL_NAME = "@nuriddinovic_m"
CHANNEL_LINK = "https://t.me/nuriddinovic_m"

DAILY_TASK = "📚 Bugungi challenge: 30 min English reading + 10 vocab"

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
    last_day TEXT
)
""")
conn.commit()

# ================= HELPERS =================
def today():
    return datetime.now().strftime("%Y-%m-%d")

def send(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    requests.get(URL + "/sendMessage", params=data)

def get_name(msg):
    user = msg["from"]
    return "@" + user.get("username") if user.get("username") else user.get("first_name", "User")

# ================= USER =================
def get_user(user_id, name=None):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    data = cur.fetchone()

    if not data:
        cur.execute("""
            INSERT INTO users (user_id, name, score, task, streak, last_day)
            VALUES (?, ?, 0, '', 0, '')
        """, (user_id, name))
        conn.commit()
        return {"name": name, "score": 0, "task": "", "streak": 0, "last_day": ""}

    return {
        "name": data[1],
        "score": data[2],
        "task": data[3],
        "streak": data[4],
        "last_day": data[5]
    }

def update_score(user_id, points):
    cur.execute("UPDATE users SET score = score + ? WHERE user_id=?", (points, user_id))
    conn.commit()

def update_task(user_id, task):
    cur.execute("UPDATE users SET task=? WHERE user_id=?", (task, user_id))
    conn.commit()

def update_streak(user_id):
    u = get_user(user_id)

    if u["last_day"] != today():
        new_streak = u["streak"] + 1 if u["last_day"] else 1

        cur.execute("""
            UPDATE users SET streak=?, last_day=?
            WHERE user_id=?
        """, (new_streak, today(), user_id))

        conn.commit()

# ================= KEYBOARD =================
def keyboard():
    return {
        "keyboard": [
            [{"text": "🚀 Start"}, {"text": "📝 Challenge"}],
            [{"text": "🔥 Done"}, {"text": "🏆 Leaderboard"}]
        ],
        "resize_keyboard": True
    }

def done_btn():
    return {
        "inline_keyboard": [
            [{"text": "☑️ Done", "callback_data": "done"}]
        ]
    }

# ================= BOT LOOP =================
last_update = 0
print("BOT STARTED...")

while True:
    res = requests.get(URL + "/getUpdates", params={
        "offset": last_update + 1
    }).json()

    for upd in res.get("result", []):
        last_update = upd["update_id"]

        # ========== MESSAGE ==========
        if "message" in upd:
            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")
            name = get_name(msg)

            user = get_user(chat_id, name)

            # START
            if text == "🚀 Start":
                send(chat_id,
                    f"🚀 Xush kelibsiz {user['name']}!\n\n"
                    f"📢 {@nuriddinovic-m}\n{https://t.me/nuriddinovic_m}\n\n"
                    f"📅 Bugungi task:\n{DAILY_TASK}",
                    keyboard()
                )

            # CHALLENGE
            elif text == "📝 Challenge":
                send(chat_id, "📝 Vazifani yozib yuboring:")

            # SAVE TASK
            elif text not in ["🚀 Start", "📝 Challenge", "🔥 Done", "🏆 Leaderboard"]:
                update_task(chat_id, text)
                send(chat_id,
                    f"📋 Task saqlandi:\n{text}\n\nTugatdingizmi?",
                    done_btn()
                )
