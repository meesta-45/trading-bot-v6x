from collections import defaultdict


class VotingEngine:

    def combine(self, signals):

        votes = defaultdict(float)

        for s in signals:

            if not s:
                continue

            direction = s["direction"]

            votes[direction] += (
                s["confidence"] *
                s["expected_value"]
            )

        if not votes:
            return None

        best = max(votes.items(), key=lambda x: x[1])

        return {
            "direction": best[0],
            "score": best[1]
        }
