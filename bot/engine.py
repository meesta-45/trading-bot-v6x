from collections import deque
import random

from bot.regime.detector import MarketRegime
from bot.core.mode_controller import ModeController
from bot.core.instruments import INSTRUMENTS

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.portfolio.correlation_engine import CorrelationEngine
from bot.portfolio.alpha_engine import AlphaEngine

from bot.risk.risk_engine import RiskEngine
from bot.risk.vol_target import VolatilityTarget
from bot.risk.drawdown_guard import DrawdownGuard

from bot.analysis.pnl_tracker import PnLTracker
from bot.analysis.drift_monitor import DriftMonitor
from bot.analysis.walk_forward import WalkForward

from bot.risk.volatility_engine import VolatilityEngine


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=1000)

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
        self.vol_target = VolatilityTarget()

        self.drawdown = DrawdownGuard()

        self.pnl_tracker = PnLTracker()

        self.correlation = CorrelationEngine()
        self.alpha = AlphaEngine()

        self.drift = DriftMonitor()
        self.walk_forward = WalkForward()

        self.vol_engine = VolatilityEngine()

        self.balance = 10000

        self.expected_return = 5

    # =====================================
    # MARKET MODE CONTROL
    # =====================================
    def set_market_mode(self, mode):

        self.mode.set_mode(mode)

    # =====================================
    # MAIN LOOP
    # =====================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        if len(self.prices) < 120:

            print(
                "WARMUP:",
                len(self.prices),
                "/120"
            )

            return

        prices = list(self.prices)

        mode = self.mode.get_mode()

        regime = self.regime.detect(prices)

        print("\n======================")
        print("MODE:", mode)
        print("REGIME:", regime)
        print("BALANCE:", round(self.balance, 2))

        # =====================================
        # DRAWDOWN CONTROL
        # =====================================
        self.drawdown.update_peak(
            self.balance
        )

        if self.drawdown.kill_switch(
            self.balance
        ):

            print(
                "🚨 MAX DRAWDOWN HIT"
            )

            return

        # =====================================
        # STRATEGY SIGNALS
        # =====================================
        signals = []

        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            print(
                f"STRATEGY [{name}]",
                signal
            )

            if signal:

                signal["strategy"] = name

                signals.append(signal)

        decision = self.voting.combine(
            signals
        )

        print("VOTING:", decision)

        if not decision:

            print("NO TRADE")
            return

        direction = decision["direction"]
        score = decision["score"]

        # =====================================
        # VOLATILITY
        # =====================================
        returns = [
            prices[i] - prices[i - 1]
            for i in range(
                1,
                len(prices)
            )
        ]

        vol = self.vol_engine.compute(
            returns
        )

        # =====================================
        # VOL TARGETING
        # =====================================
        target_size = (
            self.vol_target.target_position(
                self.balance,
                vol
            )
        )

        # =====================================
        # EXECUTION SIMULATION
        # =====================================
        pnl = random.uniform(
            -20,
            25
        )

        self.balance += pnl

        # =====================================
        # PNL TRACKING
        # =====================================
        for s in signals:

            self.pnl_tracker.record(
                s["strategy"],
                pnl
            )

        # =====================================
        # ALPHA SCORING
        # =====================================
        alpha_scores = {}

        for s in self.strategies:

            avg = self.pnl_tracker.avg_pnl(s)

            alpha_scores[s] = (
                self.alpha.score(
                    avg_pnl=avg,
                    winrate=0.55,
                    drawdown=5
                )
            )

        print(
            "ALPHA SCORES:",
            alpha_scores
        )

        # =====================================
        # DRIFT DETECTION
        # =====================================
        drift = self.drift.deviation(
            self.expected_return,
            pnl
        )

        if self.drift.unstable(drift):

            print(
                "⚠ PERFORMANCE DRIFT DETECTED"
            )

        # =====================================
        # WALK FORWARD
        # =====================================
        wf_sets = self.walk_forward.split(
            prices
        )

        print(
            "WF DATASETS:",
            len(wf_sets)
        )

        # =====================================
        # FINAL OUTPUT
        # =====================================
        print("\n🚀 TRADE EXECUTED")
        print("DIRECTION:", direction)
        print("SCORE:", round(score, 4))
        print("VOL:", round(vol, 4))
        print(
            "TARGET SIZE:",
            round(target_size, 2)
        )
        print("PNL:", round(pnl, 2))
        print(
            "BALANCE:",
            round(self.balance, 2)
        )
