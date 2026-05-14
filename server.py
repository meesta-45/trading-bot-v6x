from flask import Flask

from bot.strategies.trend_strategy import TrendStrategy

app = Flask(__name__)

strategy = TrendStrategy()

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
