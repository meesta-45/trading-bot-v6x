import statistics

class Strategy:

    def signal(self, prices):

        if len(prices) < 20:
            return "NO_TRADE"

        short = statistics.mean(prices[-5:])
        long = statistics.mean(prices[-20:])
        current = prices[-1]

        if current > short and short > long:
            return "BUY"

        if current < short and short < long:
            return "SELL"

        return "NO_TRADE"
