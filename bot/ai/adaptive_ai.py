class AdaptiveAI:

    def __init__(self):

        self.strategy_scores = {
            "trend": 1.0,
            "mean_reversion": 1.0,
            "breakout": 1.0
        }

        self.losing_streak = 0

    # =====================================
    # UPDATE STRATEGY PERFORMANCE
    # =====================================
    def update_strategy(
        self,
        strategy,
        pnl
    ):

        if pnl > 0:

            self.strategy_scores[strategy] += 0.05

            self.losing_streak = 0

        else:

            self.strategy_scores[strategy] -= 0.05

            self.losing_streak += 1

        # limits
        self.strategy_scores[strategy] = max(
            0.5,
            min(
                self.strategy_scores[strategy],
                2.0
            )
        )

    # =====================================
    # STRATEGY WEIGHT
    # =====================================
    def weight(self, strategy):

        return self.strategy_scores.get(
            strategy,
            1.0
        )

    # =====================================
    # DYNAMIC CONFIDENCE
    # =====================================
    def confidence_threshold(
        self,
        volatility,
        regime
    ):

        threshold = 0.55

        if volatility > 3:
            threshold += 0.1

        if regime == "SCALP":
            threshold += 0.05

        if self.losing_streak >= 3:
            threshold += 0.1

        return min(threshold, 0.9)

    # =====================================
    # RISK MULTIPLIER
    # =====================================
    def risk_multiplier(self):

        if self.losing_streak >= 5:
            return 0.4

        if self.losing_streak >= 3:
            return 0.6

        return 1.0
