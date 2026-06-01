class PnLTracker:

    def __init__(self):

        self.data = {
            "trend": [],
            "mean_reversion": [],
            "breakout": []
        }

    def record(self, strategy, pnl):

        if strategy not in self.data:
            self.data[strategy] = []

        self.data[strategy].append(pnl)

    def avg_pnl(self, strategy):

        values = self.data.get(strategy, [])

        if not values:
            return 0

        return sum(values) / len(values)
