from bot.indicators.ema import calculate_ema


class TrendStrategy:

    def generate(self, prices):

        if len(prices) < 50:
            return None

        ema10 = calculate_ema(prices, 10)
        ema30 = calculate_ema(prices, 30)

        if ema10 is None or ema30 is None:
            return None

        if ema10 > ema30:

            return {
                "direction": "LONG",
                "confidence": 0.7,
                "expected_value": 1.2
            }

        if ema10 < ema30:

            return {
                "direction": "SHORT",
                "confidence": 0.7,
                "expected_value": 1.2
            }

        return None
