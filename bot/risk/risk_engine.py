class RiskEngine:

    def position_size(self, balance, kelly, volatility):

        base = balance * kelly

        adjusted = base / (1 + volatility)

        max_risk = balance * 0.02

        return min(adjusted, max_risk)
