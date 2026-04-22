import threading
from flask import Flask

from engine import Engine
from feed import Feed
from config import SYMBOL

app = Flask(__name__)

engine = Engine()

def run_feed():
    feed = Feed(SYMBOL, engine.on_price)
    feed.start()

def run_bot():
    print("V9 BOT RUNNING")

threading.Thread(target=run_feed, daemon=True).start()
threading.Thread(target=run_bot, daemon=True).start()

@app.route("/")
def home():
    return "V9 Trading System Live"

@app.route("/status")
def status():
    return {"status": "running"}

app.run(host="0.0.0.0", port=10000)
