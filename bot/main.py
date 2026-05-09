import threading
import time

from flask import Flask

from bot.feed import Feed
from bot.engine import Engine
from bot.config import SYMBOL

print("V10 SYSTEM STARTING")

app = Flask(__name__)

engine = Engine()

def run_feed():

    while True:

        try:

            print("LAUNCHING DERIV FEED")

            feed = Feed(SYMBOL, engine.on_price)

            feed.start()

        except Exception as e:

            print("FEED THREAD ERROR:", e)

        print("RESTARTING FEED IN 5 SECONDS")

        time.sleep(5)

feed_thread = threading.Thread(target=run_feed)

feed_thread.start()

@app.route("/")
def home():

    return "V10 Deriv AI System Running"

@app.route("/status")
def status():

    return {
        "status": "running"
    }

app.run(host="0.0.0.0", port=10000)
