import requests
import time
import json

# ================== CONFIG ==================
TOKEN = "8786803798:AAF8LAeHpccjJozrPfeSkA81a5vy84KuvnU"

CHANNEL_NAME = "@nuriddinovic_m"
CHANNEL_LINK = "https://t.me/your_channel"

URL = f"https://api.telegram.org/bot{TOKEN}"

# ================== DATA ==================
users = {}

# ================== SEND ==================
def send(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    requests.get(URL + "/sendMessage", params=data)

# ================== KEYBOARD ==================
def main_keyboard():
    return {
        "keyboard": [
            [{"text": "🚀 Start"}, {"text": "📝 Challenge"}],
            [{"text": "🔥 Done"}, {"text": "🏆 Leaderboard"}]
        ],
        "resize_keyboard": True
    }

def done_button():
    return {
        "inline_keyboard": [
            [{"text": "☑️ Done", "callback_data": "done_task"}]
        ]
    }

# ================== BOT LOOP ==================
last_update = 0

print("Bot started...")

while True:
    res = requests.get(URL + "/getUpdates", params={
        "offset": last_update + 1
    }).json()

    for upd in res.get("result", []):
        last_update = upd["update_id"]

        # ================= MESSAGE =================
        if "message" in upd:
            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            # -------- START --------
            if text == "🚀 Start":
                if chat_id not in users:
                    users[chat_id] = {"score": 0, "task": ""}

                send(chat_id,
                    f"📢 Botdan foydalanish uchun {CHANNEL_NAME} kanaliga qo‘shiling:\n\n👇",
                    {
                        "inline_keyboard": [
                            [{"text": f"📢 {CHANNEL_NAME}", "url": CHANNEL_LINK}]
                        ]
                    }
                )

            # -------- AFTER JOIN (manual continue) --------
            elif text == "/start":
                if chat_id not in users:
                    users[chat_id] = {"score": 0, "task": ""}

                send(chat_id, "🚀 Xush kelibsiz!", main_keyboard())

            # -------- CHALLENGE --------
            elif text == "📝 Challenge":
                send(chat_id, "📝 Vazifani yozib yuboring:")

            # -------- SAVE TASK --------
            elif chat_id in users and text not in ["🚀 Start", "📝 Challenge", "🔥 Done", "🏆 Leaderboard"]:
                users[chat_id]["task"] = text
                send(chat_id,
                    f"📋 Task saqlandi:\n{text}\n\nTugatdingizmi?",
                    done_button()
                )

            # -------- DONE --------
            elif text == "🔥 Done":
                if chat_id in users:
                    users[chat_id]["score"] += 10
                    send(chat_id,
                        f"🔥 +10 ball!\n🏆 Jami: {users[chat_id]['score']}",
                        main_keyboard()
                    )

            # -------- LEADERBOARD --------
            elif text == "🏆 Leaderboard":
                text_out = "🏆 TOP USERLAR:\n\n"

                sorted_users = sorted(users.items(), key=lambda x: x[1]["score"], reverse=True)

                for i, (uid, data) in enumerate(sorted_users[:5], 1):
                    text_out += f"{i}. User {uid} - {data['score']} ball\n"

                send(chat_id, text_out, main_keyboard())

        # ================= INLINE =================
        if "callback_query" in upd:
            cq = upd["callback_query"]
            chat_id = cq["message"]["chat"]["id"]

            if cq["data"] == "done_task":
                if chat_id in users:
                    users[chat_id]["score"] += 10

                    requests.get(URL + "/answerCallbackQuery", params={
                        "callback_query_id": cq["id"]
                    })

                    send(chat_id,f"☑️ Task completed!\n🔥 +10 ball\n🏆 Jami: {users[chat_id]['score']}",
                        main_keyboard()
                    )

    time.sleep(2)
