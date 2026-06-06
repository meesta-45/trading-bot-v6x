import statistics


class CorrelationEngine:

    def correlation(self, x, y):

        if len(x) != len(y):
            return 0

        if len(x) < 2:
            return 0

        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        numerator = sum(
            (a - mean_x) * (b - mean_y)
            for a, b in zip(x, y)
        )

        std_x = statistics.pstdev(x)
        std_y = statistics.pstdev(y)

        denominator = std_x * std_y

        if denominator == 0:
            return 0

        return numerator / (
            len(x) * denominator
        )
