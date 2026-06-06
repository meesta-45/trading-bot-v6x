class ReversalDetector:

    def detect(
        self,
        prices
    ):

        if len(prices) < 5:
            return False

        latest = prices[-1]
        avg = sum(prices[-5:]) / 5

        deviation = abs(
            latest - avg
        )

        return deviation > 2
