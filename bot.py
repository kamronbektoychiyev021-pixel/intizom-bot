import sqlite3
import requests
import time

TOKEN = "8786803798:AAF8LAeHpccjJozrPfeSkA81a5vy84KuvnU"
URL = f"https://api.telegram.org/bot{TOKEN}"

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(user_id):
    cur.execute("SELECT score FROM users WHERE user_id=?", (user_id,))
    data = cur.fetchone()
    if not data:
        cur.execute("INSERT INTO users (user_id, score) VALUES (?, 0)", (user_id,))
        conn.commit()
        return 0
    return data[0]

def add_score(user_id, points):
    cur.execute("UPDATE users SET score = score + ? WHERE user_id=?", (points, user_id))
    conn.commit()

def send(chat_id, text):
    requests.get(URL + "/sendMessage", params={"chat_id": chat_id, "text": text})

last_update = 0

print("Bot started...")

while True:
    res = requests.get(URL + "/getUpdates", params={"offset": last_update + 1}).json()

    for upd in res.get("result", []):
        last_update = upd["update_id"]
        msg = upd.get("message")
        if not msg:
            continue

        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            get_user(chat_id)
            send(chat_id, "🚀 Intizom botga xush kelibsiz!")

        elif text == "/done":
            add_score(chat_id, 10)
            score = get_user(chat_id)
            send(chat_id, f"🔥 +10 ball\n🏆 Jami: {score}")

        elif text == "/leaderboard":
            cur.execute("SELECT user_id, score FROM users ORDER BY score DESC LIMIT 5")
            rows = cur.fetchall()

            text_out = "🏆 TOP USERLAR:\n\n"
            for i, r in enumerate(rows, 1):
                text_out += f"{i}. {r[0]} - {r[1]} ball\n"

            send(chat_id, text_out)

    time.sleep(2)
