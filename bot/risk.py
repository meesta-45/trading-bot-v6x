class RiskManager:

    def __init__(self, max_trades=20):
        self.trades = 0
        self.max_trades = max_trades
        self.daily_pnl = 0

    def allow(self, signal):

        if signal == "NO_TRADE":
            return False

        if self.trades >= self.max_trades:
            return False

        if self.daily_pnl <= -50:
            return False

        return True

    def update(self, result):

        self.trades += 1

        if result == "WIN":
            self.daily_pnl += 10
        else:
            self.daily_pnl -= 10
