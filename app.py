from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ===== ENV VARIABLES =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")

# ===== TRADE STATE STORAGE =====
trades = {}

# ===== PIP CALCULATION =====
# $1 move = 10 pips
PIPS_PER_DOLLAR  = 10
BE_ADVISORY_PIPS = 70
REDUCE_RISK_PIPS = 100

def calc_pips(entry, current_price, side):
    if not entry or not current_price:
        return 0
    if side == "BUY":
        return round((float(current_price) - float(entry)) * PIPS_PER_DOLLAR)
    else:
        return round((float(entry) - float(current_price)) * PIPS_PER_DOLLAR)

# ===== SEND TELEGRAM =====
def send_telegram(message, reply_to_id=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    if reply_to_id:
        payload["reply_to_message_id"] = reply_to_id
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("TELEGRAM RESPONSE:", r.text)
        data = r.json()
        if data.get("ok"):
            return data["result"]["message_id"]
        return None
    except Exception as e:
        print("ERROR SENDING:", e)
        return None

# ===== HEALTH CHECK =====
@app.route("/", methods=["GET"])
def health():
    return "OK", 200

# ===== WEBHOOK =====
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("RECEIVED:", data)

    if not data:
        return "No data", 400

    # Extract values
    signal    = str(data.get("signal", "")).strip().upper()
    price     = data.get("price") or data.get("entry", "")
    sl        = data.get("sl", "")
    tp1       = data.get("tp1", "")
    tp2       = data.get("tp2", "")
    tp3       = data.get("tp3", "")
    tp4       = data.get("tp4", "")
    tp5       = data.get("tp5", "")
    zone_low  = data.get("zone_low", "")
    zone_high = data.get("zone_high", "")
    symbol    = data.get("symbol", "XAUUSD")
    strategy  = data.get("strategy", "HS BOT")

    print("SIGNAL:", signal)

    trade_key = f"{symbol}_{strategy}"
    trade     = trades.get(trade_key, {})
    reply_id  = trade.get("message_id")
    entry     = trade.get("entry", 0)
    side      = trade.get("side", "BUY")

    # ==========================
    # BUY SIGNAL
    # ==========================
    if "BUY" in signal and "HIT" not in signal:
        tp5_line = f"💎 TP5: <code>{tp5}</code>\n" if tp5 else ""
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🔥 <b>BUY NOW</b>\n\n"
            f"📍 <b>Signal Price:</b> <code>{price}</code>\n"
            f"📍 <b>Entry Zone:</b> <code>{zone_low} - {zone_high}</code>\n"
            f"🔴 <b>SL:</b> <code>{sl}</code>\n\n"
            f"🎯 TP1: <code>{tp1}</code>\n"
            f"🎯 TP2: <code>{tp2}</code>\n"
            f"🎯 TP3: <code>{tp3}</code>\n"
            f"🚀 TP4: <code>{tp4}</code>\n"
            f"{tp5_line}"
            f"\n⚠️ <i>Make risk free once in profit and trail stop loss up ⚠️</i>\n\n"
            f"🔄 <i>Be patient and wait for price to come back to the zone before entering for a better risk/reward</i>"
        )
        msg_id = send_telegram(message)
        if msg_id:
            trades[trade_key] = {
                "message_id": msg_id,
                "entry": float(price) if price else 0,
                "side": "BUY",
                "be_advisory_sent": False,
                "reduce_risk_sent": False
            }
        return "OK", 200

    # ==========================
    # SELL SIGNAL
    # ==========================
    elif "SELL" in signal and "HIT" not in signal:
        tp5_line = f"💎 TP5: <code>{tp5}</code>\n" if tp5 else ""
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🔴 <b>SELL NOW</b>\n\n"
            f"📍 <b>Signal Price:</b> <code>{price}</code>\n"
            f"📍 <b>Entry Zone:</b> <code>{zone_low} - {zone_high}</code>\n"
            f"🔴 <b>SL:</b> <code>{sl}</code>\n\n"
            f"🎯 TP1: <code>{tp1}</code>\n"
            f"🎯 TP2: <code>{tp2}</code>\n"
            f"🎯 TP3: <code>{tp3}</code>\n"
            f"🚀 TP4: <code>{tp4}</code>\n"
            f"{tp5_line}"
            f"\n⚠️ <i>Make risk free once in profit and trail stop loss up ⚠️</i>\n\n"
            f"🔄 <i>Be patient and wait for price to come back to the zone before entering for a better risk/reward</i>"
        )
        msg_id = send_telegram(message)
        if msg_id:
            trades[trade_key] = {
                "message_id": msg_id,
                "entry": float(price) if price else 0,
                "side": "SELL",
                "be_advisory_sent": False,
                "reduce_risk_sent": False
            }
        return "OK", 200

    # ==========================
    # TP HIT HELPER
    # ==========================
    def handle_tp(tp_label, pip_emoji, close_trade=False):
        current_price = float(price) if price else 0
        pips = calc_pips(entry, current_price, side)

        pip_text = f"📈 <b>Pips:</b> <code>+{pips}</code>" if pips > 0 else f"📉 <b>Pips:</b> <code>{pips}</code>"

        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"{pip_emoji} <b>{tp_label}</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>\n"
            f"{pip_text}"
        )
        send_telegram(message, reply_to_id=reply_id)

        # BE advisory after 70 pips
        if pips >= BE_ADVISORY_PIPS and not trade.get("be_advisory_sent"):
            be_message = (
                f"📊 <b>{symbol}</b>\n"
                f"🤖 <b>{strategy}</b>\n\n"
                f"⚠️ <b>MOVE SL TO BREAKEVEN NOW!</b> ⚠️\n\n"
                f"<i>Trade is up {pips} pips — protect your position by moving your Stop Loss to entry price</i>"
            )
            send_telegram(be_message, reply_to_id=reply_id)
            if trade_key in trades:
                trades[trade_key]["be_advisory_sent"] = True

        # Reduce risk advisory after 100 pips
        if pips >= REDUCE_RISK_PIPS and not trade.get("reduce_risk_sent"):
            reduce_message = (
                f"📊 <b>{symbol}</b>\n"
                f"🤖 <b>{strategy}</b>\n\n"
                f"💡 <b>LOOK TO START REDUCING RISK</b>\n\n"
                f"<i>Trade is up {pips} pips — consider closing partial position and trailing your Stop Loss</i>"
            )
            send_telegram(reduce_message, reply_to_id=reply_id)
            if trade_key in trades:
                trades[trade_key]["reduce_risk_sent"] = True

        if close_trade:
            trades.pop(trade_key, None)

    # ==========================
    # TP HITS
    # ==========================
    if "TP1 HIT" in signal:
        handle_tp("TP1 HIT", "🎯")

    elif "TP2 HIT" in signal:
        handle_tp("TP2 HIT", "🚀")

    elif "TP3 HIT" in signal:
        handle_tp("TP3 HIT", "🚀")

    elif "TP4 HIT" in signal:
        current_price = float(price) if price else 0
        pips = calc_pips(entry, current_price, side)
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🚀🚀 <b>TP4 HIT - FULL TARGET REACHED!</b> 🚀🚀\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>\n"
            f"📈 <b>Total Pips:</b> <code>+{pips}</code>"
        )
        send_telegram(message, reply_to_id=reply_id)
        # Don't clear trade yet — TP5 may still hit

    elif "TP5 HIT" in signal:
        current_price = float(price) if price else 0
        pips = calc_pips(entry, current_price, side)
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🤑🤑 <b>TP5 HIT - PRINTING MONEY!</b> 🤑🤑\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>\n"
            f"📈 <b>Total Pips:</b> <code>+{pips}</code>"
        )
        send_telegram(message, reply_to_id=reply_id)
        trades.pop(trade_key, None)
        return "OK", 200

    # ==========================
    # SL HIT
    # ==========================
    elif "SL HIT" in signal:
        current_price = float(price) if price else 0
        pips = calc_pips(entry, current_price, side)

        if pips > 0:
            pip_text = (
                f"📈 <b>Pips at close:</b> <code>+{pips}</code>\n"
                f"<i>⚠️ Should have moved SL to breakeven!</i>"
            )
        else:
            pip_text = f"📉 <b>Loss:</b> <code>{pips} pips</code>"

        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"❌ <b>STOP LOSS HIT</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>\n"
            f"{pip_text}"
        )
        send_telegram(message, reply_to_id=reply_id)
        trades.pop(trade_key, None)
        return "OK", 200

    # ==========================
    # FALLBACK
    # ==========================
    else:
        message = (
            f"📊 <b>{symbol}</b>\n"
            f"🤖 <b>{strategy}</b>\n\n"
            f"🔵 <b>{signal}</b>\n\n"
            f"💰 <b>Price:</b> <code>{price}</code>"
        )
        send_telegram(message, reply_to_id=reply_id)

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
