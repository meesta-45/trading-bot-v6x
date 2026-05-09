import websocket
import json

class Feed:

    def __init__(self, symbol, callback):

        self.symbol = symbol
        self.callback = callback

    def on_message(self, ws, message):

        data = json.loads(message)

        if "tick" in data:

            price = float(data["tick"]["quote"])

            print("LIVE PRICE:", price)

            self.callback(price)

    def on_error(self, ws, error):

        print("WEBSOCKET ERROR:", error)

    def on_close(self, ws, close_status_code, close_msg):

        print("WEBSOCKET CLOSED")

    def on_open(self, ws):

        print("CONNECTED TO DERIV")

        payload = {
            "ticks": self.symbol
        }

        ws.send(json.dumps(payload))

    def start(self):

        print("STARTING WEBSOCKET...")

        ws = websocket.WebSocketApp(
            "wss://ws.binaryws.com/websockets/v3?app_id=1089",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        ws.run_forever()
