from flask import Flask
import threading

from bot.feed import Feed
from bot.engine import Engine
from bot.config import SYMBOL

app = Flask(__name__)

engine = Engine()

def start_bot():

    print("STARTING BOT ENGINE")

    feed = Feed(SYMBOL, engine.on_price)

    feed.start()

bot_thread = threading.Thread(target=start_bot)

bot_thread.start()

@app.route("/")
def home():

    return "Deriv AI Bot Running"

@app.route("/status")
def status():

    return {
        "status": "running"
    }

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)
