import os
import json
import pytz
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, jsonify

TOKEN = os.environ.get("TOKEN")
app = Flask(__name__)

trades_file = "trades.json"
tradebans_file = "tradebans.json"

# --- TELEGRAM BOT --- #
async def log_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    trade = {
        "item": text,
        "time": datetime.utcnow().isoformat()
    }
    if os.path.exists(trades_file):
        with open(trades_file, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(trade)
    with open(trades_file, "w") as f:
        json.dump(data, f, indent=2)
    await update.message.reply_text(f"Logged: {text}")

async def tradeban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    utc_now = datetime.utcnow()
    # Tradeban 8 dni → 9:00 PL time
    tz = pytz.timezone("Europe/Warsaw")
    tb_end = (utc_now + timedelta(days=8)).astimezone(tz).replace(hour=9, minute=0, second=0, microsecond=0)
    tradeban = {"item": text, "tradeban_end": tb_end.isoformat()}
    if os.path.exists(tradebans_file):
        with open(tradebans_file, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(tradeban)
    with open(tradebans_file, "w") as f:
        json.dump(data, f, indent=2)
    await update.message.reply_text(f"Tradeban logged: {text}, ends {tb_end}")

# --- Flask API --- #
@app.route("/trades")
def get_trades():
    if os.path.exists(trades_file):
        with open(trades_file, "r") as f:
            data = json.load(f)
    else:
        data = []
    return jsonify(data)

@app.route("/tradebans")
def get_tradebans():
    if os.path.exists(tradebans_file):
        with open(tradebans_file, "r") as f:
            data = json.load(f)
    else:
        data = []
    return jsonify(data)

# --- RUN --- #
if __name__ == "__main__":
    # Uruchom Flask w Render
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()

    # Uruchom Telegram bota
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("log", log_trade))
    app_bot.add_handler(CommandHandler("tradeban", tradeban))
    app_bot.run_polling()