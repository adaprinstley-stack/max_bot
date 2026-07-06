from fastapi import FastAPI, Request
import requests

app = FastAPI()

# 🔐 ТОКЕН MAX (ОБЯЗАТЕЛЬНО ЗАМЕНИ)
TOKEN = "PASTE_YOUR_MAX_TOKEN"
BASE_URL = "https://platform-api.max.ru"


# ----------------------------
# 💬 отправка сообщения (БЕЗ ПАДЕНИЙ)
# ----------------------------
def send_message(user_id: str, text: str):
    if not user_id:
        print("⚠️ Нет user_id")
        return

    url = f"{BASE_URL}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": str(user_id),
        "text": text,
        "attachments": []
    }

    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
    except Exception as e:
        print("SEND ERROR:", e)


# ----------------------------
# 📊 тест выгорания
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

# ⚠️ временное хранилище (для демо)
user_state = {}


def get_result(score):
    if score <= 4:
        return f"🟢 Низкий риск выгорания ({score})\nБерегите ресурс и отдыхайте."
    elif score <= 7:
        return f"🟡 Средний риск выгорания ({score})\nСтоит снизить нагрузку."
    else:
        return f"🔴 Высокий риск выгорания ({score})\nВажно подумать о восстановлении и поддержке."


# ----------------------------
# 📩 WEBHOOK MAX
# ----------------------------
@app.post("/webhook")
async def webhook(request: Request):

    try:
        data = await request.json()
        print("INCOMING:", data)
    except Exception as e:
        print("BAD REQUEST:", e)
        return {"ok": True}

    if data.get("update_type") != "message_created":
        return {"ok": True}

    msg = data.get("message") or {}

    user_id = msg.get("user_id")
    text = (msg.get("text") or "").strip().lower()

    if not user_id or not text:
        return {"ok": True}

    # ---------------- START ----------------
    if text == "/start":
        user_state[user_id] = {"i": 0, "score": 0}
        send_message(user_id, "Привет! Напиши «тест» чтобы начать.")
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
