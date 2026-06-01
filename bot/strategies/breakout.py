class BreakoutStrategy:

    def generate(self, prices):

        if len(prices) < 30:
            return None

        high = max(prices[-30:])
        low = min(prices[-30:])
        last = prices[-1]

        if last >= high:

            return {
                "direction": "LONG",
                "confidence": 0.8,
                "expected_value": 1.3
            }

        if last <= low:

            return {
                "direction": "SHORT",
                "confidence": 0.8,
                "expected_value": 1.3
            }

        return None
