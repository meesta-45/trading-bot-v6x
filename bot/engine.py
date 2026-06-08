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
from bot.ai.market_regime import MarketRegimeAI


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=1000)

        print("🔥 V28 MARKET REGIME AI ACTIVE")

        # =====================================
        # MODE
        # =====================================
        self.mode = ModeController()
        self.mode.set_mode("FOREX")

        # =====================================
        # STRATEGIES
        # =====================================
        self.strategies = {
            "trend": TrendStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy()
        }

        # =====================================
        # AI
        # =====================================
        self.ai = AdaptiveAI()

        self.market_ai = MarketRegimeAI()

        # =====================================
        # PORTFOLIO
        # =====================================
        self.voting = VotingEngine()

        self.capital_allocator = CapitalAllocator()

        self.base_capital = 100

        # =====================================
        # RISK
        # =====================================
        self.vol_engine = VolatilityEngine()

        self.drawdown = DrawdownGuard()

        self.tp_sl = TPSLEngine()

        # =====================================
        # EXECUTION
        # =====================================
        self.positions = PositionManager()

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

        # =====================================
        # CONTROLS
        # =====================================
        self.cooldown = 0
        self.cooldown_limit = 3

        self.max_positions = 2

        self.min_data = 30

    # =====================================================
    # SAFE SCORE
    # =====================================================
    def _safe_score(self, signal):

        if not signal:
            return 0

        # NEW FORMAT
        if "score" in signal:
            return signal["score"]

        # OLD FORMAT SUPPORT
        if "confidence" in signal:

            confidence = signal["confidence"]

            if confidence > 1:
                return confidence / 100

            return confidence

        return 0.5

    # =====================================================
    # POSITION MANAGEMENT
    # =====================================================
    def _manage_positions(self, price):

        for p in list(
            self.positions.active_positions()
        ):

            pnl = 0
            closed = False

            # =====================================
            # LONG
            # =====================================
            if p.direction == "LONG":

                if price >= p.take_profit:

                    pnl = (
                        price - p.entry_price
                    ) * p.size

                    closed = True

                    print("✅ TP LONG")

                elif price <= p.stop_loss:

                    pnl = (
                        price - p.entry_price
                    ) * p.size

                    closed = True

                    print("❌ SL LONG")

                elif self.reversal.detect(
                    list(self.prices)
                ):

                    pnl = (
                        price - p.entry_price
                    ) * p.size

                    closed = True

                    print("⚠ REVERSAL LONG")

            # =====================================
            # SHORT
            # =====================================
            else:

                if price <= p.take_profit:

                    pnl = (
                        p.entry_price - price
                    ) * p.size

                    closed = True

                    print("✅ TP SHORT")

                elif price >= p.stop_loss:

                    pnl = (
                        p.entry_price - price
                    ) * p.size

                    closed = True

                    print("❌ SL SHORT")

                elif self.reversal.detect(
                    list(self.prices)
                ):

                    pnl = (
                        p.entry_price - price
                    ) * p.size

                    closed = True

                    print("⚠ REVERSAL SHORT")

            # =====================================
            # TIME EXIT
            # =====================================
            if p.expired():

                if p.direction == "LONG":

                    pnl = (
                        price - p.entry_price
                    ) * p.size

                else:

                    pnl = (
                        p.entry_price - price
                    ) * p.size

                closed = True

                print("⏰ TIME EXIT")

            # =====================================
            # CLOSE
            # =====================================
            if closed:

                self.balance += pnl

                if pnl > 0:
                    self.wins += 1
                else:
                    self.losses += 1

                self.ai.update_strategy(
                    getattr(
                        p,
                        "strategy",
                        "trend"
                    ),
                    pnl
                )

                self.positions.close_position(p)

                print("\n📊 CLOSED TRADE")

                print(
                    "PNL:",
                    round(pnl, 2)
                )

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
                    round(
                        self.wins / total,
                        2
                    )
                )

    # =====================================================
    # MAIN LOOP
    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)

        print(
            "DATA SIZE:",
            len(self.prices)
        )

        # =====================================
        # MANAGE POSITIONS
        # =====================================
        self._manage_positions(price)

        # =====================================
        # COOLDOWN
        # =====================================
        if self.cooldown > 0:

            self.cooldown -= 1

            print(
                "🧊 COOLDOWN:",
                self.cooldown
            )

            return

        # =====================================
        # WARMUP
        # =====================================
        if len(self.prices) < self.min_data:

            print(
                "⏳ WARMUP:",
                len(self.prices),
                "/",
                self.min_data
            )

            return

        prices = list(self.prices)

        # =====================================
        # MARKET REGIME AI
        # =====================================
        regime = self.market_ai.detect(
            prices
        )

        allowed = (
            self.market_ai.allowed_strategies(
                regime
            )
        )

        print(
            "🌎 MARKET REGIME:",
            regime
        )

        print(
            "✅ ALLOWED:",
            allowed
        )

        # =====================================
        # MAX POSITIONS
        # =====================================
        if len(
            self.positions.active_positions()
        ) >= self.max_positions:

            print(
                "🚫 MAX POSITIONS ACTIVE"
            )

            return

        # =====================================
        # STRATEGY LAYER
        # =====================================
        signals = []

        print(
            "🚀 ENTERING STRATEGY LAYER"
        )

        for name, strat in self.strategies.items():

            # =====================================
            # REGIME FILTER
            # =====================================
            if name not in allowed:

                print(
                    "🚫 BLOCKED:",
                    name
                )

                continue

            print(
                "📊 RUNNING STRATEGY:",
                name
            )

            try:

                signal = strat.generate(
                    prices
                )

            except Exception as e:

                print(
                    "❌ STRATEGY ERROR:",
                    name,
                    str(e)
                )

                continue

            if not signal:

                print(
                    "❌ NO SIGNAL:",
                    name
                )

                continue

            score = self._safe_score(
                signal
            )

            weight = self.ai.weight(
                name
            )

            final_score = (
                score * weight
            )

            print(
                "✔ SIGNAL:",
                name,
                "RAW:",
                round(score, 4),
                "WEIGHT:",
                round(weight, 4),
                "FINAL:",
                round(final_score, 4)
            )

            signals.append({
                "direction":
                    signal["direction"],

                "score":
                    final_score,

                "strategy":
                    name
            })

        print(
            "📡 SIGNAL COUNT:",
            len(signals)
        )

        # =====================================
        # VOTING
        # =====================================
        decision = self.voting.combine(
            signals
        )

        print(
            "🧠 VOTING:",
            decision
        )

        if not decision:

            print(
                "❌ NO DECISION"
            )

            return

        direction = decision["direction"]

        score = decision["score"]

        # =====================================
        # VOLATILITY
        # =====================================
        vol = self.vol_engine.compute(
            [
                prices[i] - prices[i - 1]
                for i in range(
                    1,
                    len(prices)
                )
            ]
        )

        print(
            "📉 VOL:",
            round(vol, 4)
        )

        # =====================================
        # DYNAMIC THRESHOLD
        # =====================================
        threshold = (
            self.ai.confidence_threshold(
                vol,
                regime
            )
        )

        print(
            "🎯 THRESHOLD:",
            round(threshold, 4)
        )

        if score < threshold:

            print(
                "🚫 BELOW THRESHOLD"
            )

            return

        # =====================================
        # ORDER FLOW FILTERS
        # =====================================
        zones = (
            self.orderflow.liquidity_zones(
                prices
            )
        )

        support = zones["support"]

        resistance = zones["resistance"]

        momentum = abs(
            prices[-1] - prices[-5]
        )

        fake_breakout = (
            self.orderflow.fake_breakout(
                price,
                resistance,
                support,
                momentum
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

        quality = (
            self.orderflow.quality_score(
                score,
                vol,
                compression
            )
        )

        print(
            "⭐ QUALITY:",
            round(quality, 4)
        )

        if quality < 0.5:

            print(
                "🚫 LOW QUALITY"
            )

            return

        # =====================================
        # CAPITAL ALLOCATION
        # =====================================
        size = (
            self.capital_allocator.allocate(
                self.base_capital,
                decision.get(
                    "strategy",
                    "trend"
                ),
                regime,
                score,
                vol,
                self.drawdown.drawdown(
                    self.balance
                )
            )
        )

        size *= (
            self.ai.risk_multiplier()
        )

        print(
            "💰 SIZE:",
            round(size, 2)
        )

        # =====================================
        # SLIPPAGE
        # =====================================
        slippage = (
            self.orderflow.slippage(
                vol
            )
        )

        trade_direction = (
            "LONG"
            if direction == "BUY"
            else "SHORT"
        )

        entry = (
            price + slippage
            if trade_direction == "LONG"
            else price - slippage
        )

        # =====================================
        # TP / SL
        # =====================================
        tp, sl = self.tp_sl.generate(
            trade_direction,
            entry,
            vol
        )

        # =====================================
        # HOLD TIME
        # =====================================
        hold_minutes = 1

        if regime == "TRENDING":
            hold_minutes = 5

        elif regime == "VOLATILE":
            hold_minutes = 2

        elif regime == "RANGING":
            hold_minutes = 1

        # =====================================
        # OPEN POSITION
        # =====================================
        position = Position(
            direction=trade_direction,
            entry_price=entry,
            size=size,
            stop_loss=sl,
            take_profit=tp,
            hold_minutes=hold_minutes
        )

        position.strategy = decision.get(
            "strategy",
            "trend"
        )

        self.positions.open_position(
            position
        )

        # =====================================
        # COOLDOWN RESET
        # =====================================
        self.cooldown = (
            self.cooldown_limit
        )

        print("\n🚀 TRADE OPENED")

        print(
            "DIR:",
            trade_direction
        )

        print(
            "ENTRY:",
            round(entry, 4)
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
            "HOLD:",
            hold_minutes,
            "MIN"
        )

        print(
            "BALANCE:",
            round(self.balance, 2)
        )
