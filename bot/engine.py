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

    def on_price(self, price):

        self.prices.append(price)

        if len(self.prices) < 100:
            return

        prices = list(self.prices)

        regime = self.regime.detect(prices)

        signals = []

        # ----------------------------
        # STRATEGY LOOP
        # ----------------------------
        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            if not signal:
                continue

            signals.append(signal)

        decision = self.voting.combine(signals)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        # ----------------------------
        # EXECUTION SIMULATION
        # ----------------------------
        executed_price = self.slippage.apply(price, direction)

        # fake PnL model (replace with broker later)
        import random
        pnl = random.uniform(-12, 18)

        self.balance += pnl

        # ----------------------------
        # DRIFT DETECTION
        # ----------------------------
        actual = pnl
        drift = self.drift.detect(self.expected_return, actual)

        if self.drift.is_broken(drift):
            print("🚨 STRATEGY EDGE BROKEN - REDUCING EXPOSURE")

        # ----------------------------
        # EDGE DECAY TRACKING
        # ----------------------------
        self.edge.update("portfolio", pnl)

        # ----------------------------
        # LOG OUTPUT
        # ----------------------------
        print("\n--- V17 TRADE ---")
        print("REGIME:", regime)
        print("EXEC PRICE:", executed_price)
        print("DIRECTION:", direction)
        print("SCORE:", score)
        print("PNL:", pnl)
        print("DRIFT:", drift)
        print("BALANCE:", self.balance)
