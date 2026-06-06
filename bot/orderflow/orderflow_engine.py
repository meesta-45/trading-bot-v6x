class OrderFlowEngine:

    def liquidity_zones(self, prices):

        highs = sorted(prices[-20:])[-5:]
        lows = sorted(prices[-20:])[:5]

        return {
            "resistance": sum(highs) / len(highs),
            "support": sum(lows) / len(lows)
        }

    # =====================================
    # FAKE BREAKOUT DETECTION
    # =====================================
    def fake_breakout(
        self,
        current_price,
        resistance,
        support,
        momentum
    ):

        # fake bullish breakout
        if current_price > resistance and momentum < 0.5:
            return True

        # fake bearish breakout
        if current_price < support and momentum < 0.5:
            return True

        return False

    # =====================================
    # VOLATILITY COMPRESSION
    # =====================================
    def compression(self, prices):

        recent = prices[-10:]

        ranges = [
            abs(recent[i] - recent[i - 1])
            for i in range(1, len(recent))
        ]

        avg_range = sum(ranges) / len(ranges)

        return avg_range < 0.3

    # =====================================
    # SLIPPAGE SIMULATION
    # =====================================
    def slippage(self, volatility):

        if volatility > 3:
            return 0.5

        if volatility > 1.5:
            return 0.2

        return 0.05

    # =====================================
    # TRADE QUALITY SCORE
    # =====================================
    def quality_score(
        self,
        confidence,
        volatility,
        compression
    ):

        score = confidence

        if volatility > 3:
            score -= 0.15

        if compression:
            score += 0.1

        return round(max(0, min(score, 1)), 2)
