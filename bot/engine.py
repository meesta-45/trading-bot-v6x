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

        print("🔥 V27 ENGINE ACTIVE")

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

        # =====================================
        # CONTROL SYSTEM (IMPORTANT FIX)
        # =====================================
        self.cooldown = 0
        self.cooldown_limit = 3

        self.max_positions = 2

        # prevents infinite warmup blocking
        self.min_data = 30

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

        noise = len([x for x in changes if x < avg_move * 0.5]) / len(changes)

        momentum = abs(recent[-1] - recent[0])

        if noise > 0.6:
            return "SCALP"

        if momentum > avg_move * 3:
            return "STRUCTURE"

        return "SWING"

    # =====================================================
    def _safe_score(self, signal):

        if not signal:
            return None

        if "score" in signal:
            return signal["score"]

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

                self.ai.update_strategy(getattr(p, "strategy", "trend"), pnl)

                self.positions.close_position(p)

                print("📊 CLOSED TRADE")
                print("PNL:", round(pnl, 2))
                print("BAL:", round(self.balance, 2))

    # =====================================================
    def on_price(self, price):

        self.prices.append(price)

        print("\nLIVE PRICE:", price)
        print("DATA SIZE:", len(self.prices))

        # ALWAYS manage positions
        self._manage_positions(price)

        # cooldown logic
        if self.cooldown > 0:
            self.cooldown -= 1
            print("🧊 COOLDOWN:", self.cooldown)
            return

        # =====================================
        # IMPORTANT FIX: DO NOT BLOCK TOO HARD
        # =====================================
        if len(self.prices) < self.min_data:
            print("⏳ WARMUP MODE:", len(self.prices), "/", self.min_data)
            return

        prices = list(self.prices)

        # =====================================
        # STRATEGY EXECUTION VISIBILITY FIX
        # =====================================
        signals = []

        print("🚀 ENTERING STRATEGY LAYER")

        for name, strat in self.strategies.items():

            print("📊 RUNNING STRATEGY:", name)

            signal = strat.generate(prices)

            if not signal:
                print("❌ NO SIGNAL:", name)
                continue

            score = self._safe_score(signal)

            weight = self.ai.weight(name)

            final_score = score * weight

            print(
                "✔ SIGNAL:",
                name,
                "RAW:",
                score,
                "WEIGHT:",
                weight,
                "FINAL:",
                round(final_score, 3)
            )

            signals.append({
                "direction": signal["direction"],
                "score": final_score,
                "strategy": name
            })

        print("📡 SIGNAL COUNT:", len(signals))

        decision = self.voting.combine(signals)

        print("🧠 VOTING RESULT:", decision)

        if not decision:
            print("❌ NO DECISION FROM VOTING")
            return

        direction = decision["direction"]
        score = decision["score"]

        # =====================================
        # VOLATILITY
        # =====================================
        vol = self.vol_engine.compute(
            [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        )

        print("📉 VOL:", vol)

        threshold = self.ai.confidence_threshold(vol, self.micro_regime(prices))

        print("🎯 THRESHOLD:", threshold)

        if score < threshold:
            print("❌ BELOW THRESHOLD")
            return

        # =====================================
        # ORDERFLOW FILTERS
        # =====================================
        zones = self.orderflow.liquidity_zones(prices)

        momentum = abs(prices[-1] - prices[-5])

        if self.orderflow.fake_breakout(price, zones["resistance"], zones["support"], momentum):
            print("🚫 FAKE BREAKOUT")
            return

        compression = self.orderflow.compression(prices)

        quality = self.orderflow.quality_score(score, vol, compression)

        print("⭐ QUALITY:", quality)

        if quality < 0.5:
            print("❌ LOW QUALITY SKIP")
            return

        # =====================================
        # EXECUTION ALWAYS REACHES HERE NOW
        # =====================================
        trade_direction = "LONG" if direction == "BUY" else "SHORT"

        slippage = self.orderflow.slippage(vol)

        entry = price + slippage if trade_direction == "LONG" else price - slippage

        tp, sl = self.tp_sl.generate(trade_direction, entry, vol)

        position = Position(
            direction=trade_direction,
            entry_price=entry,
            size=1,
            stop_loss=sl,
            take_profit=tp,
            hold_minutes=1
        )

        position.strategy = decision.get("strategy", "trend")

        self.positions.open_position(position)

        self.cooldown = self.cooldown_limit

        print("🚀 TRADE OPENED")
        print("DIR:", trade_direction)
        print("ENTRY:", entry)
        print("TP:", tp)
        print("SL:", sl)
        print("BAL:", self.balance)
