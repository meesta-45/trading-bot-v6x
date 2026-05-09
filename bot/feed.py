import asyncio
import json
import websockets

class Feed:

    def __init__(self, symbol, callback):

        self.symbol = symbol
        self.callback = callback

    async def connect(self):

        url = "wss://ws.derivws.com/websockets/v3?app_id=1089"

        while True:

            try:

                print("CONNECTING TO DERIV...")

                async with websockets.connect(url) as websocket:

                    print("CONNECTED TO DERIV")

                    payload = {
                        "ticks": self.symbol
                    }

                    await websocket.send(json.dumps(payload))

                    while True:

                        message = await websocket.recv()

                        data = json.loads(message)

                        if "tick" in data:

                            price = float(data["tick"]["quote"])

                            print("LIVE PRICE:", price)

                            self.callback(price)

            except Exception as e:

                print("WEBSOCKET ERROR:", e)

                print("RECONNECTING IN 5 SECONDS...")

                await asyncio.sleep(5)

    def start(self):

        asyncio.run(self.connect())
