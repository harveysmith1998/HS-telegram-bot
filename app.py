from flask import Flask, request
import requests
import os

app = Flask(__name__)

# 🔐 Use environment variables (recommended)
BOT_TOKEN = os.environ.get("8755949206:AAG_6J4Vx7YfHv-yg_eA1t_AlIOQKX3hsag")
CHAT_ID = os.environ.get("-1003787596424")

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("🔥 RECEIVED:", data)

    if not data:
        return "No data", 400

    # 📊 Extract values safely
    signal = data.get("signal", "")
    price = data.get("price", "")
    sl = data.get("sl", "")
    tp1 = data.get("tp1", "")
    tp2 = data.get("tp2", "")
    symbol = data.get("symbol", "XAUUSD")

    # 🎯 Build message
    if signal == "BUY":
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🟢 <b>BUY NOW</b>\n\n"
            f"<b>💰 Price:</b> <code>{price}</code>\n"
            f"<b>🛑 SL:</b> <code>{sl}</code>\n"
            f"<b>🎯 TP1:</b> <code>{tp1}</code>\n"
            f"<b>🚀 TP2:</b> <code>{tp2}</code>"
        )

    elif signal == "SELL":
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🔴 <b>SELL NOW</b>\n\n"
            f"<b>💰 Price:</b> <code>{price}</code>\n"
            f"<b>🛑 SL:</b> <code>{sl}</code>\n"
            f"<b>🎯 TP1:</b> <code>{tp1}</code>\n"
            f"<b>🚀 TP2:</b> <code>{tp2}</code>"
        )

    elif signal == "TP1 HIT":
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🎯 <b>TP1 HIT</b>\n\n"
            f"<b>💰 Price:</b> <code>{price}</code>"
        )

    elif signal == "TP2 HIT":
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🚀 <b>TP2 HIT</b>\n\n"
            f"<b>💰 Price:</b> <code>{price}</code>"
        )

    elif signal == "SL HIT":
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"❌ <b>STOP LOSS HIT</b>\n\n"
            f"<b>💰 Price:</b> <code>{price}</code>"
        )

    else:
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"⚪ <b>SIGNAL</b>\n\n"
            f"<b>💰 Price:</b> <code>{price}</code>"
        )

    # 📤 Send to Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        print("📩 TELEGRAM RESPONSE:", r.text)
    except Exception as e:
        print("❌ ERROR SENDING:", e)

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
