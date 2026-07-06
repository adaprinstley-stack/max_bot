from fastapi import FastAPI, Request
import requests

app = FastAPI()

# 🔐 ТВОЙ ТОКЕН MAX
TOKEN = "PASTE_YOUR_MAX_TOKEN"
BASE_URL = "https://platform-api.max.ru"


# ----------------------------
# 💬 отправка сообщения
# ----------------------------
def send_message(user_id: str, text: str):
    url = f"{BASE_URL}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": user_id,
        "text": text,
        "attachments": []
    }

    requests.post(url, json=payload, headers=headers)


# ----------------------------
# 📊 тест выгорания (упрощённый)
# ----------------------------
QUESTIONS = [
    "Как часто вы чувствуете усталость на работе?",
    "Есть ли ощущение эмоционального истощения?",
    "Часто ли вы раздражены на работе?"
]

answers = {
    "никогда": 0,
    "редко": 1,
    "иногда": 2,
    "часто": 3,
    "постоянно": 4
}

user_state = {}


def get_result(score):
    if score <= 4:
        return f"🟢 Низкий риск выгорания ({score})"
    elif score <= 7:
        return f"🟡 Средний риск выгорания ({score})"
    else:
        return f"🔴 Высокий риск выгорания ({score})"


# ----------------------------
# 📩 WEBHOOK MAX
# ----------------------------
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("INCOMING:", data)  # 🔥 важно для проверки

    if data.get("update_type") != "message_created":
        return {"ok": True}

    msg = data.get("message", {})
    user_id = msg.get("user_id")
    text = msg.get("text", "").strip().lower()

    # ---------------- START ----------------
    if text == "/start":
        user_state[user_id] = {"i": 0, "score": 0}
        send_message(user_id, "Привет! Напиши 'тест' чтобы начать.")
        return {"ok": True}

    # ---------------- START TEST ----------------
    if text == "тест":
        user_state[user_id] = {"i": 0, "score": 0}
        send_message(user_id, QUESTIONS[0])
        return {"ok": True}

    # ---------------- TEST LOGIC ----------------
    if user_id in user_state:

        state = user_state[user_id]

        if text in answers:
            state["score"] += answers[text]
            state["i"] += 1

            if state["i"] >= len(QUESTIONS):
                result = get_result(state["score"])
                send_message(user_id, result)
                del user_state[user_id]
                return {"ok": True}

            send_message(user_id, QUESTIONS[state["i"]])
            return {"ok": True}

    send_message(user_id, "Напишите /start")
    return {"ok": True}