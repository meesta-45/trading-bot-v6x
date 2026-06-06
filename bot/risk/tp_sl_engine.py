class TPSLEngine:

    def generate(
        self,
        direction,
        entry,
        volatility
    ):

        distance = volatility * 2

        if direction == "LONG":

            tp = entry + distance
            sl = entry - distance

        else:

            tp = entry - distance
            sl = entry + distance

        return tp, sl
