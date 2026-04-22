import statistics

class Strategy:

    def signal(self, prices):

        if len(prices) < 30:
            return "NO_TRADE"

        short = statistics.mean(prices[-5:])
        mid = statistics.mean(prices[-15:])
        long = statistics.mean(prices[-30:])
        current = prices[-1]

        if short > mid > long and current > short:
            return "BUY"

        if short < mid < long and current < short:
            return "SELL"

        return "NO_TRADE"
