class CapitalAllocator:

    def __init__(self):

        self.strategy_weights = {
            "trend": 1.0,
            "mean_reversion": 1.0,
            "breakout": 1.0
        }

    # =====================================
    # UPDATE STRATEGY PERFORMANCE WEIGHTS
    # =====================================
    def update_weights(self, alpha_scores):

        for k, v in alpha_scores.items():

            if k in self.strategy_weights:

                # normalize into safe range
                self.strategy_weights[k] = max(
                    0.5,
                    min(2.0, v / 20)
                )

    # =====================================
    # HORIZON WEIGHTING
    # =====================================
    def horizon_weight(self, horizon):

        if horizon == "SCALP_30S":
            return 0.3

        if horizon == "SCALP_45S":
            return 0.5

        if horizon == "SHORT_5M":
            return 0.8

        return 1.2  # SWING_15M

    # =====================================
    # FINAL POSITION SIZE
    # =====================================
    def allocate(
        self,
        base_capital,
        strategy,
        horizon,
        confidence,
        volatility,
        drawdown
    ):

        strategy_w = self.strategy_weights.get(strategy, 1.0)

        horizon_w = self.horizon_weight(horizon)

        # risk reduction in high volatility
        vol_factor = 1 / (1 + volatility)

        # drawdown protection (reduce risk when losing)
        dd_factor = 1 if drawdown < 5 else 0.5

        # confidence boost
        conf_factor = 0.5 + confidence

        size = (
            base_capital *
            strategy_w *
            horizon_w *
            vol_factor *
            dd_factor *
            conf_factor
        )

        return round(size, 2)
