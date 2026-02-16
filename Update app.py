from flask import Flask, request
import requests
import os
import math

# =========================
# CONFIG
# =========================
TOKEN = os.environ.get("TOKEN")
app = Flask(__name__)

user_data = {}

# =========================
# TELEGRAM SEND FUNCTION
# =========================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# =========================
# RCC FUNCTION (Example)
# =========================
def analyze_singly(b, d, Ast, fck, fy):
    xu = (0.87 * fy * Ast) / (0.36 * fck * b)
    Mu = 0.87 * fy * Ast * d * (1 - (Ast * fy)/(b * d * fck))
    return round(xu,2), round(Mu/10**6,2)

# =========================
# WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text","")

    if text == "/start":
        send_message(chat_id, "RCC AI Bot Online 🚀\nSend: b,d,Ast,fck,fy")

    else:
        try:
            params = [float(x.strip()) for x in text.split(",")]
            if len(params) != 5:
                raise ValueError

            xu, Mu = analyze_singly(*params)

            result = f"""
Results:
xu = {xu} mm
Mu = {Mu} kNm
"""
            send_message(chat_id, result)

        except:
            send_message(chat_id, "Use format:\n230,450,942,20,415")

    return "ok"

# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return "RCC Bot Running!"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
