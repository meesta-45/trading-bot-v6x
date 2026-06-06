import statistics


class MeanReversionStrategy:

    def generate(self, prices):

        if len(prices) < 30:
            return None

        recent = prices[-20:]

        mean = sum(recent) / len(recent)
        std = statistics.stdev(recent)

        if std == 0:
            return None

        last_price = prices[-1]

        z_score = (last_price - mean) / std

        if z_score > 1:

            return {
                "direction": "SELL",
                "score": min(1.0, abs(z_score) / 3)
            }

        elif z_score < -1:

            return {
                "direction": "BUY",
                "score": min(1.0, abs(z_score) / 3)
            }

        return None
