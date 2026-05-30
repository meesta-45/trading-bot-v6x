from collections import Counter
import statistics

from bot.indicators.ema import calculate_ema
from bot.indicators.macd import calculate_macd

from bot.confidence import ConfidenceEngine
from bot.deriv_execution import DerivExecution
from bot.tracker import TradeTracker


class Engine:

    def __init__(self):

        self.prices = []

        self.confidence_engine = ConfidenceEngine()

        self.execution = DerivExecution()

        self.tracker = TradeTracker()

        self.cooldown = 0

        self.base_threshold = 70

    # ----------------------------
    # DIGIT ANALYSIS (v12 improved)
    # ----------------------------
    def analyze_digits(self):

        if len(self.prices) < 20:
            return None

        digits = [int(str(p)[-1]) for p in self.prices[-20:]]

        counts = Counter(digits)

        total = sum(counts.values())

        weighted = {
            k: v / total for k, v in counts.items()
        }

        digit, weight = max(weighted.items(), key=lambda x: x[1])

        print(f"DOMINANT DIGIT: {digit} ({weight:.2f})")

        return digit, weight

    # ----------------------------
    # TREND ANALYSIS (v12 upgraded)
    # ----------------------------
    def analyze_trend(self):

        if len(self.prices) < 30:
            return None, 0

        ema10 = calculate_ema(self.prices, 10)
        ema20 = calculate_ema(self.prices, 20)

        if ema10 is None or ema20 is None:
            return None, 0

        diff = abs(ema10 - ema20)

        # trend strength (v12 improvement)
        strength = min(diff / ema20, 1)

        if ema10 > ema20:
            return "UP", strength

        elif ema10 < ema20:
            return "DOWN", strength

        return "SIDEWAYS", 0

    # ----------------------------
    # VOLATILITY FILTER (NEW v12)
    # ----------------------------
    def volatility(self):

        if len(self.prices) < 20:
            return 0

        return statistics.pstdev(self.prices[-20:])

    # ----------------------------
    # CONFIDENCE ENGINE (v12 upgraded)
    # ----------------------------
    def calculate_confidence(self):

        trend, strength = self.analyze_trend()

        macd = calculate_macd(self.prices)

        volatility = self.volatility()

        trend_score = 1 if trend in ["UP", "DOWN"] else 0

        macd_score = 0
        if macd is not None:
            macd_score = min(abs(macd) / 2, 1)

        volatility_score = 1 if volatility > 0 else 0

        # core confidence
        confidence = self.confidence_engine.calculate(
            trend_score,
            macd_score,
            volatility_score,
            strength > 0.3
        )

        # adaptive adjustment (v12 key upgrade)
        if volatility < 0.5:
            confidence -= 10  # avoid flat market traps

        if strength > 0.6:
            confidence += 10  # strong trend boost

        return max(0, min(100, confidence))

    # ----------------------------
    # SIGNAL GENERATION (v12 refined)
    # ----------------------------
    def generate_signal(self):

        trend, strength = self.analyze_trend()

        digit_data = self.analyze_digits()

        confidence = self.calculate_confidence()

        print("TREND:", trend, "STRENGTH:", strength)
        print("CONFIDENCE:", confidence)

        # adaptive threshold (v12 upgrade)
        threshold = self.base_threshold + (10 if strength > 0.5 else 0)

        if confidence < threshold:

            print("LOW CONFIDENCE — SKIPPING")

            return None

        if trend == "UP":

            return {
                "contract": "RISE",
                "confidence": confidence,
                "trend_strength": strength,
                "digit": digit_data
            }

        elif trend == "DOWN":

            return {
                "contract": "FALL",
                "confidence": confidence,
                "trend_strength": strength,
                "digit": digit_data
            }

        return None

    # ----------------------------
    # EXECUTION (v12 safer)
    # ----------------------------
    def execute_trade(self, signal):

        if signal is None:
            return

        if self.cooldown > 0:

            print("COOLDOWN ACTIVE")

            self.cooldown -= 1

            return

        contract = signal["contract"]

        confidence = signal["confidence"]

        print("EXECUTING TRADE:", contract, "CONF:", confidence)

        result = self.execution.buy(
            contract=contract,
            amount=1
        )

        if result == "WIN":

            self.tracker.record_win(10)

            self.cooldown = 3  # shorter after win

        else:

            self.tracker.record_loss(10)

            self.cooldown = 6  # longer after loss

        print("STATS:", self.tracker.stats())

    # ----------------------------
    # PRICE FEED
    # ----------------------------
    def on_price(self, price):

        self.prices.append(price)

        if len(self.prices) > 100:
            self.prices.pop(0)

        print("LIVE PRICE:", price)

        signal = self.generate_signal()

        self.execute_trade(signal)
