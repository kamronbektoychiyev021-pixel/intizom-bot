import requests
import time
import json
import sqlite3

# ================= CONFIG =================
TOKEN = "8786803798:AAF8LAeHpccjJozrPfeSkA81a5vy84KuvnU"
URL = f"https://api.telegram.org/bot{TOKEN}"

CHANNEL = "nuriddinovic_m"
CHANNEL_LINK = "https://t.me/nuriddinovic_m"

# ================= DB =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
name TEXT,
score INTEGER DEFAULT 0
)
""")
conn.commit()

# ================= FUNCTIONS =================
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
            [{"text": "👤 My Score"}]
        ],
        "resize_keyboard": True
    }

def get_user(uid, name):
    cur.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    data = cur.fetchone()

    if not data:
        cur.execute("INSERT INTO users VALUES (?, ?, 0)", (uid, name))
        conn.commit()
        return 0

    return data[2]

def add_score(uid, points):
    cur.execute("UPDATE users SET score = score + ? WHERE user_id=?", (points, uid))
    conn.commit()

# ================= BOT LOOP =================
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
            name = msg["from"].get("first_name", "User")

            score = get_user(chat_id, name)

            # ================= START =================
            if text == "🚀 Start":
                send(chat_id,
                    f"🚀 Welcome {name}!\n"
                    f"📢 Channel: {CHANNEL_LINK}",
                    kb()
                )

            # ================= CHALLENGE =================
            elif text == "📝 Challenge":
                send(chat_id, "📝 Send your task", kb())

            # ================= DONE =================
            elif text == "🔥 Done":
                add_score(chat_id, 10)
                send(chat_id, "🔥 +10 points added!", kb())

            # ================= LEADERBOARD =================
            elif text == "🏆 Leaderboard":
                cur.execute("SELECT name, score FROM users ORDER BY score DESC LIMIT 5")
                top = cur.fetchall()

                txt = "🏆 TOP USERS:\n\n"
                for i, (n, s) in enumerate(top, 1):
                    txt += f"{i}. {n} - {s}\n"

                send(chat_id, txt, kb())

            # ================= MY SCORE =================
            elif text == "👤 My Score":
                cur.execute("SELECT score FROM users WHERE user_id=?", (chat_id,))
                s = cur.fetchone()[0]
                send(chat_id, f"👤 {name}\n🏆 Score: {s}", kb())

        time.sleep(1)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(3)
