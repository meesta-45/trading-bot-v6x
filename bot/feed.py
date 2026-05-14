import asyncio
import json
import websockets


class Feed:

    def __init__(self, symbol, callback):

        self.symbol = symbol
        self.callback = callback

    async def connect(self):

        print("ENTERED CONNECT FUNCTION")

        url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

        while True:

            try:

                print("CONNECTING TO DERIV...")

                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=10,
                    open_timeout=30,
                    ssl=True
                ) as websocket:

                    print("CONNECTED TO DERIV")

                    payload = {
                        "ticks": self.symbol
                    }

                    await websocket.send(json.dumps(payload))

                    print("SUBSCRIBED TO TICKS")

                    while True:

                        message = await websocket.recv()

                        data = json.loads(message)

                        print("RAW MESSAGE:", data)

                        if "tick" in data:

                            price = float(data["tick"]["quote"])

                            print("LIVE PRICE:", price)

                            self.callback(price)

            except Exception as e:

                print("WEBSOCKET ERROR:", str(e))

                print("RECONNECTING IN 5 SECONDS...")

                await asyncio.sleep(5)

    def start(self):

        print("START METHOD CALLED")

        try:

            asyncio.run(self.connect())

        except Exception as e:

            print("ASYNCIO ERROR:", str(e))
