from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "V9 API Live"

@app.route("/health")
def health():
    return {"status": "ok"}

app.run(host="0.0.0.0", port=10000)
