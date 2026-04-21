import requests
import time
import json
import sqlite3
from datetime import datetime

# ================= CONFIG =================
TOKEN = "8786803798:AAF8LAeHpccjJozrPfeSkA81a5vy84KuvnU"
URL = f"https://api.telegram.org/bot{TOKEN}"

CHANNEL = "nuriddinovic_m"
CHANNEL_LINK = "https://t.me/nuriddinovic_m"

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    score INTEGER DEFAULT 0,
    task TEXT,
    joined INTEGER DEFAULT 0
)
""")
conn.commit()

# ================= HELPERS =================
def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.get(URL + "/sendMessage", params=data)

def board():
    return {
        "keyboard": [
            [{"text": "🚀 Start"}, {"text": "📝 Challenge"}],
            [{"text": "🔥 Done"}, {"text": "🏆 Leaderboard"}],
            [{"text": "👤 My Score"}]
        ],
        "resize_keyboard": True
    }

# ================= DB =================
def get_user(uid, name, username):
    cur.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    data = cur.fetchone()

    if not data:
        cur.execute(
            "INSERT INTO users (user_id, name, username, score, task, joined) VALUES (?, ?, ?, 0, '', 0)",
            (uid, name, username)
        )
        conn.commit()
        return {"score": 0, "joined": 0}

    return {"score": data[3], "joined": data[5]}

def add_score(uid, point):
    cur.execute("UPDATE users SET score = score + ? WHERE user_id=?", (point, uid))
    conn.commit()

def set_task(uid, task):
    cur.execute("UPDATE users SET task=? WHERE user_id=?", (task, uid))
    conn.commit()

def check_join(uid):
    u = get_user(uid, "", "")
    return u["joined"] == 1

# ================= BOT LOOP =================
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
            username = msg["from"].get("username", "no_username")

            user = get_user(chat_id, name, username)

            # ================= START =================
            if text == "🚀 Start":
                send(chat_id,
                    f"🚀 Welcome {name}!\n\n"
                    f"📢 Join channel first:\n{CHANNEL_LINK}\n\n"
                    f"Then use bot 👇",
                    board()
                )

            # ================= CHANNEL CHECK =================
            elif text == "/join":
                cur.execute("UPDATE users SET joined=1 WHERE user_id=?", (chat_id,))
                conn.commit()
                send(chat_id, "✅ You joined channel successfully!", board())

            # ================= CHALLENGE =================
            elif text == "📝 Challenge":
                if not check_join(chat_id):
                    send(chat_id, "❌ First join channel then /join")
                else:
                    send(chat_id, "📝 Send your challenge task:")

            # ================= SAVE TASK =================
            elif text not in ["🚀 Start", "📝 Challenge", "🔥 Done", "🏆 Leaderboard", "👤 My Score"]:
                set_task(chat_id, text)
                send(chat_id, "📋 Task saved!\nNow press DONE 🔥", board())

            # ================= DONE =================
            elif text == "🔥 Done":
                add_score(chat_id, 10)
                send(chat_id, "🔥 +10 score added!", board())

            # ================= LEADERBOARD =================
            elif text == "🏆 Leaderboard":
                cur.
