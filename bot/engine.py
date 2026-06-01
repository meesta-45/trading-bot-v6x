from collections import deque

from bot.regime.detector import MarketRegime
from bot.core.mode_controller import ModeController
from bot.core.instruments import INSTRUMENTS

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.risk.risk_engine import RiskEngine


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=500)

        # =========================
        # MARKET MODE SYSTEM
        # =========================
        self.mode_controller = ModeController()
        self.mode_controller.set_mode("FOREX")  # default mode

        self.regime = MarketRegime()

        # =========================
        # STRATEGIES
        # =========================
        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()
        self.risk = RiskEngine()

        self.balance = 10000

        self.debug = True

    # =====================================
    # SWITCH MARKET MODE
    # =====================================
    def set_market_mode(self, mode):

        self.mode_controller.set_mode(mode)

    # =====================================
    # MAIN ENGINE LOOP
    # =====================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        # WAIT FOR ENOUGH DATA
        if len(self.prices) < 100:

            if self.debug:
                print("WAITING FOR DATA:", len(self.prices), "/100")

            return

        mode = self.mode_controller.get_mode()

        prices = list(self.prices)

        regime = self.regime.detect(prices)

        print("\n==============================")
        print("ACTIVE MODE:", mode)
        print("REGIME:", regime)
        print("BALANCE:", round(self.balance, 2))
        print("==============================")

        signals = []

        # =====================================
        # GET MODE INSTRUMENTS (for future expansion)
        # =====================================
        symbols = INSTRUMENTS.get(mode, [])

        if self.debug:
            print("MODE INSTRUMENTS:", symbols)

        # =====================================
        # STRATEGY EXECUTION
        # =====================================
        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            print(f"STRATEGY [{name}] OUTPUT:", signal)

            if not signal:
                continue

            # =========================
            # MODE FILTERING LOGIC
            # =========================

            if mode == "FOREX":

                # forex prefers trend + breakout
                if name == "mean_reversion":
                    continue

            elif mode == "CRYPTO":

                # crypto prefers breakout
                if name == "mean_reversion":
                    continue

            elif mode == "SYNTHETIC":

                # synthetic prefers mean reversion
                if name == "breakout":
                    continue

            signal["strategy"] = name
            signals.append(signal)

        # =====================================
        # VOTING ENGINE
        # =====================================
        decision = self.voting.combine(signals)

        print("\nALL SIGNALS:", signals)
        print("VOTING RESULT:", decision)

        if not decision:

            print("NO TRADE (NO CONSENSUS)")
            return

        direction = decision["direction"]
        score = decision["score"]

        # =====================================
        # EDGE FILTER
        # =====================================
        if score < 0.5:

            print("TRADE REJECTED (LOW EDGE)")
            return

        # =====================================
        # RISK SIZING
        # =====================================
        volatility = 1.0

        size = self.risk.position_size(
            self.balance,
            kelly=0.2,
            volatility=volatility
        )

        # =====================================
        # SIMULATED EXECUTION (placeholder for broker)
        # =====================================
        import random

        pnl = random.uniform(-12, 18)

        self.balance += pnl

        # =====================================
        # TRADE OUTPUT
        # =====================================
        print("\n🚀 TRADE EXECUTED")
        print("DIRECTION:", direction)
        print("SCORE:", round(score, 3))
        print("SIZE:", round(size, 2))
        print("PNL:", round(pnl, 2))
        print("NEW BALANCE:", round(self.balance, 2))
