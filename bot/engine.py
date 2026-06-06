from collections import deque
import random

from bot.regime.detector import MarketRegime
from bot.core.mode_controller import ModeController

from bot.strategies.trend import TrendStrategy
from bot.strategies.mean_reversion import MeanReversionStrategy
from bot.strategies.breakout import BreakoutStrategy

from bot.portfolio.voting import VotingEngine
from bot.portfolio.capital_allocator import CapitalAllocator

from bot.risk.volatility_engine import VolatilityEngine
from bot.risk.drawdown_guard import DrawdownGuard
from bot.risk.tp_sl_engine import TPSLEngine

from bot.execution.position import Position
from bot.execution.position_manager import PositionManager

from bot.analysis.reversal_detector import ReversalDetector


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=1000)

        # =========================
        # CORE SYSTEMS
        # =========================
        self.mode = ModeController()
        self.mode.set_mode("FOREX")

        self.regime = MarketRegime()

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()

        # =========================
        # PORTFOLIO SYSTEMS
        # =========================
        self.capital_allocator = CapitalAllocator()
        self.base_capital = 100

        self.positions = PositionManager()

        # =========================
        # RISK SYSTEMS
        # =========================
        self.vol_engine = VolatilityEngine()
        self.drawdown = DrawdownGuard()
        self.tp_sl = TPSLEngine()
        self.reversal = ReversalDetector()

        # =========================
        # ACCOUNT STATE
        # =========================
        self.balance = 10000

    # =====================================================
    # HORIZON CLASSIFICATION
    # =====================================================
    def classify_horizon(self, vol, score):

        if vol > 2.5 and score < 0.6:
            return "SCALP_30S"

        if vol > 1.8 and score < 0.65:
            return "SCALP_45S"

        if score < 0.8:
            return "SHORT_5M"

        return "SWING_15M"

    # =====================================================
    # HORIZON TO HOLD TIME
    # =====================================================
    def horizon_to_minutes(self, horizon):

        if horizon == "SCALP_30S":
            return 0.5

        if horizon == "SCALP_45S":
            return 0.75

        if horizon == "SHORT_5M":
            return 5

        return 15

    # =====================================================
    # POSITION MANAGEMENT
    # =====================================================
    def _manage_positions(self, price):

        for position in list(self.positions.active_positions()):

            # ================= LONG =================
            if position.direction == "LONG":

                if price >= position.take_profit:

                    print("✅ TAKE PROFIT (LONG)")
                    self.balance += 20
                    self.positions.close_position(position)

                elif price <= position.stop_loss:

                    print("❌ STOP LOSS (LONG)")
                    self.balance -= 15
                    self.positions.close_position(position)

                elif self.reversal.detect(list(self.prices)):

                    print("⚠ REVERSAL EXIT (LONG)")
                    self.positions.close_position(position)

            # ================= SHORT =================
            elif position.direction == "SHORT":

                if price <= position.take_profit:

                    print("✅ TAKE PROFIT (SHORT)")
                    self.balance += 20
                    self.positions.close_position(position)

                elif price >= position.stop_loss:

                    print("❌ STOP LOSS (SHORT)")
                    self.balance -= 15
                    self.positions.close_position(position)

                elif self.reversal.detect(list(self.prices)):

                    print("⚠ REVERSAL EXIT (SHORT)")
                    self.positions.close_position(position)

            # ================= TIME EXIT =================
            if position.expired():

                print("⏰ TIME EXIT")
                self.positions.close_position(position)

    # =====================================================
    # MAIN ENGINE LOOP
    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        # manage open positions first
        self._manage_positions(price)

        # ================= WARMUP =================
        if len(self.prices) < 120:
            print("WARMUP:", len(self.prices))
            return

        prices = list(self.prices)

        print("\n======================")
        print("BALANCE:", self.balance)
        print("ACTIVE POSITIONS:", len(self.positions.active_positions()))
        print("======================")

        # ================= POSITION LIMIT =================
        if len(self.positions.active_positions()) >= 2:
            print("MAX POSITIONS ACTIVE")
            return

        # ================= STRATEGY SIGNALS =================
        signals = []

        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            if signal:
                signal["strategy"] = name
                signals.append(signal)

        decision = self.voting.combine(signals)

        print("VOTING:", decision)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        if score < 0.55:
            print("LOW EDGE SKIP")
            return

        # ================= VOLATILITY =================
        vol = self.vol_engine.compute(
            [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        )

        print("VOL:", round(vol, 4))

        # ================= HORIZON SELECTION =================
        horizon = self.classify_horizon(vol, score)

        hold_minutes = self.horizon_to_minutes(horizon)

        print("HORIZON:", horizon)
        print("HOLD TIME:", hold_minutes)

        # ================= DRAWNDOWN =================
        drawdown = self.drawdown.drawdown(self.balance)

        # ================= STRATEGY NAME =================
        strategy_name = decision.get("strategy", "trend")

        # ================= CAPITAL ALLOCATION =================
        size = self.capital_allocator.allocate(
            base_capital=self.base_capital,
            strategy=strategy_name,
            horizon=horizon,
            confidence=score,
            volatility=vol,
            drawdown=drawdown
        )

        print("POSITION SIZE:", size)

        # ================= TP/SL =================
        trade_direction = "LONG" if direction == "BUY" else "SHORT"

        tp, sl = self.tp_sl.generate(trade_direction, price, vol)

        # ================= POSITION CREATION =================
        position = Position(
            direction=trade_direction,
            entry_price=price,
            size=size,
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
        print("HORIZON:", horizon)
        print("SIZE:", size)
