class VotingEngine:

    def combine(self, signals):

        if not signals:
            return None

        buy_score = 0
        sell_score = 0

        best_strategy = None
        best_score = 0

        for signal in signals:

            direction = signal["direction"]

            score = signal.get("score", 0.5)

            if score > best_score:
                best_score = score
                best_strategy = signal.get(
                    "strategy",
                    "trend"
                )

            if direction == "BUY":
                buy_score += score

            elif direction == "SELL":
                sell_score += score

        if buy_score == 0 and sell_score == 0:
            return None

        if buy_score > sell_score:

            return {
                "direction": "BUY",
                "score": buy_score,
                "strategy": best_strategy
            }

        elif sell_score > buy_score:

            return {
                "direction": "SELL",
                "score": sell_score,
                "strategy": best_strategy
            }

        return None
