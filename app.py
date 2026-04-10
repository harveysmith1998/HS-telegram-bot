from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "bot8755949206:AAG_6J4Vx7YfHv-yg_eA1t_AlIOQKX3hsag"
CHAT_ID = "Chat id-1003787596424"

@app.route("/", methods=["GET", "POST"])
def home():
    print("🔥 REQUEST RECEIVED")

    try:
        data = request.get_data(as_text=True)
        print("📩 DATA:", data)

        # Send to Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": f"📡 Alert:\n{data}"
        })

        return "OK", 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return "Error", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
