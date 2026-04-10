from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "bot8755949206:AAG_6J4Vx7YfHv-yg_eA1t_AlIOQKX3hsag"
CHAT_ID = "-1003787596424"

@app.route('/', methods=['POST'])
def webhook():
    data = request.json

    signal = data.get("signal", "UNKNOWN")
    price = data.get("price", "N/A")

    message = f"{signal} XAUUSD\nEntry: {price}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, json=payload)

    return "OK"

app.run(host='0.0.0.0', port=10000)
