from bot.indicators.ema import calculate_ema
from bot.indicators.macd import calculate_macd


class TrendStrategy:

    def generate(self, prices):

        if len(prices) < 50:
            return None

        ema10 = calculate_ema(prices, 10)
        ema30 = calculate_ema(prices, 30)

        macd = calculate_macd(prices)

        if ema10 is None or ema30 is None:
            return None

        if ema10 > ema30 and macd > 0:
            return {
                "direction": "LONG",
                "confidence": 0.75,
                "expected_value": 1.3
            }

        if ema10 < ema30 and macd < 0:
            return {
                "direction": "SHORT",
                "confidence": 0.75,
                "expected_value": 1.3
            }

        return None
