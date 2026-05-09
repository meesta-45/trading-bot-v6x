class TrendStrategy:

    def analyze(self, prices):

        if len(prices) < 30:
            return ("NO_TRADE", 0)

        short = sum(prices[-5:]) / 5
        mid = sum(prices[-15:]) / 15
        long = sum(prices[-30:]) / 30

        if short > mid > long:
            return ("RISE", 80)

        if short < mid < long:
            return ("FALL", 80)

        return ("NO_TRADE", 0)
