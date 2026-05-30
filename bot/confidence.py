class ConfidenceEngine:

    def calculate(
        self,
        trend,
        macd,
        adx,
        momentum
    ):

        score = 0

        if trend:
            score += 25

        if macd:
            score += 25

        if adx:
            score += 25

        if momentum:
            score += 25

        return score
