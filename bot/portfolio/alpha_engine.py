class AlphaEngine:

    def score(
        self,
        avg_pnl,
        winrate,
        drawdown
    ):

        alpha = (
            (avg_pnl * 0.5)
            +
            (winrate * 100 * 0.4)
            -
            (drawdown * 0.3)
        )

        return round(alpha, 4)
