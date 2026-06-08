class SelfLearningAI:

    def __init__(self):

        self.stats = {
            "trend": {"wins": 0, "losses": 0, "pnl": 0},
            "mean_reversion": {"wins": 0, "losses": 0, "pnl": 0},
            "breakout": {"wins": 0, "losses": 0, "pnl": 0}
        }

        self.min_weight = 0.2
        self.max_weight = 2.5

    # =====================================
    # UPDATE AFTER TRADE
    # =====================================
    def update(self, strategy, pnl):

        if strategy not in self.stats:
            return

        if pnl > 0:
            self.stats[strategy]["wins"] += 1
        else:
            self.stats[strategy]["losses"] += 1

        self.stats[strategy]["pnl"] += pnl

    # =====================================
    # PERFORMANCE SCORE
    # =====================================
    def performance_score(self, strategy):

        data = self.stats.get(strategy, None)

        if not data:
            return 1.0

        total = data["wins"] + data["losses"]

        if total == 0:
            return 1.0

        winrate = data["wins"] / total

        avg_pnl = data["pnl"] / max(total, 1)

        score = (winrate * 0.7) + (avg_pnl * 0.3)

        return score

    # =====================================
    # DYNAMIC WEIGHT
    # =====================================
    def weight(self, strategy):

        score = self.performance_score(strategy)

        weight = 1 + (score - 0.5) * 2

        weight = max(self.min_weight, min(self.max_weight, weight))

        return round(weight, 3)
