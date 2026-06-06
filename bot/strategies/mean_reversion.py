import statistics


class MeanReversionStrategy:

    def generate(self, prices):

        if len(prices) < 20:
            return None

        recent = prices[-20:]

        mean = sum(recent) / len(recent)
        std = statistics.stdev(recent)

        if std == 0:
            return None

        last = prices[-1]

        z = (last - mean) / std

        strength = min(1.0, abs(z) / 2.5)

        if z > 0.7:

            return {
                "direction": "SELL",
                "score": strength
            }

        if z < -0.7:

            return {
                "direction": "BUY",
                "score": strength
            }

        return None
