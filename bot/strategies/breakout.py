class BreakoutStrategy:

    def generate(self, prices):

        if len(prices) < 30:
            return None

        resistance = max(prices[-20:])
        support = min(prices[-20:])

        last = prices[-1]

        range_size = resistance - support

        if range_size == 0:
            return None

        if last > resistance:

            strength = (last - resistance) / range_size

            return {
                "direction": "BUY",
                "score": min(1.0, strength * 2)
            }

        elif last < support:

            strength = (support - last) / range_size

            return {
                "direction": "SELL",
                "score": min(1.0, strength * 2)
            }

        return None
