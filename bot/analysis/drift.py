class DriftDetector:

    def detect(self, expected, actual):

        if expected == 0:
            return 0

        drift = abs(actual - expected) / abs(expected)

        return drift

    def is_broken(self, drift):

        return drift > 0.35
