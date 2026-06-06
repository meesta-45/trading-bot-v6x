class HoldEngine:

    def calculate(self, volatility):

        # high volatility = shorter hold
        if volatility > 3:
            return 15

        if volatility > 1.5:
            return 30

        return 60
