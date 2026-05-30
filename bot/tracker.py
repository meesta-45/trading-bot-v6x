class TradeTracker:

    def __init__(self):

        self.balance = 1000

        self.wins = 0
        self.losses = 0

        self.total_trades = 0

    def record_win(self, amount):

        self.balance += amount

        self.wins += 1

        self.total_trades += 1

    def record_loss(self, amount):

        self.balance -= amount

        self.losses += 1

        self.total_trades += 1

    def stats(self):

        if self.total_trades == 0:

            winrate = 0

        else:

            winrate = (
                self.wins /
                self.total_trades
            ) * 100

        return {
            "balance": self.balance,
            "wins": self.wins,
            "losses": self.losses,
            "winrate": round(winrate, 2)
        }
