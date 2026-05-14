import asyncio
import json
import websockets


class Feed:

    def __init__(self, symbol, callback):

        self.symbol = symbol
        self.callback = callback

    async def fetch_tick(self):

        url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

        try:

            async with websockets.connect(url) as websocket:

                payload = {
                    "ticks": self.symbol,
                    "subscribe": 1
                }

                await websocket.send(json.dumps(payload))

                message = await websocket.recv()

                data = json.loads(message)

                if "tick" in data:

                    price = float(data["tick"]["quote"])

                    print("LIVE PRICE:", price)

                    self.callback(price)

        except Exception as e:

            print("FETCH ERROR:", str(e))

    async def loop(self):

        print("STARTING POLLING LOOP")

        while True:

            await self.fetch_tick()

            await asyncio.sleep(2)

    def start(self):

        print("START METHOD CALLED")

        asyncio.run(self.loop())
