import statistics


class BreakoutStrategy:

    def generate(self, prices):

        if len(prices) < 20:
            return None

        high = max(prices[-20:])
        low = min(prices[-20:])
        last = prices[-1]

        if last > high * 0.999:
            return {
                "direction": "RISE",
                "confidence": 0.75,
                "expected_value": 1.3
            }

        if last < low * 1.001:
            return {
                "direction": "FALL",
                "confidence": 0.75,
                "expected_value": 1.3
            }

        return None
