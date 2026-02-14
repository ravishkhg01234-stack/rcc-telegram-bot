from flask import Flask, request
import requests

TOKEN = "YOUR_NEW_TELEGRAM_TOKEN"

app = Flask(__name__)

# Temporary user storage
user_data = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" not in data:
        return "ok"
    
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if chat_id not in user_data:
        user_data[chat_id] = {"step": 0}

    step = user_data[chat_id]["step"]

    try:
        if step == 0:
            user_data[chat_id]["step"] = 1
            reply = "Enter width of beam (b) in mm:"

        elif step == 1:
            user_data[chat_id]["b"] = float(text)
            user_data[chat_id]["step"] = 2
            reply = "Enter effective depth (d) in mm:"

        elif step == 2:
            user_data[chat_id]["d"] = float(text)
            user_data[chat_id]["step"] = 3
            reply = "Enter concrete strength fck (N/mm²):"

        elif step == 3:
            user_data[chat_id]["fck"] = float(text)
            user_data[chat_id]["step"] = 4
            reply = "Enter steel strength fy (N/mm²):"

        elif step == 4:
            user_data[chat_id]["fy"] = float(text)
            user_data[chat_id]["step"] = 5
            reply = "Enter steel area Ast (mm²):"

        elif step == 5:
            user_data[chat_id]["ast"] = float(text)

            b = user_data[chat_id]["b"]
            d = user_data[chat_id]["d"]
            fck = user_data[chat_id]["fck"]
            fy = user_data[chat_id]["fy"]
            ast = user_data[chat_id]["ast"]

            if fy >= 500:
                coeff = 0.46
            elif fy >= 415:
                coeff = 0.48
            else:
                coeff = 0.53

            xu_max = coeff * d
            xu = (0.87 * fy * ast) / (0.36 * fck * b)

            if xu <= xu_max:
                status = "UNDER-REINFORCED"
                mu = 0.87 * fy * ast * (d - 0.42 * xu)
            else:
                status = "OVER-REINFORCED"
                mu = 0.36 * (xu_max / d) * (1 - 0.42 * (xu_max / d)) * fck * b * (d**2)

            reply = (
                f"--- RCC REPORT ---\n"
                f"Beam: {b} x {d} mm\n"
                f"Status: {status}\n"
                f"xu = {xu:.2f} mm\n"
                f"xu_max = {xu_max:.2f} mm\n"
                f"Mu = {mu/10**6:.2f} kNm"
            )

            user_data[chat_id] = {"step": 0}

        else:
            reply = "Type anything to start RCC calculation."

    except:
        reply = "Invalid input. Please enter numeric value."
        user_data[chat_id]["step"] = 0

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": reply}
    )

    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
