from flask import Flask
import threading
import time

from strategy import Strategy
from bot_logic import BotEngine
from data_feed import DataFeed

app = Flask(__name__)

strategy = Strategy()
bot = BotEngine(strategy)

# ---- CALLBACK ----
def on_price(price):
    bot.update_price(price)

# ---- THREAD 1: BOT ----
def run_bot():
    bot.run()

# ---- THREAD 2: DATA FEED ----
def run_feed():
    feed = DataFeed("R_75", callback=on_price)
    feed.start()

threading.Thread(target=run_bot, daemon=True).start()
threading.Thread(target=run_feed, daemon=True).start()

@app.route("/")
def home():
    return "V7 Trading Bot Running"

@app.route("/status")
def status():
    return {"status": "live"}

app.run(host="0.0.0.0", port=10000)
