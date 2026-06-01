from collections import deque

from bot.regime.detector import MarketRegime

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.risk.risk_engine import RiskEngine

from bot.execution.slippage_model import SlippageModel

from bot.analysis.drift import DriftDetector
from bot.analysis.edge_decay import EdgeDecay

from bot.portfolio.meta_allocator import MetaAllocator


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=500)

        self.regime = MarketRegime()

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()
        self.risk = RiskEngine()

        self.slippage = SlippageModel()
        self.drift = DriftDetector()
        self.edge = EdgeDecay()
        self.meta = MetaAllocator()

        self.balance = 10000

        self.expected_return = 1.0

        # DEBUG MODE
        self.debug = True

    # =====================================
    # MAIN PRICE LOOP
    # =====================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        # ---------------------------------
        # WAIT FOR ENOUGH DATA
        # ---------------------------------
        if len(self.prices) < 100:

            if self.debug:
                print(
                    "WAITING FOR DATA:",
                    len(self.prices),
                    "/100"
                )

            return

        prices = list(self.prices)

        # ---------------------------------
        # REGIME DETECTION
        # ---------------------------------
        regime = self.regime.detect(prices)

        print("REGIME:", regime)

        signals = []

        # =====================================
        # STRATEGY EXECUTION LOOP
        # =====================================
        for name, strat in self.strategies.items():

            try:

                signal = strat.generate(prices)

                print(
                    f"STRATEGY [{name}] SIGNAL:",
                    signal
                )

                if signal:

                    signal["strategy"] = name

                    signals.append(signal)

            except Exception as e:

                print(
                    f"ERROR IN STRATEGY [{name}]:",
                    e
                )

        # ---------------------------------
        # SHOW ALL SIGNALS
        # ---------------------------------
        print("ALL SIGNALS:", signals)

        # =====================================
        # VOTING ENGINE
        # =====================================
        decision = self.voting.combine(signals)

        print("VOTING DECISION:", decision)

        if not decision:

            print(
                "NO CONSENSUS — NO TRADE EXECUTED"
            )

            return

        direction = decision["direction"]
        score = decision["score"]

        # ---------------------------------
        # MINIMUM EDGE FILTER
        # ---------------------------------
        if score < 0.5:

            print(
                "LOW SCORE — TRADE REJECTED"
            )

            return

        # =====================================
        # EXECUTION SIMULATION
        # =====================================
        executed_price = self.slippage.apply(
            price,
            direction
        )

        # =====================================
        # POSITION SIZING
        # =====================================
        volatility = 1.0

        size = self.risk.position_size(
            self.balance,
            kelly=0.2,
            volatility=volatility
        )

        print("POSITION SIZE:", size)

        # =====================================
        # SIMULATED PNL
        # =====================================
        import random

        pnl = random.uniform(-12, 18)

        self.balance += pnl

        # =====================================
        # DRIFT DETECTION
        # =====================================
        actual = pnl

        drift = self.drift.detect(
            self.expected_return,
            actual
        )

        if self.drift.is_broken(drift):

            print(
                "🚨 EDGE DRIFT DETECTED"
            )

        # =====================================
        # EDGE TRACKING
        # =====================================
        self.edge.update(
            "portfolio",
            pnl
        )

        decaying = self.edge.is_decaying(
            "portfolio"
        )

        if decaying:

            print(
                "⚠ EDGE DECAY DETECTED"
            )

        # =====================================
        # FINAL TRADE OUTPUT
        # =====================================
        print("\n========================")
        print("🚀 V17 TRADE EXECUTED")
        print("========================")

        print("DIRECTION:", direction)

        print(
            "EXECUTED PRICE:",
            executed_price
        )

        print("SCORE:", score)

        print("PNL:", round(pnl, 2))

        print(
            "BALANCE:",
            round(self.balance, 2)
        )

        print(
            "DRIFT:",
            round(drift, 4)
        )

        print("========================")
