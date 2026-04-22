from flask import Flask
import threading
import time

app = Flask(__name__)

def bot_loop():
    print("Bot thread started")

    while True:
        try:
            print("Bot running...")
            time.sleep(5)
        except Exception as e:
            print("Bot error:", e)
            time.sleep(5)

@app.route("/")
def home():
    return "Bot is running"

@app.route("/status")
def status():
    return {"status": "live"}

# IMPORTANT: daemon ensures Render doesn't kill thread silently
thread = threading.Thread(target=bot_loop, daemon=True)
thread.start()

app.run(host="0.0.0.0", port=10000)
