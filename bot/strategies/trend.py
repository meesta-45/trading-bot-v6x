from bot.indicators.ema import calculate_ema
from bot.indicators.macd import calculate_macd


class TrendStrategy:

    def generate(self, prices):

        if len(prices) < 30:
            return None

        ema10 = calculate_ema(prices, 10)
        ema20 = calculate_ema(prices, 20)

        macd = calculate_macd(prices)

        if ema10 is None or ema20 is None:
            return None

        if ema10 > ema20 and macd > 0:
            return {
                "direction": "RISE",
                "confidence": 0.7,
                "expected_value": 1.2
            }

        if ema10 < ema20 and macd < 0:
            return {
                "direction": "FALL",
                "confidence": 0.7,
                "expected_value": 1.2
            }

        return None
