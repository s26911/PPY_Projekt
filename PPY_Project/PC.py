import random


class PC:
    def __init__(self, board_size, fleet):
        self.board_size = board_size
        self.game_board_data_opponent = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.shots = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.fleet = fleet
        self.last_hit = None

        counter = 0
        for i in self.fleet.keys():
            for j in range(self.fleet[i]):
                counter += i
        self.ships_alive_opponent = counter
        self.ship_in_focus = False

    def select_shoot_coordinates(self):
        # if not self.ship_in_focus:
            while True:
                row, col = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if self.shots[row][col] != 1:
                    return row, col


