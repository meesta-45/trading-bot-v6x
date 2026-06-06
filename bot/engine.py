from collections import deque
from datetime import datetime
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
from bot.risk.tp_sl_engine import TPSLEngine

from bot.analysis.pnl_tracker import PnLTracker
from bot.analysis.drift_monitor import DriftMonitor
from bot.analysis.walk_forward import WalkForward
from bot.analysis.reversal_detector import ReversalDetector

from bot.risk.volatility_engine import VolatilityEngine

from bot.execution.position import Position
from bot.execution.position_manager import PositionManager
from bot.execution.hold_engine import HoldEngine


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=1000)

        # =====================================
        # MODE CONTROL
        # =====================================
        self.mode = ModeController()

        # DEFAULT MODE
        self.mode.set_mode("FOREX")

        # =====================================
        # REGIME
        # =====================================
        self.regime = MarketRegime()

        # =====================================
        # STRATEGIES
        # =====================================
        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        # =====================================
        # PORTFOLIO SYSTEMS
        # =====================================
        self.voting = VotingEngine()

        self.correlation = CorrelationEngine()

        self.alpha = AlphaEngine()

        # =====================================
        # RISK SYSTEMS
        # =====================================
        self.risk = RiskEngine()

        self.vol_target = VolatilityTarget()

        self.drawdown = DrawdownGuard()

        self.vol_engine = VolatilityEngine()

        self.tp_sl = TPSLEngine()

        # =====================================
        # ANALYTICS
        # =====================================
        self.pnl_tracker = PnLTracker()

        self.drift = DriftMonitor()

        self.walk_forward = WalkForward()

        self.reversal = ReversalDetector()

        # =====================================
        # POSITION MANAGEMENT
        # =====================================
        self.positions = PositionManager()

        self.hold_engine = HoldEngine()

        # =====================================
        # ACCOUNT
        # =====================================
        self.balance = 10000

        self.expected_return = 5

    # =====================================
    # SWITCH MARKET MODE
    # =====================================
    def set_market_mode(self, mode):

        self.mode.set_mode(mode)

    # =====================================
    # MAIN ENGINE LOOP
    # =====================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        # =====================================
        # MONITOR OPEN POSITIONS
        # =====================================
        for position in self.positions.active_positions():

            # LONG POSITIONS
            if position.direction == "LONG":

                if price >= position.take_profit:

                    print("\n✅ TAKE PROFIT HIT")

                    profit = 20

                    self.balance += profit

                    self.positions.close_position(
                        position
                    )

                    print(
                        "BALANCE:",
                        round(self.balance, 2)
                    )

                    continue

                elif price <= position.stop_loss:

                    print("\n❌ STOP LOSS HIT")

                    loss = 15

                    self.balance -= loss

                    self.positions.close_position(
                        position
                    )

                    print(
                        "BALANCE:",
                        round(self.balance, 2)
                    )

                    continue

            # SHORT POSITIONS
            elif position.direction == "SHORT":

                if price <= position.take_profit:

                    print("\n✅ TAKE PROFIT HIT")

                    profit = 20

                    self.balance += profit

                    self.positions.close_position(
                        position
                    )

                    print(
                        "BALANCE:",
                        round(self.balance, 2)
                    )

                    continue

                elif price >= position.stop_loss:

                    print("\n❌ STOP LOSS HIT")

                    loss = 15

                    self.balance -= loss

                    self.positions.close_position(
                        position
                    )

                    print(
                        "BALANCE:",
                        round(self.balance, 2)
                    )

                    continue

            # =====================================
            # REVERSAL EXIT
            # =====================================
            if self.reversal.detect(
                list(self.prices)
            ):

                print(
                    "\n⚠ REVERSAL DETECTED — EXITING POSITION"
                )

                self.positions.close_position(
                    position
                )

                continue

            # =====================================
            # TIME EXIT
            # =====================================
            if position.expired():

                print(
                    "\n⏰ POSITION HOLD TIME EXPIRED"
                )

                self.positions.close_position(
                    position
                )

                continue

        # =====================================
        # WARMUP
        # =====================================
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

        print("\n==========================")
        print("TIME:", datetime.utcnow())
        print("MODE:", mode)
        print("REGIME:", regime)
        print("BALANCE:", round(self.balance, 2))
        print(
            "ACTIVE POSITIONS:",
            len(
                self.positions.active_positions()
            )
        )
        print("==========================")

        # =====================================
        # DRAWDOWN PROTECTION
        # =====================================
        self.drawdown.update_peak(
            self.balance
        )

        if self.drawdown.kill_switch(
            self.balance
        ):

            print(
                "\n🚨 MAXIMUM DRAWDOWN REACHED"
            )

            return

        # =====================================
        # MODE INSTRUMENTS
        # =====================================
        symbols = INSTRUMENTS.get(
            mode,
            []
        )

        print(
            "MODE INSTRUMENTS:",
            symbols
        )

        # =====================================
        # STRATEGY SIGNALS
        # =====================================
        signals = []

        for name, strat in self.strategies.items():

            signal = strat.generate(
                prices
            )

            print(
                f"STRATEGY [{name}] =>",
                signal
            )

            if not signal:
                continue

            # =====================================
            # MODE FILTERING
            # =====================================
            if mode == "FOREX":

                if name == "mean_reversion":
                    continue

            elif mode == "CRYPTO":

                if name == "mean_reversion":
                    continue

            elif mode == "SYNTHETIC":

                if name == "breakout":
                    continue

            signal["strategy"] = name

            signals.append(signal)

        # =====================================
        # VOTING ENGINE
        # =====================================
        decision = self.voting.combine(
            signals
        )

        print("\nVOTING RESULT:")
        print(decision)

        if not decision:

            print("NO TRADE")

            return

        direction = decision["direction"]

        score = decision["score"]

        # =====================================
        # LOW EDGE FILTER
        # =====================================
        if score < 0.5:

            print(
                "TRADE REJECTED (LOW EDGE)"
            )

            return

        # =====================================
        # VOLATILITY CALCULATION
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

        print(
            "VOLATILITY:",
            round(vol, 4)
        )

        # =====================================
        # POSITION SIZE
        # =====================================
        target_size = (
            self.vol_target.target_position(
                self.balance,
                vol
            )
        )

        print(
            "TARGET POSITION SIZE:",
            round(target_size, 2)
        )

        # =====================================
        # HOLD TIME ENGINE
        # =====================================
        hold_minutes = (
            self.hold_engine.calculate(
                vol
            )
        )

        print(
            "HOLD TIME:",
            hold_minutes,
            "MINUTES"
        )

        # =====================================
        # TP/SL CALCULATION
        # =====================================
        if direction == "BUY":

            trade_direction = "LONG"

        else:

            trade_direction = "SHORT"

        tp, sl = self.tp_sl.generate(
            trade_direction,
            price,
            vol
        )

        # =====================================
        # CREATE POSITION
        # =====================================
        position = Position(
            direction=trade_direction,
            entry_price=price,
            size=target_size,
            stop_loss=sl,
            take_profit=tp,
            hold_minutes=hold_minutes
        )

        # =====================================
        # OPEN POSITION
        # =====================================
        self.positions.open_position(
            position
        )

        # =====================================
        # PNL TRACKING
        # =====================================
        simulated_pnl = random.uniform(
            -5,
            10
        )

        for s in signals:

            self.pnl_tracker.record(
                s["strategy"],
                simulated_pnl
            )

        # =====================================
        # ALPHA SCORING
        # =====================================
        alpha_scores = {}

        for s in self.strategies:

            avg = self.pnl_tracker.avg_pnl(
                s
            )

            alpha_scores[s] = (
                self.alpha.score(
                    avg_pnl=avg,
                    winrate=0.55,
                    drawdown=5
                )
            )

        print(
            "\nALPHA SCORES:"
        )

        print(alpha_scores)

        # =====================================
        # DRIFT DETECTION
        # =====================================
        drift = self.drift.deviation(
            self.expected_return,
            simulated_pnl
        )

        if self.drift.unstable(drift):

            print(
                "\n⚠ PERFORMANCE DRIFT DETECTED"
            )

        # =====================================
        # WALK FORWARD
        # =====================================
        wf_sets = (
            self.walk_forward.split(
                prices
            )
        )

        print(
            "WF DATASETS:",
            len(wf_sets)
        )

        # =====================================
        # FINAL TRADE OUTPUT
        # =====================================
        print("\n🚀 POSITION OPENED")
        print("DIRECTION:", trade_direction)
        print(
            "ENTRY:",
            round(price, 4)
        )
        print(
            "TAKE PROFIT:",
            round(tp, 4)
        )
        print(
            "STOP LOSS:",
            round(sl, 4)
        )
        print(
            "SIZE:",
            round(target_size, 2)
        )
        print(
            "HOLD:",
            hold_minutes,
            "MINUTES"
        )
