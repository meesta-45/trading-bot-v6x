from flask import Flask
import threading
import time

app = Flask(__name__)

# ---- BOT LOGIC ----
def bot_loop():
    print("Bot started")

    while True:
        print("Bot running...")
        time.sleep(5)

# ---- START BOT IN BACKGROUND ----
threading.Thread(target=bot_loop).start()

# ---- WEB SERVER (RENDER NEEDS THIS) ----
@app.route("/")
def home():
    return "Bot is running"

@app.route("/status")
def status():
    return {"status": "live"}

app.run(host="0.0.0.0", port=10000)
