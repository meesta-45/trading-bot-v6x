class TrendStrategy:

    def generate(self, prices):

        if len(prices) < 30:
            return None

        short = sum(prices[-5:]) / 5
        mid = sum(prices[-15:]) / 15
        long = sum(prices[-30:]) / 30

        bullish = short > mid > long
        bearish = short < mid < long

        diff = abs(short - long)

        strength = min(1.0, diff / long * 10)

        if bullish:

            return {
                "direction": "BUY",
                "score": strength
            }

        if bearish:

            return {
                "direction": "SELL",
                "score": strength
            }

        return None
