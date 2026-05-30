from collections import Counter

from bot.indicators.ema import calculate_ema
from bot.indicators.macd import calculate_macd

from bot.confidence import ConfidenceEngine
from bot.deriv_execution import DerivExecution


class Engine:

    def __init__(self):

        self.prices = []

        self.confidence_engine = ConfidenceEngine()

        self.execution = DerivExecution()

        self.cooldown = 0

    def analyze_digits(self):

        digits = [
            int(str(price)[-1])
            for price in self.prices[-20:]
        ]

        counts = Counter(digits)

        most_common = counts.most_common(1)

        if not most_common:
            return None

        digit = most_common[0][0]

        print("DOMINANT DIGIT:", digit)

        return digit

    def analyze_trend(self):

        if len(self.prices) < 30:
            return None

        ema10 = calculate_ema(self.prices, 10)
        ema20 = calculate_ema(self.prices, 20)

        if ema10 is None or ema20 is None:
            return None

        if ema10 > ema20:
            return "UP"

        elif ema10 < ema20:
            return "DOWN"

        return "SIDEWAYS"

    def calculate_confidence(self):

        trend = self.analyze_trend()

        macd = calculate_macd(self.prices)

        trend_score = trend in ["UP", "DOWN"]

        macd_score = macd is not None and abs(macd) > 0.5

        confidence = self.confidence_engine.calculate(
            trend_score,
            macd_score,
            True,
            True
        )

        return confidence

    def generate_signal(self):

        trend = self.analyze_trend()

        digit = self.analyze_digits()

        confidence = self.calculate_confidence()

        print("TREND:", trend)
        print("CONFIDENCE:", confidence)

        if confidence < 70:

            print("LOW CONFIDENCE — SKIPPING")

            return None

        if trend == "UP":

            return {
                "contract": "RISE",
                "confidence": confidence
            }

        elif trend == "DOWN":

            return {
                "contract": "FALL",
                "confidence": confidence
            }

        return None

    def execute_trade(self, signal):

        if signal is None:
            return

        if self.cooldown > 0:

            print("COOLDOWN ACTIVE")

            self.cooldown -= 1

            return

        contract = signal["contract"]

        confidence = signal["confidence"]

        print(
            "EXECUTING TRADE:",
            contract,
            "CONFIDENCE:",
            confidence
        )

        self.execution.buy(
            contract=contract,
            amount=1
        )

        self.cooldown = 5

    def on_price(self, price):

        self.prices.append(price)

        if len(self.prices) > 100:

            self.prices.pop(0)

        signal = self.generate_signal()

        self.execute_trade(signal)
    from bot.tracker import TradeTracker
