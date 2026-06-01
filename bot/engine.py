from collections import deque

from bot.regime.detector import MarketRegime

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.risk.risk_engine import RiskEngine

from bot.core.mode_controller import ModeController


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=500)

        self.mode_controller = ModeController()

        # default mode (YOU CONTROL THIS)
        self.mode_controller.set_mode("FOREX")

        self.regime = MarketRegime()

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()
        self.risk = RiskEngine()

        self.balance = 10000

    # =====================================
    # MANUAL MODE SWITCH
    # =====================================
    def set_market_mode(self, mode):

        self.mode_controller.set_mode(mode)

    # =====================================
    # MAIN LOOP
    # =====================================
    def on_price(self, price):

        self.prices.append(price)

        if len(self.prices) < 100:
            print("WAITING FOR DATA...")
            return

        mode = self.mode_controller.get_mode()

        prices = list(self.prices)

        regime = self.regime.detect(prices)

        print("\n======================")
        print("MODE:", mode)
        print("REGIME:", regime)

        signals = []

        # =====================================
        # MODE FILTERING LOGIC
        # =====================================

        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            if not signal:
                continue

            # FILTER STRATEGIES BY MODE
            if mode == "FOREX" and name == "mean_reversion":
                continue  # weaker in forex in this version

            if mode == "CRYPTO" and name == "trend":
                pass  # allowed

            if mode == "SYNTHETIC" and name == "breakout":
                continue

            signal["strategy"] = name
            signals.append(signal)

        decision = self.voting.combine(signals)

        print("SIGNALS:", signals)
        print("DECISION:", decision)

        if not decision:
            print("NO TRADE")
            return

        direction = decision["direction"]
        score = decision["score"]

        volatility = 1.0

        size = self.risk.position_size(
            self.balance,
            kelly=0.2,
            volatility=volatility
        )

        print("TRADE:", direction)
        print("SIZE:", size)
