from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "8755949206:AAG_6J4Vx7YfHv-yg_eA1t_AlIOQKX3hsag"
CHAT_ID = "-1003787596424"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("🔥 RECEIVED:", data)

if data:
    signal = data.get("signal", "")
    price = data.get("price", "")
    sl = data.get("sl", "")
    tp1 = data.get("tp1", "")
    tp2 = data.get("tp2", "")

    if signal == "BUY":
        header = "🟢 BUY NOW"
    elif signal == "SELL":
        header = "🔴 SELL NOW"
    else:
        header = "⚪ SIGNAL"

    message = (
        f"XAUUSD {header}\n"
        f"PRICE {price}\n"
        f"SL {sl}\n"
        f"TP1 {tp1}\n"
        f"TP2 {tp2}"
    )

    

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        r = requests.post(url, json=payload)
        print("📤 TELEGRAM RESPONSE:", r.text)

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
