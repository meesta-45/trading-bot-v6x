from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Trading Bot API Running"

app.run(host="0.0.0.0", port=10000)
