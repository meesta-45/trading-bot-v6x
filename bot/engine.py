from strategy import Strategy
from risk import RiskManager
from execution import ExecutionEngine
from config import SYMBOL

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

            result = self.exec.execute(SYMBOL, signal)

            self.risk.update(result)

            print("SIGNAL:", signal, "RESULT:", result)
from config import MODE, SYMBOL
