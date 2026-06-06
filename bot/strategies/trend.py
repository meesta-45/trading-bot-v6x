class TrendStrategy:

    def generate(self, prices):

        if len(prices) < 30:
            return None

        short = sum(prices[-5:]) / 5
        mid = sum(prices[-15:]) / 15
        long = sum(prices[-30:]) / 30

        trend_strength = abs(short - long) / long

        strength = min(1.0, trend_strength * 50)  # 🔥 BOOSTED

        if short > mid > long:

            return {
                "direction": "BUY",
                "score": strength
            }

        if short < mid < long:

            return {
                "direction": "SELL",
                "score": strength
            }

        return None
