class ModeController:

    def __init__(self):

        self.modes = ["FOREX", "CRYPTO", "SYNTHETIC"]

        self.active_mode = None

    def set_mode(self, mode):

        if mode not in self.modes:
            raise ValueError("Invalid mode selected")

        self.active_mode = mode

        print("\n🚀 ACTIVE MARKET MODE:", mode)

    def get_mode(self):

        return self.active_mode
