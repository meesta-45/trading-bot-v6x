import random


class InstitutionalExecution:

    def __init__(self):

        self.base_spread = 0.0002

    # =====================================
    # SPREAD MODEL
    # =====================================
    def spread(self, volatility):

        return self.base_spread + (volatility * 0.1)

    # =====================================
    # SLIPPAGE MODEL
    # =====================================
    def slippage(self, volatility, size):

        impact = size * 0.00001

        noise = random.uniform(
            0,
            volatility * 0.05
        )

        return impact + noise

    # =====================================
    # EXECUTION DELAY
    # =====================================
    def execution_delay(self, volatility):

        if volatility < 0.5:
            return 0
        elif volatility < 1.5:
            return 1
        else:
            return 2

    # =====================================
    # FILL QUALITY
    # =====================================
    def fill_quality(self, volatility, size):

        base = 1 - (volatility * 0.1)

        penalty = size * 0.00001

        quality = base - penalty

        return max(0.2, min(1.0, quality))

    # =====================================
    # CORE EXECUTION METHOD (FIXED)
    # =====================================
    def execute(self, price, direction, volatility, size):

        spread = self.spread(volatility)
        slip = self.slippage(volatility, size)
        delay = self.execution_delay(volatility)
        fill_quality = self.fill_quality(volatility, size)

        if direction == "LONG":
            fill_price = price + spread + slip
        else:
            fill_price = price - spread - slip

        return {
            "fill_price": round(fill_price, 4),
            "spread": round(spread, 6),
            "slippage": round(slip, 6),
            "delay": delay,
            "fill_quality": round(fill_quality, 3)
        }
