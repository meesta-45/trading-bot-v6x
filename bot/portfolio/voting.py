from collections import defaultdict


class VotingEngine:

    def combine(self, signals):

        votes = defaultdict(float)

        for s in signals:

            if s is None:
                continue

            direction = s["direction"]

            votes[direction] += (
                s["confidence"] *
                s["expected_value"]
            )

        if not votes:
            return None

        best = max(votes.items(), key=lambda x: x[1])

        direction, score = best

        return {
            "contract": direction,
            "score": score
        }
