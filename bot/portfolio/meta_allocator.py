class MetaAllocator:

    def adjust(self, weights, performance):

        new_weights = {}

        total = sum(performance.values()) + 1e-9

        for k in weights:

            score = performance.get(k, 0)

            new_weights[k] = score / total

        return new_weights
