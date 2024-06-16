from tkinter import messagebox


class BattleshipsGame:
    def __init__(self):
        self.pvp = True
        self.board_size = 10
        self.fleet = {5: 1, 4: 1, 3: 2, 2: 1}
        self.game_board_data_p1 = [[]]  # 2-dimensional int array, 0:empty, 1:ship
        self.game_board_data_p2 = [[]]
        self.shots_p1 = [[]]
        self.shots_p2 = [[]]
        self.ships_alive_p1 = None
        self.ships_alive_p2 = None
        self.leaderboard = {}
        self.read_leaderboard_from_file("leaderboard.txt")

    def update_board_size(self, size):
        self.board_size = int(size)

    def update_pvp(self, value):
        self.pvp = True if value == "Player vs Player" else False

    def update_fleet(self, mode, size, quantity):
        try:
            size = int(size)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Please provide integer values.")
            return

        if size < 1 or size > self.board_size:
            messagebox.showerror("Error", "Size must be between 1 and {}.".format(self.board_size))

        if mode:
            if size not in self.fleet.keys():
                self.fleet[size] = quantity
            else:
                self.fleet[size] += quantity
        else:
            if size not in self.fleet.keys():
                messagebox.showerror("Error", "Cannot remove ship not present in fleet.")
            elif self.fleet[size] - quantity < 0:
                messagebox.showerror("Error", "Cannot remove more ships than are absent in fleet.")
            elif len(self.fleet) == 1 and self.fleet[size] - quantity <= 0:
                messagebox.showerror("Error", "Fleet cannot be empty.")
            else:
                self.fleet[size] -= quantity
                if self.fleet[size] == 0:
                    self.fleet.pop(size)

    def get_fleet_info(self, fleet=None):
        if fleet is None:
            fleet = self.fleet
        string = ""
        for ship_size in sorted(fleet.keys(), reverse=True):
            string += "Size: {}, quantity: {}\n".format(ship_size, fleet[ship_size])
        return string

    def add_ship_to_board(self, row, column, ship_size, orientation, player_number):
        game_board = self.game_board_data_p1 if player_number == 1 else self.game_board_data_p2
        if orientation == "horizontal":
            for i in range(ship_size):
                game_board[row][column + i] = 1
        else:
            for i in range(ship_size):
                game_board[row + i][column] = 1

    def shoot(self, row, col, player_number):
        if self.ships_alive_p1 is None:
            counter = 0
            for i in self.fleet.keys():
                for j in range(self.fleet[i]):
                    counter += i
            print(counter)
            self.ships_alive_p1 = counter
            self.ships_alive_p2 = counter

        shots = self.shots_p1 if player_number == 2 else self.shots_p2
        board_data = self.game_board_data_p1 if player_number == 1 else self.game_board_data_p2
        shots[row][col] = 1

        if board_data[row][col] == 1:
            if player_number == 1:
                self.ships_alive_p1 = self.ships_alive_p1 - 1
            else:
                self.ships_alive_p2 = self.ships_alive_p2 - 1

            if (self.ships_alive_p1 if player_number == 1 else self.ships_alive_p2) == 0:
                return True
        return False

    def if_already_shot(self, row, col, player_number):
        shots = self.shots_p1 if player_number == 2 else self.shots_p2
        return shots[row][col] == 1

    def read_leaderboard_from_file(self, file_name):
        try:
            with open(file_name, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    s = line.split(' ')
                    self.leaderboard[s[0]] = int(s[1])
        except FileNotFoundError:
            with open(file_name, 'w') as f:
                return

    def add_to_leaderboard(self, player_name):
        if player_name not in self.leaderboard.keys():
            self.leaderboard[player_name] = 1
        else:
            self.leaderboard[player_name] += 1
