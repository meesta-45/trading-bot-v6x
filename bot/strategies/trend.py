class TrendStrategy:

    def generate(self, prices):

        if len(prices) < 30:
            return None

        recent = prices[-20:]

        ema_fast = sum(recent[-5:]) / 5
        ema_slow = sum(recent[-20:]) / 20

        if ema_fast > ema_slow:

            return {
                "direction": "BUY",
                "score": min(1.0, (ema_fast - ema_slow) / ema_slow * 10)
            }

        elif ema_fast < ema_slow:

            return {
                "direction": "SELL",
                "score": min(1.0, (ema_slow - ema_fast) / ema_slow * 10)
            }

        return None
