import requests
import time
import json
import sqlite3
from datetime import datetime

TOKEN = "8786803798:AAF8LAeHpccjJozrPfeSkA81a5vy84KuvnU"
URL = f"https://api.telegram.org/bot{TOKEN}"

CHANNEL = "nuriddinovic_m"
LINK = "https://t.me/nuriddinovic_m"

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

def today():
    return datetime.now().strftime("%Y-%m-%d")

def send(chat_id, text):
    requests.get(URL + "/sendMessage", params={"chat_id": chat_id, "text": text})

def kb():
    return {
        "keyboard": [
            [{"text": "🚀 Start"}, {"text": "📝 Challenge"}],
            [{"text": "🔥 Done"}, {"text": "🏆 Leaderboard"}]
        ],
        "resize_keyboard": True
    }

def get_user(user_id, name):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    data = cur.fetchone()
    if not data:
        cur.execute("INSERT INTO users VALUES (?, ?, 0, '', 0, '')", (user_id, name))
        conn.commit()
        return {"score": 0, "streak": 0}
    return {"score": data[2], "streak": data[4]}

last_update = 0
print("BOT STARTED")

while True:
    try:
        res = requests.get(URL + "/getUpdates", params={"offset": last_update + 1}).json()

        for u in res.get("result", []):
            last_update = u["update_id"]

            if "message" not in u:
                continue

            msg = u["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")
            name = msg["from"]["first_name"]

            user = get_user(chat_id, name)

            if text == "🚀 Start":
                send(chat_id, f"Welcome!\nChannel: @{CHANNEL}\n{LINK}")

            elif text == "📝 Challenge":
                send(chat_id, "Send your task")

            elif text == "🔥 Done":
                cur.execute("UPDATE users SET score = score + 10 WHERE user_id=?", (chat_id,))
                conn.commit()
                send(chat_id, "🔥 +10 points")

            elif text == "🏆 Leaderboard":
                cur.execute("SELECT name, score FROM users ORDER BY score DESC LIMIT 5")
                top = cur.fetchall()

                txt = "TOP USERS:\n"
                for i, t in enumerate(top, 1):
                    txt += f"{i}. {t[0]} - {t[1]}\n"

                send(chat_id, txt)

        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(3)
