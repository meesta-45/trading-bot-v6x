from bot.strategies.trend_strategy import TrendStrategy
from bot.strategies.digit_strategy import DigitStrategy

class Engine:

    def __init__(self):

        self.prices = []

        self.trend = TrendStrategy()
        self.digits = DigitStrategy()

    def on_price(self, price):

        self.prices.append(price)

        if len(self.prices) > 100:
            self.prices.pop(0)

        if len(self.prices) < 30:
            return

        trend_signal = self.trend.analyze(self.prices)

        digit_signal = self.digits.analyze(self.prices)

        print("TREND:", trend_signal)
        print("DIGITS:", digit_signal)
