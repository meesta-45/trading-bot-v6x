from collections import deque

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

        # ================= CORE =================
        self.mode = ModeController()
        self.mode.set_mode("FOREX")

        self.regime = MarketRegime()

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

        self.balance = 10000

    # =====================================================
    # MICRO REGIME DETECTOR (KEY FIX)
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
    # HORIZON CLASSIFIER (FIXED MULTI-SPEED)
    # =====================================================
    def classify_horizon(self, vol, score, prices):

        regime = self.micro_regime(prices)

        # ================= SCALP =================
        if regime == "SCALP":

            if score < 0.55:
                return "SCALP_5S"

            if score < 0.6:
                return "SCALP_15S"

            if score < 0.7:
                return "SCALP_30S"

            return "SCALP_1M"

        # ================= STRUCTURE =================
        if regime == "STRUCTURE":
            return "SHORT_5M"

        # ================= SWING =================
        return "SWING_15M"

    # =====================================================
    # HOLD TIME MAP
    # =====================================================
    def horizon_to_minutes(self, horizon):

        if horizon == "SCALP_5S":
            return 0.083

        if horizon == "SCALP_15S":
            return 0.25

        if horizon == "SCALP_30S":
            return 0.5

        if horizon == "SCALP_1M":
            return 1

        if horizon == "SHORT_5M":
            return 5

        return 15

    # =====================================================
    # POSITION MANAGEMENT
    # =====================================================
    def _manage_positions(self, price):

        for position in list(self.positions.active_positions()):

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
                    print("⚠ REVERSAL LONG")
                    self.positions.close_position(position)

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
                    print("⚠ REVERSAL SHORT")
                    self.positions.close_position(position)

            if position.expired():
                print("⏰ TIME EXIT")
                self.positions.close_position(position)

    # =====================================================
    # MAIN ENGINE
    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        self._manage_positions(price)

        if len(self.prices) < 120:
            print("WARMUP:", len(self.prices))
            return

        prices = list(self.prices)

        # ================= LIMIT =================
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

        # ================= MICRO DECISION =================
        horizon = self.classify_horizon(vol, score, prices)

        hold_minutes = self.horizon_to_minutes(horizon)

        print("\nMICRO REGIME:", self.micro_regime(prices))
        print("HORIZON:", horizon)
        print("HOLD TIME:", hold_minutes)

        # ================= RISK =================
        drawdown = self.drawdown.drawdown(self.balance)

        strategy_name = decision.get("strategy", "trend")

        # ================= SIZE =================
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
        print("HORIZON:", horizon)
        print("SIZE:", size)
