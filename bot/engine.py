from collections import deque

from bot.regime.detector import MarketRegime

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.risk.risk_engine import RiskEngine

from bot.storage.database import TradeDB
from bot.portfolio.weights import StrategyWeights
from bot.risk.kill_switch import KillSwitch
from bot.analysis.performance_tracker import PerformanceTracker


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=500)

        self.regime_detector = MarketRegime()

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()
        self.risk = RiskEngine()

        self.weights = StrategyWeights()
        self.killswitch = KillSwitch()
        self.performance = PerformanceTracker()
        self.db = TradeDB()

        self.balance = 10000
        self.peak_balance = 10000

    def on_price(self, price):

        self.prices.append(price)

        if len(self.prices) < 100:
            return

        prices = list(self.prices)

        regime = self.regime_detector.detect(prices)

        signals = []
        weighted_perf = {}

        # =====================================
        # STRATEGY EXECUTION
        # =====================================
        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            if not signal:
                continue

            # KILL SWITCH CHECK
            allow = self.killswitch.evaluate(
                name,
                ev=signal["expected_value"],
                drawdown=5,   # placeholder (upgrade later)
                sharpe=1.0
            )

            if not allow:
                continue

            # weight injection
            weight = self.weights.weights.get(name, 1)

            signal["weight"] = weight
            signal["strategy"] = name

            signals.append(signal)

        # =====================================
        # VOTING ENGINE
        # =====================================
        decision = self.voting.combine(signals)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        # =====================================
        # RISK ENGINE
        # =====================================
        volatility = 1.0

        size = self.risk.position_size(
            self.balance,
            kelly=0.2,
            volatility=volatility
        )

        print("\n--- TRADE SIGNAL ---")
        print("REGIME:", regime)
        print("DIRECTION:", direction)
        print("SCORE:", score)
        print("SIZE:", size)

        # =====================================
        # SIMULATED RESULT HOOK (replace with broker later)
        # =====================================
        import random
        pnl = random.uniform(-10, 15)
        win = pnl > 0

        self.balance += pnl

        # update peak balance
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance

        # =====================================
        # UPDATE PERFORMANCE SYSTEMS
        # =====================================
        for s in signals:
            self.performance.record(s["strategy"], win)

        perf = self.performance.performance()

        self.weights.update(perf)

        # =====================================
        # DATABASE LOGGING
        # =====================================
        for s in signals:

            self.db.log_trade(
                strategy=s["strategy"],
                direction=direction,
                confidence=s["confidence"],
                score=score,
                regime=regime,
                pnl=pnl
            )

        print("BALANCE:", self.balance)
        print("WEIGHTS:", self.weights.weights)
