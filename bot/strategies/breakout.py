class BreakoutStrategy:

    def generate(self, prices):

        if len(prices) < 20:
            return None

        resistance = max(prices[-15:])
        support = min(prices[-15:])

        last = prices[-1]

        range_size = resistance - support

        if range_size == 0:
            return None

        if last > resistance:

            return {
                "direction": "BUY",
                "score": min(1.0, (last - resistance) / range_size * 2)
            }

        if last < support:

            return {
                "direction": "SELL",
                "score": min(1.0, (support - last) / range_size * 2)
            }

        return None
