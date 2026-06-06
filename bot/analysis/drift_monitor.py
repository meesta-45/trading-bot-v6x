class DriftMonitor:

    def deviation(
        self,
        expected,
        actual
    ):

        if expected == 0:
            return 0

        return abs(
            actual - expected
        ) / abs(expected)

    def unstable(self, drift):

        return drift > 0.4
