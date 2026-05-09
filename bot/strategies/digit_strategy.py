from collections import Counter

class DigitStrategy:

    def analyze(self, prices):

        digits = [int(str(p)[-1]) for p in prices[-50:]]

        freq = Counter(digits)

        least_common = min(freq, key=freq.get)

        if least_common <= 4:
            return ("OVER", 70)

        return ("UNDER", 65)
