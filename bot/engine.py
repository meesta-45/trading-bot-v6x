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

        # ==============================
        # V22 INTELLIGENCE CONTROLS
        # ==============================
        self.trade_count = 0
        self.cooldown = 0

        self.cooldown_limit = 5
        self.trade_batch_limit = 8
        self.batch_profit_target = 40

        self.batch_profit = 0

    # ==============================
    # MARKET MODE SWITCH
    # ==============================
    def set_market_mode(self, mode):
        self.mode.set_mode(mode)

    # ==============================
    # POSITION ANALYSIS
    # ==============================
    def _manage_positions(self, price):

        for position in list(self.positions.active_positions()):

            # LONG
