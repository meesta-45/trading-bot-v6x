import statistics


class MeanReversionStrategy:

    def generate(self, prices):

        if len(prices) < 20:
            return None

        avg = sum(prices[-20:]) / 20
        price = prices[-1]

        deviation = (price - avg) / avg

        if deviation > 0.01:
            return {
                "direction": "FALL",
                "confidence": 0.65,
                "expected_value": 1.1
            }

        if deviation < -0.01:
            return {
                "direction": "RISE",
                "confidence": 0.65,
                "expected_value": 1.1
            }

        return None
