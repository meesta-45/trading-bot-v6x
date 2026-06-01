class DrawdownGuard:

    def __init__(self):

        self.peak = 10000

    def update_peak(self, balance):

        if balance > self.peak:
            self.peak = balance

    def drawdown(self, balance):

        if self.peak == 0:
            return 0

        return (self.peak - balance) / self.peak * 100

    def kill_switch(self, balance):

        dd = self.drawdown(balance)

        return dd > 12  # hard institutional cutoff
