class WalkForward:

    def split(self, prices, window=100):

        sets = []

        for i in range(0, len(prices) - window, 20):

            train = prices[i:i + window]
            test = prices[i + window:i + window + 20]

            if len(test) == 20:

                sets.append((train, test))

        return sets
