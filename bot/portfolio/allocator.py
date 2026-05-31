class CapitalAllocator:

    def allocate(self, balance, kelly, confidence, regime):

        base = balance * kelly

        # regime adjustments
        if regime == "VOLATILE":
            base *= 0.5

        if regime == "TRENDING":
            base *= 1.2

        size = base * (confidence / 100)

        return max(1, size)
