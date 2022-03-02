class Player:
    LOCAL = 0
    LAN = 1

    def __init__(self, mode=LOCAL) -> None:
        self.symbol = None
        self.mode = mode

    def set_as_x(self) -> None:
        self.symbol = 'X'

    def set_as_o(self) -> None:
        self.symbol = 'O'