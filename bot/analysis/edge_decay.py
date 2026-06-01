class EdgeDecay:

    def __init__(self):

        self.history = {}

    def update(self, strategy, performance):

        if strategy not in self.history:
            self.history[strategy] = []

        self.history[strategy].append(performance)

    def is_decaying(self, strategy):

        data = self.history.get(strategy, [])

        if len(data) < 5:
            return False

        return data[-1] < data[-3]
