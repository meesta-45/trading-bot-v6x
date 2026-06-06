class WalkForward:

    def split(
        self,
        prices,
        train_size=100,
        test_size=20
    ):

        datasets = []

        step = test_size

        for i in range(
            0,
            len(prices) - train_size - test_size,
            step
        ):

            train = prices[
                i:i + train_size
            ]

            test = prices[
                i + train_size:
                i + train_size + test_size
            ]

            datasets.append(
                (train, test)
            )

        return datasets
