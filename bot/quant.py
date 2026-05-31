import math
import random


class QuantEngine:

    # =====================================
    # EXPECTED VALUE (EV)
    # =====================================

    def expected_value(
        self,
        winrate,
        avg_win,
        avg_loss
    ):

        ev = (
            (winrate * avg_win)
            -
            ((1 - winrate) * avg_loss)
        )

        return round(ev, 4)

    # =====================================
    # SHARPE RATIO
    # =====================================

    def sharpe_ratio(
        self,
        returns,
        risk_free_rate=0
    ):

        if len(returns) < 2:
            return 0

        avg_return = (
            sum(returns) / len(returns)
        )

        variance = sum(
            (
                r - avg_return
            ) ** 2 for r in returns
        ) / len(returns)

        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return 0

        sharpe = (
            avg_return - risk_free_rate
        ) / std_dev

        return round(sharpe, 4)

    # =====================================
    # KELLY CRITERION
    # =====================================

    def kelly_criterion(
        self,
        win_probability,
        reward_risk_ratio
    ):

        kelly = (
            (
                reward_risk_ratio
                * win_probability
            )
            -
            (1 - win_probability)
        ) / reward_risk_ratio

        return round(
            max(kelly, 0),
            4
        )

    # =====================================
    # PROFIT FACTOR
    # =====================================

    def profit_factor(
        self,
        gross_profit,
        gross_loss
    ):

        if gross_loss == 0:
            return 0

        pf = (
            gross_profit /
            abs(gross_loss)
        )

        return round(pf, 4)

    # =====================================
    # DRAWDOWN %
    # =====================================

    def drawdown_percent(
        self,
        peak_balance,
        current_balance
    ):

        if peak_balance == 0:
            return 0

        dd = (
            (
                peak_balance
                -
                current_balance
            )
            /
            peak_balance
        ) * 100

        return round(dd, 2)

    # =====================================
    # CAGR
    # =====================================

    def cagr(
        self,
        start_balance,
        end_balance,
        years
    ):

        if (
            start_balance <= 0 or
            years <= 0
        ):
            return 0

        cagr = (
            (
                end_balance /
                start_balance
            ) ** (
                1 / years
            )
            - 1
        ) * 100

        return round(cagr, 2)

    # =====================================
    # MONTE CARLO
    # =====================================

    def monte_carlo(
        self,
        trades=100,
        simulations=1000,
        winrate=0.55,
        reward=10,
        risk=10
    ):

        final_balances = []

        for _ in range(simulations):

            balance = 1000

            for _ in range(trades):

                outcome = random.random()

                if outcome < winrate:

                    balance += reward

                else:

                    balance -= risk

            final_balances.append(balance)

        avg_balance = (
            sum(final_balances)
            / len(final_balances)
        )

        max_balance = max(final_balances)

        min_balance = min(final_balances)

        return {
            "average_balance": round(
                avg_balance,
                2
            ),
            "best_case": round(
                max_balance,
                2
            ),
            "worst_case": round(
                min_balance,
                2
            )
        }
