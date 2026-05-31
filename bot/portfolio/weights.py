class StrategyWeights:

    def __init__(self):

        self.weights = {
            "trend": 0.4,
            "mean_reversion": 0.35,
            "breakout": 0.25
        }

    def update(self, performance):

        total = sum(performance.values()) + 1e-9

        for k in self.weights:

            if k in performance:

                self.weights[k] = performance[k] / total

        return self.weights
