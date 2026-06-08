import statistics


class MarketRegimeAI:

    def detect(self, prices):

        if len(prices) < 50:
            return "UNKNOWN"

        recent = prices[-30:]

        # =====================================
        # VOLATILITY
        # =====================================
        returns = [
            abs(recent[i] - recent[i - 1])
            for i in range(1, len(recent))
        ]

        volatility = sum(returns) / len(returns)

        # =====================================
        # TREND STRENGTH
        # =====================================
        short = sum(recent[-5:]) / 5
        long = sum(recent) / len(recent)

        trend_strength = abs(short - long)

        # =====================================
        # RANGE DETECTION
        # =====================================
        price_std = statistics.stdev(recent)

        # =====================================
        # REGIME LOGIC
        # =====================================
        if volatility > price_std * 1.5:

            return "VOLATILE"

        if trend_strength > price_std * 0.8:

            return "TRENDING"

        if price_std < volatility * 1.2:

            return "RANGING"

        return "QUIET"

    # =====================================
    # STRATEGY FILTER
    # =====================================
    def allowed_strategies(self, regime):

        mapping = {

            "TRENDING": [
                "trend",
                "breakout"
            ],

            "RANGING": [
                "mean_reversion"
            ],

            "VOLATILE": [
                "breakout",
                "trend"
            ],

            "QUIET": [
                "mean_reversion"
            ]
        }

        return mapping.get(
            regime,
            ["trend"]
        )
