from bot.strategy import Strategy
from bot.risk import RiskManager
from bot.execution import ExecutionEngine

class Engine:

    def __init__(self):
        self.prices = []
        self.strategy = Strategy()
        self.risk = RiskManager()
        self.exec = ExecutionEngine()

    def on_price(self, price):

        self.prices.append(price)

        if len(self.prices) > 100:
            self.prices.pop(0)

        if len(self.prices) < 30:
            return

        signal = self.strategy.signal(self.prices)

        if self.risk.allow(signal):

            result = self.exec.execute("R_75", signal)

            self.risk.update(result)

            print("SIGNAL:", signal, "RESULT:", result)
