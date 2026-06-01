import statistics


class VolatilityEngine:

    def compute(self, returns):

        if len(returns) < 2:
            return 1.0

        return statistics.pstdev(returns)
