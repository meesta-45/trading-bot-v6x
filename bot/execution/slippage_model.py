import random


class SlippageModel:

    def apply(self, price, direction):

        # simulate spread + slippage

        slippage = random.uniform(-0.2, 0.2)

        if direction == "LONG":
            return price + slippage

        return price - slippage
