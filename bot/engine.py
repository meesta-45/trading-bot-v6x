from collections import deque

from bot.regime.detector import MarketRegime
from bot.core.mode_controller import ModeController
from bot.core.instruments import INSTRUMENTS

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.risk.risk_engine import RiskEngine

from bot.analysis.pnl_tracker import PnLTracker
from bot.risk.volatility_engine import VolatilityEngine
from bot.risk.drawdown_guard import DrawdownGuard


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=500)

        self.mode = ModeController()
        self.mode.set_mode("FOREX")

        self.regime = MarketRegime()

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()
        self.risk = RiskEngine()

        # =========================
        # V19 ADDITIONS
        # =========================
        self.pnl_tracker = PnLTracker()
        self.vol_engine = VolatilityEngine()
        self.drawdown = DrawdownGuard()

        self.balance = 10000

    def set_market_mode(self, mode):

        self.mode.set_mode(mode)

    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        if len(self.prices) < 100:
            print("WARMUP:", len(self.prices))
            return

        prices = list(self.prices)

        mode = self.mode.get_mode()

        regime = self.regime.detect(prices)

        print("\n========================")
        print("MODE:", mode)
        print("REGIME:", regime)
        print("BALANCE:", round(self.balance, 2))

        # =========================
        # DRAWDOWN CHECK
        # =========================
        self.drawdown.update_peak(self.balance)

        if self.drawdown.kill_switch(self.balance):
            print("🚨 KILL SWITCH ACTIVATED (DRAWDOWN LIMIT)")
            return

        signals = []

        # =========================
        # STRATEGY LOOP
        # =========================
        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            print(f"STRATEGY [{name}]:", signal)

            if signal:

                signal["strategy"] = name
                signals.append(signal)

        decision = self.voting.combine(signals)

        print("\nVOTING:", decision)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        if score < 0.5:
            print("LOW EDGE")
            return

        # =========================
        # VOLATILITY ESTIMATE (simple proxy)
        # =========================
        returns = [
            prices[i] - prices[i - 1]
            for i in range(1, len(prices))
        ]

        vol = self.vol_engine.compute(returns)

        # =========================
        # RISK SIZING
        # =========================
        size = self.risk.position_size(
            self.balance,
            kelly=0.2,
            volatility=vol
        )

        # =========================
        # EXECUTION SIMULATION
        # =========================
        import random

        pnl = random.uniform(-15, 20)

        self.balance += pnl

        # =========================
        # TRACK PERFORMANCE
        # =========================
        for s in signals:
            self.pnl_tracker.record(s["strategy"], pnl)

        # =========================
        # OUTPUT
        # =========================
        print("\n🚀 TRADE EXECUTED")
        print("DIRECTION:", direction)
        print("SCORE:", round(score, 3))
        print("VOL:", round(vol, 4))
        print("SIZE:", round(size, 2))
        print("PNL:", round(pnl, 2))
        print("NEW BALANCE:", round(self.balance, 2))
