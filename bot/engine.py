from collections import deque
import random

from bot.regime.detector import MarketRegime
from bot.core.mode_controller import ModeController
from bot.core.instruments import INSTRUMENTS

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.portfolio.alpha_engine import AlphaEngine

from bot.risk.volatility_engine import VolatilityEngine
from bot.risk.drawdown_guard import DrawdownGuard
from bot.risk.tp_sl_engine import TPSLEngine

from bot.execution.position import Position
from bot.execution.position_manager import PositionManager
from bot.execution.hold_engine import HoldEngine

from bot.analysis.reversal_detector import ReversalDetector


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

        self.positions = PositionManager()
        self.hold_engine = HoldEngine()

        self.vol_engine = VolatilityEngine()
        self.tp_sl = TPSLEngine()
        self.drawdown = DrawdownGuard()
        self.alpha = AlphaEngine()
        self.reversal = ReversalDetector()

        self.balance = 10000

        # =========================
        # V22 CONTROL SYSTEM
        # =========================
        self.cooldown = 0
        self.trade_count = 0

        self.cooldown_limit = 5
        self.trade_batch_limit = 8
        self.batch_profit_target = 40
        self.batch_profit = 0

    # =========================
    # POSITION MANAGEMENT
    # =========================
    def _manage_positions(self, price):

        for position in list(self.positions.active_positions()):

            # ================= LONG =================
            if position.direction == "LONG":

                if price >= position.take_profit:

                    print("✅ TAKE PROFIT HIT (LONG)")
                    self.balance += 20
                    self.batch_profit += 20
                    self.positions.close_position(position)

                elif price <= position.stop_loss:

                    print("❌ STOP LOSS HIT (LONG)")
                    self.balance -= 15
                    self.batch_profit -= 15
                    self.positions.close_position(position)

                # reversal exit
                elif self.reversal.detect(list(self.prices)):

                    print("⚠ REVERSAL EXIT (LONG)")
                    self.positions.close_position(position)

            # ================= SHORT =================
            elif position.direction == "SHORT":

                if price <= position.take_profit:

                    print("✅ TAKE PROFIT HIT (SHORT)")
                    self.balance += 20
                    self.batch_profit += 20
                    self.positions.close_position(position)

                elif price >= position.stop_loss:

                    print("❌ STOP LOSS HIT (SHORT)")
                    self.balance -= 15
                    self.batch_profit -= 15
                    self.positions.close_position(position)

                elif self.reversal.detect(list(self.prices)):

                    print("⚠ REVERSAL EXIT (SHORT)")
                    self.positions.close_position(position)

            # ================= TIME EXIT =================
            if position.expired():

                print("⏰ HOLD TIME EXPIRED")
                self.positions.close_position(position)

    # =========================
    # MAIN ENGINE
    # =========================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        # manage open trades first
        self._manage_positions(price)

        # ================= COOLDOWN =================
        if self.cooldown > 0:

            print("🧊 COOLDOWN:", self.cooldown)
            self.cooldown -= 1
            return

        # ================= WARMUP =================
        if len(self.prices) < 120:

            print("WARMUP:", len(self.prices))
            return

        prices = list(self.prices)

        mode = self.mode.get_mode()

        print("\n====================")
        print("MODE:", mode)
        print("BALANCE:", self.balance)
        print("ACTIVE POSITIONS:", len(self.positions.active_positions()))
        print("====================")

        # ================= STRATEGY SIGNALS =================
        signals = []

        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            if signal:

                signal["strategy"] = name
                signals.append(signal)

        decision = VotingEngine().combine(signals)

        print("VOTING:", decision)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        if score < 0.55:
            print("LOW EDGE SKIP")
            return

        # ================= LIMIT ACTIVE POSITIONS =================
        if len(self.positions.active_positions()) >= 2:
            print("MAX POSITIONS REACHED")
            return

        # ================= HOLD LOGIC =================
        vol = self.vol_engine.compute(
            [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        )

        hold_minutes = self.hold_engine.calculate(vol)

        # ================= LONG HOLD EXTENSION RULE =================
        # ONLY extend if strong conviction
        if score > 0.75 and direction == "BUY":
            hold_minutes = min(60, hold_minutes + 30)

        trade_direction = "LONG" if direction == "BUY" else "SHORT"

        tp, sl = self.tp_sl.generate(trade_direction, price, vol)

        position = Position(
            direction=trade_direction,
            entry_price=price,
            size=1,
            stop_loss=sl,
            take_profit=tp,
            hold_minutes=hold_minutes
        )

        self.positions.open_position(position)

        print("\n🚀 POSITION OPENED")
        print("DIR:", trade_direction)
        print("ENTRY:", price)
        print("TP:", tp)
        print("SL:", sl)
        print("HOLD:", hold_minutes)

        # ================= COOLDOWN LOGIC =================
        self.trade_count += 1

        if self.batch_profit >= self.batch_profit_target:
            print("🎯 PROFIT TARGET HIT → COOLDOWN START")
            self.cooldown = self.cooldown_limit
            self.batch_profit = 0

        elif self.trade_count >= self.trade_batch_limit:
            print("📊 TRADE BATCH LIMIT HIT → COOLDOWN")
            self.cooldown = self.cooldown_limit
            self.trade_count = 0
