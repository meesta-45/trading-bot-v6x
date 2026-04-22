import time

class BotEngine:

    def __init__(self, strategy):
        self.strategy = strategy
        self.prices = []

    def update_price(self, price):
        self.prices.append(price)

        if len(self.prices) > 100:
            self.prices.pop(0)

    def run(self):
        while True:
            if len(self.prices) > 20:
                signal = self.strategy.signal(self.prices)
                print("SIGNAL:", signal)

            time.sleep(2)
