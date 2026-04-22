import websocket
import json

class DataFeed:

    def __init__(self, symbol="R_75", callback=None):
        self.symbol = symbol
        self.callback = callback

    def on_message(self, ws, message):
        data = json.loads(message)

        if "tick" in data:
            price = float(data["tick"]["quote"])

            if self.callback:
                self.callback(price)

    def start(self):
        ws = websocket.WebSocketApp(
            "wss://ws.binaryws.com/websockets/v3?app_id=1089",
            on_message=self.on_message
        )

        ws.send(json.dumps({"ticks": self.symbol}))
        ws.run_forever()
