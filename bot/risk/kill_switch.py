class KillSwitch:

    def __init__(self):

        self.disabled_strategies = set()

    def evaluate(self, strategy, ev, drawdown, sharpe):

        if ev < 0 or drawdown > 15 or sharpe < 0.5:

            self.disabled_strategies.add(strategy)

        if strategy in self.disabled_strategies:

            return False

        return True
