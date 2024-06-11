class Config:
    def __init__(self):
        self.board_size = 10
        self.pvp = False

    def set_board_size(self, board_size):
        self.board_size = board_size

    def set_pvp(self, pvp):
        self.pvp = pvp
