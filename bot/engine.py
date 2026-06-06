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

        # =====================================
        # CORE
        # =====================================
        self.mode = ModeController()
        self.mode.set_mode("FOREX")

        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        self.voting = VotingEngine()

        # =====================================
        # AI ENGINE
        # =====================================
        self.ai = AdaptiveAI()

        # =====================================
        # PORTFOLIO
        # =====================================
        self.capital_allocator = CapitalAllocator()

        self.base_capital = 100

        self.positions = PositionManager()

        # =====================================
        # RISK
        # =====================================
        self.vol_engine = VolatilityEngine()

        self.drawdown = DrawdownGuard()

        self.tp_sl = TPSLEngine()

        # =====================================
        # ANALYSIS
        # =====================================
        self.reversal = ReversalDetector()

        self.orderflow = OrderFlowEngine()

        # =====================================
        # ACCOUNT
        # =====================================
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
    # HORIZON CLASSIFICATION
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
    # HOLD TIME MAPPING
    # =====================================================
    def horizon_to_minutes(self, horizon):

        mapping = {
            "SCALP_5S": 0.083,
            "SCALP_15S": 0.25,
            "SCALP_30S": 0.5,
            "SCALP_1M": 1,
            "SHORT_5M": 5,
            "SWING_15M": 15
        }

        return mapping.get(horizon, 5)

    # =====================================================
    # POSITION MANAGEMENT
    # =====================================================
    def _manage_positions(self, price):

        for position in list(
            self.positions.active_positions()
        ):

            closed = False
            pnl = 0

            # =====================================
            # LONG
            # =====================================
            if position.direction == "LONG":

                if price >= position.take_profit:

                    pnl = (
                        price - position.entry_price
                    ) * position.size

                    closed = True

                    print("✅ TP LONG")

                elif price <= position.stop_loss:

                    pnl = (
                        price - position.entry_price
                    ) * position.size

                    closed = True

                    print("❌ SL LONG")

                elif self.reversal.detect(
                    list(self.prices)
                ):

                    pnl = (
                        price - position.entry_price
                    ) * position.size

                    closed = True

                    print("⚠ REVERSAL EXIT LONG")

            # =====================================
            # SHORT
            # =====================================
            else:

                if price <= position.take_profit:

                    pnl = (
                        position.entry_price - price
                    ) * position.size

                    closed = True

                    print("✅ TP SHORT")

                elif price >= position.stop_loss:

                    pnl = (
                        position.entry_price - price
                    ) * position.size

                    closed = True

                    print("❌ SL SHORT")

                elif self.reversal.detect(
                    list(self.prices)
                ):

                    pnl = (
                        position.entry_price - price
                    ) * position.size

                    closed = True

                    print("⚠ REVERSAL EXIT SHORT")

            # =====================================
            # TIME EXIT
            # =====================================
            if position.expired():

                if position.direction == "LONG":

                    pnl = (
                        price - position.entry_price
                    ) * position.size

                else:

                    pnl = (
                        position.entry_price - price
                    ) * position.size

                closed = True

                print("⏰ TIME EXIT")

            # =====================================
            # CLOSE POSITION
            # =====================================
            if closed:

                self.balance += pnl

                if pnl > 0:
                    self.wins += 1
                else:
                    self.losses += 1

                strategy = getattr(
                    position,
                    "strategy",
                    "trend"
                )

                self.ai.update_strategy(
                    strategy,
                    pnl
                )

                self.positions.close_position(
                    position
                )

                print("\n📊 TRADE CLOSED")
                print("PNL:", round(pnl, 2))
                print(
                    "BALANCE:",
                    round(self.balance, 2)
                )

                total = max(
                    self.wins + self.losses,
                    1
                )

                print(
                    "WIN RATE:",
                    round(self.wins / total, 2)
                )

                print(
                    "AI SCORE:",
                    strategy,
                    round(
                        self.ai.weight(strategy),
                        2
                    )
                )

    # =====================================================
    # MAIN ENGINE LOOP
    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        # =====================================
        # MANAGE POSITIONS
        # =====================================
        self._manage_positions(price)

        # =====================================
        # COOLDOWN
        # =====================================
        if self.cooldown > 0:

            print(
                "🧊 COOLDOWN:",
                self.cooldown
            )

            self.cooldown -= 1

            return

        # =====================================
        # WARMUP
        # =====================================
        if len(self.prices) < 120:

            print(
                "WARMUP:",
                len(self.prices)
            )

            return

        prices = list(self.prices)

        # =====================================
        # MAX POSITIONS
        # =====================================
        if len(
            self.positions.active_positions()
        ) >= self.max_positions:

            print("MAX POSITIONS ACTIVE")

            return

        # =====================================
        # STRATEGY SIGNALS
        # =====================================
        signals = []

        for name, strat in self.strategies.items():

            signal = strat.generate(prices)

            if signal:

                signal["strategy"] = name

                weight = self.ai.weight(name)

                signal["score"] *= weight

                print(
                    "AI WEIGHT:",
                    name,
                    round(weight, 2)
                )

                signals.append(signal)

        decision = self.voting.combine(signals)

        print("VOTING:", decision)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        # =====================================
        # VOLATILITY
        # =====================================
        vol = self.vol_engine.compute(
            [
                prices[i] - prices[i - 1]
                for i in range(1, len(prices))
            ]
        )

        print("VOL:", round(vol, 4))

        # =====================================
        # DYNAMIC THRESHOLD
        # =====================================
        dynamic_threshold = (
            self.ai.confidence_threshold(
                vol,
                self.micro_regime(prices)
            )
        )

        print(
            "DYNAMIC THRESHOLD:",
            dynamic_threshold
        )

        if score < dynamic_threshold:

            print("🚫 LOW CONFIDENCE")

            return

        # =====================================
        # ORDER FLOW
        # =====================================
        zones = self.orderflow.liquidity_zones(
            prices
        )

        support = zones["support"]
        resistance = zones["resistance"]

        print(
            "SUPPORT:",
            round(support, 4)
        )

        print(
            "RESISTANCE:",
            round(resistance, 4)
        )

        momentum = abs(
            prices[-1] - prices[-5]
        )

        fake_breakout = (
            self.orderflow.fake_breakout(
                current_price=price,
                resistance=resistance,
                support=support,
                momentum=momentum
            )
        )

        if fake_breakout:

            print(
                "🚫 FAKE BREAKOUT"
            )

            return

        compression = (
            self.orderflow.compression(
                prices
            )
        )

        print(
            "COMPRESSION:",
            compression
        )

        quality = (
            self.orderflow.quality_score(
                confidence=score,
                volatility=vol,
                compression=compression
            )
        )

        print(
            "QUALITY:",
            quality
        )

        if quality < 0.6:

            print(
                "🚫 LOW QUALITY"
            )

            return

        # =====================================
        # HORIZON
        # =====================================
        horizon = self.classify_horizon(
            vol,
            score,
            prices
        )

        hold_minutes = (
            self.horizon_to_minutes(
                horizon
            )
        )

        print(
            "\nMICRO REGIME:",
            self.micro_regime(prices)
        )

        print("HORIZON:", horizon)

        print("HOLD:", hold_minutes)

        # =====================================
        # CAPITAL ALLOCATION
        # =====================================
        drawdown = self.drawdown.drawdown(
            self.balance
        )

        strategy_name = decision.get(
            "strategy",
            "trend"
        )

        size = (
            self.capital_allocator.allocate(
                base_capital=self.base_capital,
                strategy=strategy_name,
                horizon=horizon,
                confidence=score,
                volatility=vol,
                drawdown=drawdown
            )
        )

        # =====================================
        # AI RISK CONTROL
        # =====================================
        risk_multiplier = (
            self.ai.risk_multiplier()
        )

        size *= risk_multiplier

        print(
            "RISK MULTIPLIER:",
            risk_multiplier
        )

        print(
            "SIZE:",
            round(size, 2)
        )

        # =====================================
        # SLIPPAGE
        # =====================================
        slippage = self.orderflow.slippage(
            vol
        )

        print(
            "SLIPPAGE:",
            slippage
        )

        trade_direction = (
            "LONG"
            if direction == "BUY"
            else "SHORT"
        )

        adjusted_entry = (
            price + slippage
            if trade_direction == "LONG"
            else price - slippage
        )

        # =====================================
        # TP / SL
        # =====================================
        tp, sl = self.tp_sl.generate(
            trade_direction,
            adjusted_entry,
            vol
        )

        # =====================================
        # EXECUTION
        # =====================================
        position = Position(
            direction=trade_direction,
            entry_price=adjusted_entry,
            size=size,
            stop_loss=sl,
            take_profit=tp,
            hold_minutes=hold_minutes
        )

        position.strategy = strategy_name

        self.positions.open_position(
            position
        )

        # =====================================
        # COOLDOWN RESET
        # =====================================
        self.cooldown = self.cooldown_limit

        print("\n🚀 POSITION OPENED")

        print(
            "DIR:",
            trade_direction
        )

        print(
            "ENTRY:",
            round(adjusted_entry, 4)
        )

        print(
            "TP:",
            round(tp, 4)
        )

        print(
            "SL:",
            round(sl, 4)
        )

        print(
            "SIZE:",
            round(size, 2)
        )

        print(
            "BALANCE:",
            round(self.balance, 2)
        )
