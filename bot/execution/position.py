from datetime import datetime, timedelta


class Position:

    def __init__(
        self,
        direction,
        entry_price,
        size,
        stop_loss,
        take_profit,
        hold_minutes
    ):

        self.direction = direction

        self.entry_price = entry_price

        self.size = size

        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.open_time = datetime.utcnow()

        self.expiry_time = (
            self.open_time +
            timedelta(minutes=hold_minutes)
        )

        self.active = True

    def expired(self):

        return (
            datetime.utcnow() >=
            self.expiry_time
        )
