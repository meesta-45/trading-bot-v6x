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
from bot.ai.self_learning_ai import SelfLearningAI

from bot.execution.institutional_execution import InstitutionalExecution


class Engine:

    def __init__(self):

        self.prices = deque(maxlen=1000)

        print("🔥 V30 INSTITUTIONAL EXECUTION ENGINE ACTIVE")

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
        # AI SYSTEMS
        # =====================================
        self.ai = AdaptiveAI()
        self.market_ai = MarketRegimeAI()
        self.learning_ai = SelfLearningAI()

        # =====================================
        # EXECUTION ENGINE (NEW V30 CORE)
        # =====================================
        self.execution = InstitutionalExecution()

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
        # EXECUTION / ANALYSIS
        # =====================================
        self.positions = PositionManager()
        self.reversal = ReversalDetector()
        self.orderflow = OrderFlowEngine()

        # =====================================
        # ACCOUNT STATE
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
    def _safe_score(self, signal):

        if not signal:
            return 0

        if "score" in signal:
            return signal["score"]

        if "confidence" in signal:
            c = signal["confidence"]
            return c / 100 if c > 1 else c

        return 0.5

    # =====================================================
    def _manage_positions(self, price):

        for p in list(self.positions.active_positions()):

            pnl = 0
            closed = False

            if p.direction == "LONG":

                if price >= p.take_profit:
                    pnl = (price - p.entry_price) * p.size
                    closed = True
                    print("✅ TP LONG")

                elif price <= p.stop_loss:
                    pnl = (price - p.entry_price) * p.size
                    closed = True
                    print("❌ SL LONG")

                elif self.reversal.detect(list(self.prices)):
                    pnl = (price - p.entry_price) * p.size
                    closed = True
                    print("⚠ REVERSAL LONG")

            else:

                if price <= p.take_profit:
                    pnl = (p.entry_price - price) * p.size
                    closed = True
                    print("✅ TP SHORT")

                elif price >= p.stop_loss:
                    pnl = (p.entry_price - price) * p.size
                    closed = True
                    print("❌ SL SHORT")

                elif self.reversal.detect(list(self.prices)):
                    pnl = (p.entry_price - price) * p.size
                    closed = True
                    print("⚠ REVERSAL SHORT")

            if p.expired():
                pnl = (price - p.entry_price) * p.size if p.direction == "LONG" else (p.entry_price - price) * p.size
                closed = True
                print("⏰ TIME EXIT")

            if closed:

                self.balance += pnl

                if pnl > 0:
                    self.wins += 1
                else:
                    self.losses += 1

                strategy = getattr(p, "strategy", "trend")

                self.learning_ai.update(strategy, pnl)
                self.ai.update_strategy(strategy, pnl)

                self.positions.close_position(p)

                print("\n📊 CLOSED TRADE")
                print("STRATEGY:", strategy)
                print("PNL:", round(pnl, 2))
                print("BALANCE:", round(self.balance, 2))

    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)
        print("DATA SIZE:", len(self.prices))

        self._manage_positions(price)

        if self.cooldown > 0:
            self.cooldown -= 1
            print("🧊 COOLDOWN:", self.cooldown)
            return

        if len(self.prices) < self.min_data:
            print("⏳ WARMUP:", len(self.prices), "/", self.min_data)
            return

        prices = list(self.prices)

        # =====================================
        # MARKET REGIME
        # =====================================
        regime = self.market_ai.detect(prices)
        allowed = self.market_ai.allowed_strategies(regime)

        print("🌎 REGIME:", regime)
        print("✅ ALLOWED:", allowed)

        if len(self.positions.active_positions()) >= self.max_positions:
            print("🚫 MAX POSITIONS")
            return

        # =====================================
        # STRATEGY LAYER
        # =====================================
        signals = []

        print("🚀 STRATEGY LAYER")

        for name, strat in self.strategies.items():

            if name not in allowed:
                print("🚫 BLOCKED:", name)
                continue

            print("📊 RUN:", name)

            try:
                signal = strat.generate(prices)
            except Exception as e:
                print("❌ ERROR:", name, e)
                continue

            if not signal:
                print("❌ NO SIGNAL:", name)
                continue

            score = self._safe_score(signal)

            weight = self.learning_ai.weight(name)

            final_score = score * weight

            print(
                "✔ SIGNAL:",
                name,
                "SCORE:",
                round(score, 4),
                "WEIGHT:",
                round(weight, 3),
                "FINAL:",
                round(final_score, 4)
            )

            signals.append({
                "direction": signal["direction"],
                "score": final_score,
                "strategy": name
            })

        print("📡 SIGNALS:", len(signals))

        decision = self.voting.combine(signals)

        print("🧠 VOTING:", decision)

        if not decision:
            return

        direction = decision["direction"]
        score = decision["score"]

        vol = self.vol_engine.compute(
            [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        )

        threshold = self.ai.confidence_threshold(vol, regime)

        print("🎯 THRESHOLD:", round(threshold, 4))

        if score < threshold:
            print("🚫 BELOW THRESHOLD")
            return

        zones = self.orderflow.liquidity_zones(prices)

        momentum = abs(prices[-1] - prices[-5])

        if self.orderflow.fake_breakout(price, zones["resistance"], zones["support"], momentum):
            print("🚫 FAKE BREAKOUT")
            return

        compression = self.orderflow.compression(prices)

        quality = self.orderflow.quality_score(score, vol, compression)

        if quality < 0.5:
            print("🚫 LOW QUALITY")
            return

        size = self.base_capital

        # =====================================
        # V30 INSTITUTIONAL EXECUTION (NEW CORE)
        # =====================================
        trade_direction = "LONG" if direction == "BUY" else "SHORT"

        exec_result = self.execution.execute(
            price=price,
            direction=trade_direction,
            volatility=vol,
            size=size
        )

        entry = exec_result["fill_price"]
        spread = exec_result["spread"]
        slippage = exec_result["slippage"]
        delay = exec_result["delay"]
        fill_quality = exec_result["fill_quality"]

        tp, sl = self.tp_sl.generate(trade_direction, entry, vol)

        position = Position(
            direction=trade_direction,
            entry_price=entry,
            size=size,
            stop_loss=sl,
            take_profit=tp,
            hold_minutes=1
        )

        position.strategy = decision.get("strategy", "trend")

        self.positions.open_position(position)

        self.cooldown = self.cooldown_limit

        print("\n🚀 TRADE OPENED")

        print("DIR:", trade_direction)
        print("ENTRY:", round(entry, 4))
        print("TP:", round(tp, 4))
        print("SL:", round(sl, 4))

        print("📉 SPREAD:", round(spread, 6))
        print("⚡ SLIPPAGE:", round(slippage, 6))
        print("⏱ DELAY:", delay)
        print("🏷 FILL QUALITY:", fill_quality)

        print("BALANCE:", round(self.balance, 2))
