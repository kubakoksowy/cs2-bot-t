from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os, json
from datetime import datetime, timedelta
import pytz

TOKEN = os.environ.get("TOKEN")
TRADES_FILE = "trades.json"
TB_FILE = "tradebans.json"

app = Flask(__name__)

# ===== Telegram Bot Commands =====
def log_trade(update: Update, context: CallbackContext):
    item = " ".join(context.args)
    trades = json.load(open(TRADES_FILE, "r")) if os.path.exists(TRADES_FILE) else []
    trades.append({"item": item, "date": datetime.now().strftime("%Y-%m-%d")})
    json.dump(trades, open(TRADES_FILE, "w"), indent=2)
    update.message.reply_text(f"✅ Logged: {item}")

def tradeban(update: Update, context: CallbackContext):
    skin = " ".join(context.args)
    tz = pytz.timezone("Europe/Warsaw")
    now = datetime.now(tz)
    target_date = (now + timedelta(days=8)).replace(hour=9, minute=0)
    tb = json.load(open(TB_FILE, "r")) if os.path.exists(TB_FILE) else []
    tb.append({"skin": skin, "notify_at": target_date.strftime("%Y-%m-%d %H:%M"), "chat_id": update.message.chat_id})
    json.dump(tb, open(TB_FILE, "w"), indent=2)
    update.message.reply_text(f"⏳ Tradeban set: {target_date.strftime('%Y-%m-%d %H:%M')}")

# ===== Flask API =====
@app.route("/trades")
def trades():
    trades = json.load(open(TRADES_FILE, "r")) if os.path.exists(TRADES_FILE) else []
    return jsonify(trades)

@app.route("/tradebans")
def tradebans():
    tb = json.load(open(TB_FILE, "r")) if os.path.exists(TB_FILE) else []
    return jsonify(tb)

# ===== Start bot in background =====
def start_bot():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("log", log_trade))
    dp.add_handler(CommandHandler("tradeban", tradeban))
    updater.start_polling()

import threading
threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    # Flask będzie działać na porcie, który Render przydzieli
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))