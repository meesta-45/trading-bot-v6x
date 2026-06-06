class PositionManager:

    def __init__(self):

        self.positions = []

    def open_position(self, position):

        self.positions.append(position)

    def active_positions(self):

        return [
            p for p in self.positions
            if p.active
        ]

    def close_position(self, position):

        position.active = False
