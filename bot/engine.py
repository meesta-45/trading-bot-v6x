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

from bot.orderflow.orderflow_engine import OrderFlowEngine

from bot.ai.adaptive_ai import AdaptiveAI


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=1000)

        self.mode = ModeController()
        self.mode.set_mode("FOREX")

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()

        self.ai = AdaptiveAI()

        self.capital_allocator = CapitalAllocator()
        self.base_capital = 100

        self.positions = PositionManager()

        self.vol_engine = VolatilityEngine()
        self.drawdown = DrawdownGuard()
        self.tp_sl = TPSLEngine()

        self.reversal = ReversalDetector()
        self.orderflow = OrderFlowEngine()

        self.balance = 10000

        self.wins = 0
        self.losses = 0

        self.cooldown = 0
        self.cooldown_limit = 5
        self.max_positions = 2

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
    def classify_horizon(self, vol, score, prices):

        regime = self.micro_regime(prices)

        if regime == "SCALP":

            if score < 0.55:
                return "SCALP_5S"

            if score < 0.60:
                return "SCALP_15S"

            if score < 0.70:
                return "SCALP_30S"

            return "SCALP_1M"

        if regime == "STRUCTURE":
            return "SHORT_5M"

        return "SWING_15M"

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
    def _safe_signal_score(self, signal):

        if not signal:
            return None

        if "score" in signal:
            return signal["score"]

        if "confidence" in signal:
            return signal["confidence"]

        return 0.55

    # =====================================================
    def _manage_positions(self, price):

        for position in list(self.positions.active_positions()):

            pnl = 0
            closed = False

            if position.direction == "LONG":

                if price >= position.take_profit:
                    pnl = (price - position.entry_price) * position.size
                    closed = True
                    print("✅ TP LONG")

                elif price <= position.stop_loss:
                    pnl = (price - position.entry_price) * position.size
                    closed = True
                    print("❌ SL LONG")

                elif self.reversal.detect(list(self.prices)):
                    pnl = (price - position.entry_price) * position.size
                    closed = True
                    print("⚠ REVERSAL LONG")

            else:

                if price <= position.take_profit:
                    pnl = (position.entry_price - price) * position.size
                    closed = True
                    print("✅ TP SHORT")

                elif price >= position.stop_loss:
                    pnl = (position.entry_price - price) * position.size
                    closed = True
                    print("❌ SL SHORT")

                elif self.reversal.detect(list(self.prices)):
                    pnl = (position.entry_price - price) * position.size
                    closed = True
                    print("⚠ REVERSAL SHORT")

            if position.expired():
                pnl = (
                    (price - position.entry_price)
                    if position.direction == "LONG"
                    else (position.entry_price - price)
                ) * position.size
                closed = True
                print("⏰ TIME EXIT")

            if closed:

                self.balance += pnl

                if pnl > 0:
                    self.wins += 1
                else:
                    self.losses += 1

                self.ai.update_strategy(
                    getattr(position, "strategy", "trend"),
                    pnl
                )

                self.positions.close_position(position)

                print("📊 CLOSED TRADE")
                print("PNL:", round(pnl, 2))
                print("BALANCE:", round(self.balance, 2))

    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        self._manage_positions(price)

        if self.cooldown > 0:
            self.cooldown -= 1
            print("COOLDOWN:", self.cooldown)
            return

        if len(self.prices) < 120:
            return

        if len(self.positions.active_positions()) >= self.max_positions:
            return

        prices = list(self.prices)

        signals = []

        # =====================================================
        # STRATEGY ENGINE (SAFE)
        # =====================================================
        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            if not signal:
                continue

            score = self._safe_signal_score(signal)

            weight = self.ai.weight(name)

            signal["score"] = score * weight
            signal["strategy"] = name

            signals.append(signal)

            print("AI WEIGHT:", name, round(weight, 2))

        decision = self.voting.combine(signals)

        print("VOTING:", decision)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        vol = self.vol_engine.compute(
            [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        )

        threshold = self.ai.confidence_threshold(
            vol,
            self.micro_regime(prices)
        )

        print("THRESHOLD:", threshold)

        if score < threshold:
            print("LOW CONFIDENCE SKIP")
            return

        zones = self.orderflow.liquidity_zones(prices)

        support = zones["support"]
        resistance = zones["resistance"]

        momentum = abs(prices[-1] - prices[-5])

        if self.orderflow.fake_breakout(
            price,
            resistance,
            support,
            momentum
        ):
            print("FAKE BREAKOUT SKIP")
            return

        compression = self.orderflow.compression(prices)

        quality = self.orderflow.quality_score(
            score,
            vol,
            compression
        )

        if quality < 0.6:
            print("LOW QUALITY SKIP")
            return

        horizon = self.classify_horizon(vol, score, prices)
        hold = self.horizon_to_minutes(horizon)

        size = self.capital_allocator.allocate(
            self.base_capital,
            decision.get("strategy", "trend"),
            horizon,
            score,
            vol,
            self.drawdown.drawdown(self.balance)
        )

        size *= self.ai.risk_multiplier()

        slippage = self.orderflow.slippage(vol)

        entry = price + slippage if direction == "BUY" else price - slippage

        tp, sl = self.tp_sl.generate(direction, entry, vol)

        position = Position(
            direction="LONG" if direction == "BUY" else "SHORT",
            entry_price=entry,
            size=size,
            stop_loss=sl,
            take_profit=tp,
            hold_minutes=hold
        )

        position.strategy = decision.get("strategy", "trend")

        self.positions.open_position(position)

        self.cooldown = self.cooldown_limit

        print("🚀 TRADE OPENED")
        print("DIR:", position.direction)
        print("ENTRY:", entry)
        print("TP:", tp)
        print("SL:", sl)
        print("SIZE:", size)
        print("BALANCE:", self.balance)
