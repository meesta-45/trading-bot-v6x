import statistics


class MarketRegime:

    def detect(self, prices):

        if len(prices) < 30:
            return "UNKNOWN"

        recent = prices[-30:]

        volatility = statistics.pstdev(recent)

        trend_strength = abs(recent[-1] - recent[0])

        # simple classification logic

        if volatility < 0.5:
            return "CHOPPY"

        if trend_strength > volatility * 2:
            return "TRENDING"

        if volatility > 2:
            return "VOLATILE"

        return "MIXED"
