class VolatilityTarget:

    def target_position(
        self,
        balance,
        volatility,
        target_vol=0.02
    ):

        if volatility <= 0:
            return balance * 0.01

        exposure = (
            target_vol / volatility
        ) * balance

        return max(exposure, 0)
