class PerformanceTracker:

    def __init__(self):

        self.stats = {
            "trend": {"wins": 0, "losses": 0},
            "mean_reversion": {"wins": 0, "losses": 0},
            "breakout": {"wins": 0, "losses": 0}
        }

    def record(self, strategy, win):

        if win:
            self.stats[strategy]["wins"] += 1
        else:
            self.stats[strategy]["losses"] += 1

    def performance(self):

        perf = {}

        for k, v in self.stats.items():

            total = v["wins"] + v["losses"]

            if total == 0:
                perf[k] = 0
            else:
                perf[k] = v["wins"] / total

        return perf
