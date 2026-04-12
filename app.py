from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ✅ Correct way to get env variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("📩 RECEIVED:", data)

    if not data:
        return "No data", 400

    # ✅ Clean + extract values
    signal = str(data.get("signal", "")).strip().upper()
    price = data.get("price", "")
    sl = data.get("sl", "")
    tp1 = data.get("tp1", "")
    tp2 = data.get("tp2", "")
    symbol = data.get("symbol", "XAUUSD")
    strategy = data.get("strategy", "HS BOT")

    print("📊 SIGNAL:", signal)

    # =========================
    # 🧠 BUILD MESSAGE
    # =========================

    if "BUY" in signal:
        message = (
            f"📈 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🟢 <b>BUY NOW</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>\n"
            f"🛑 <b>SL:</b> <code>{sl}</code>\n"
            f"🎯 <b>TP1:</b> <code>{tp1}</code>\n"
            f"🚀 <b>TP2:</b> <code>{tp2}</code>"
        )

    elif "SELL" in signal:
        message = (
            f"📉 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🔴 <b>SELL NOW</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>\n"
            f"🛑 <b>SL:</b> <code>{sl}</code>\n"
            f"🎯 <b>TP1:</b> <code>{tp1}</code>\n"
            f"🚀 <b>TP2:</b> <code>{tp2}</code>"
        )

    elif "TP1" in signal:
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🎯 <b>TP1 HIT</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>"
        )

    elif "TP2" in signal:
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🚀 <b>TP2 HIT</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>"
        )

    elif "SL" in signal:
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"❌ <b>STOP LOSS HIT</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>"
        )

    else:
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"⚪ <b>{signal}</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>"
        )

    print("📤 Sending message:", message)

    # =========================
    # 📩 SEND TO TELEGRAM
    # =========================

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
