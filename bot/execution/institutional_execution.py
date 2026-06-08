import random


class InstitutionalExecution:

    def __init__(self):

        self.base_spread = 0.2  # synthetic spread baseline

    # =====================================
    # SPREAD MODEL
    # =====================================
    def spread(self, volatility):

        return self.base_spread + (volatility * 0.1)

    # =====================================
    # SLIPPAGE MODEL
    # =====================================
    def slippage(self, volatility, order_size):

        base = volatility * 0.05

        impact = order_size * 0.001

        noise = random.uniform(-0.1, 0.1)

        return base + impact + noise

    # =====================================
    # EXECUTION QUALITY
    # =====================================
    def execution_quality(self, volatility):

        if volatility < 0.5:
            return "EXCELLENT"

        if volatility < 1.5:
            return "GOOD"

        if volatility < 3:
            return "POOR"

        return "VERY_POOR"

    # =====================================
    # PARTIAL FILL SIMULATION
    # =====================================
    def fill_ratio(self, volatility, order_size):

        if volatility < 1:
            return 1.0

        if volatility < 2:

            return random.uniform(0.7, 1.0)

        if volatility < 3:

            return random.uniform(0.4, 0.8)

        return random.uniform(0.2, 0.6)

    # =====================================
    # LATENCY SIMULATION
    # =====================================
    def latency_penalty(self, volatility):

        return random.uniform(0, volatility * 0.02)
