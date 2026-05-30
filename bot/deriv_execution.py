import random


class DerivExecution:

    def __init__(self):

        self.stake = 1

    def buy(self, contract, amount):

        print(
            "EXECUTING:",
            contract,
            amount
        )

        result = random.choice([
            "WIN",
            "LOSS"
        ])

        print("RESULT:", result)

        return result
