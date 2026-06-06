from collections import deque

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

        # ================= CORE =================
        self.mode = ModeController()
        self.mode.set_mode("FOREX")

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()

        # ================= PORTFOLIO =================
        self.capital_allocator = CapitalAllocator()
        self.base_capital = 100
        self.positions = PositionManager()

        # ================= RISK =================
        self.vol_engine = VolatilityEngine()
        self.drawdown = DrawdownGuard()
        self.tp_sl = TPSLEngine()
        self.reversal = ReversalDetector()

        # ================= ACCOUNT =================
        self.balance = 10000

        # ================= CONTROL =================
        self.cooldown = 0
        self.cooldown_limit = 5
        self.max_positions = 2

        # performance tracking hooks (for v25 PnL engine)
        self.wins = 0
        self.losses = 0

    # =====================================================
    # MICRO REGIME DETECTOR
    # =====================================================
    def micro_regime(self, prices):

        if len(prices) < 20:
            return "SWING"

        recent = prices[-10:]

        changes = [
            abs(recent[i] - recent[i - 1])
            for i in range(1, len(recent))
        ]

        avg_move = sum(changes) / len(changes)

        noise = len([
            x for x in changes
            if x < avg_move * 0.5
        ]) / len(changes)

        momentum = abs(recent[-1] - recent[0])

        if noise > 0.6 and avg_move > 0.5:
            return "SCALP"

        if momentum > avg_move * 3:
            return "STRUCTURE"

        return "SWING"

    # =====================================================
    # HORIZON SELECTION ENGINE (FIXED MULTI-SPEED)
    # =====================================================
    def classify_horizon(self, vol, score, prices):

        regime = self.micro_regime(prices)

        # ---------------- SCALP ----------------
        if regime == "SCALP":

            if score < 0.55:
                return "SCALP_5S"

            if score < 0.6:
                return "SCALP_15S"

            if score < 0.7:
                return "SCALP_30S"

            return "SCALP_1M"

        # ---------------- STRUCTURE ----------------
        if regime == "STRUCTURE":
            return "SHORT_5M"

        # ---------------- SWING ----------------
        return "SWING_15M"

    # =====================================================
    # HOLD TIME MAPPING
    # =====================================================
    def horizon_to_minutes(self, horizon):

        return {
            "SCALP_5S": 0.083,
            "SCALP_15S": 0.25,
            "SCALP_30S": 0.5,
            "SCALP_1M": 1,
            "SHORT_5M": 5,
            "SWING_15M": 15
        }.get(horizon, 5)

    # =====================================================
    # POSITION MANAGEMENT
    # NOTE: PnL integration will be completed in V25
    # =====================================================
    def _manage_positions(self, price):

        for position in list(self.positions.active_positions()):

            # LONG
            if position.direction == "LONG":

                if price >= position.take_profit:
                    print("✅ TP LONG")
                    self.balance += 20
                    self.positions.close_position(position)

                elif price <= position.stop_loss:
                    print("❌ SL LONG")
                    self.balance -= 15
                    self.positions.close_position(position)

                elif self.reversal.detect(list(self.prices)):
                    print("⚠ REVERSAL EXIT LONG")
                    self.positions.close_position(position)

            # SHORT
            else:

                if price <= position.take_profit:
                    print("✅ TP SHORT")
                    self.balance += 20
                    self.positions.close_position(position)

                elif price >= position.stop_loss:
                    print("❌ SL SHORT")
                    self.balance -= 15
                    self.positions.close_position(position)

                elif self.reversal.detect(list(self.prices)):
                    print("⚠ REVERSAL EXIT SHORT")
                    self.positions.close_position(position)

            # TIME EXIT
            if position.expired():
                print("⏰ TIME EXIT")
                self.positions.close_position(position)

    # =====================================================
    # MAIN ENGINE LOOP
    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        # manage existing trades first
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

        # ================= LIMIT POSITIONS =================
        if len(self.positions.active_positions()) >= self.max_positions:
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

        # ================= HORIZON DECISION =================
        horizon = self.classify_horizon(vol, score, prices)

        hold_minutes = self.horizon_to_minutes(horizon)

        print("\nMICRO REGIME:", self.micro_regime(prices))
        print("HORIZON:", horizon)
        print("HOLD:", hold_minutes)

        # ================= CAPITAL ALLOCATION =================
        drawdown = self.drawdown.drawdown(self.balance)

        strategy_name = decision.get("strategy", "trend")

        size = self.capital_allocator.allocate(
            base_capital=self.base_capital,
            strategy=strategy_name,
            horizon=horizon,
            confidence=score,
            volatility=vol,
            drawdown=drawdown
        )

        trade_direction = "LONG" if direction == "BUY" else "SHORT"

        tp, sl = self.tp_sl.generate(trade_direction, price, vol)

        # ================= EXECUTION =================
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
        print("SIZE:", size)
