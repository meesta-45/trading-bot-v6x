class RiskPolicy:

    def __init__(self):

        self.min_ev = 0
        self.min_pf = 1.2
        self.max_drawdown = 10
        self.min_sharpe = 0.8

    # =====================================
    # TRADE APPROVAL FILTER
    # =====================================

    def allow_trade(
        self,
        ev,
        profit_factor,
        sharpe,
        drawdown
    ):

        if ev <= self.min_ev:
            return False

        if profit_factor < self.min_pf:
            return False

        if sharpe < self.min_sharpe:
            return False

        if drawdown > self.max_drawdown:
            return False

        return True

    # =====================================
    # POSITION SIZING (KELLY CONTROLLED)
    # =====================================

    def position_size(
        self,
        balance,
        kelly,
        confidence
    ):

        # hedge fund rule: NEVER full Kelly
        safe_kelly = kelly * 0.25

        size = balance * safe_kelly * (confidence / 100)

        # hard risk cap (important)
        max_risk = balance * 0.02

        return min(size, max_risk)
