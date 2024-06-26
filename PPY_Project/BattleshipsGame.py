import json
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
        self.ships_alive = None
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
                messagebox.showerror("Error", "Cannot remove more ships than are present in fleet.")
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
        if self.ships_alive is None:
            self.ships_alive = {}
            counter = 0
            for i in self.fleet.keys():
                for j in range(self.fleet[i]):
                    counter += i
            self.ships_alive[1] = counter
            self.ships_alive[2] = counter

        shots = self.shots_p1 if player_number == 2 else self.shots_p2
        board_data = self.game_board_data_p1 if player_number == 1 else self.game_board_data_p2
        shots[row][col] = 1

        if board_data[row][col] == 1:
            self.ships_alive[player_number] -= 1
            if self.ships_alive[player_number] == 0:
                return True

        return False

    def if_hit(self, row, col, player_number):
        data = self.game_board_data_p1 if player_number == 1 else self.game_board_data_p2
        return data[row][col] == 1

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

    def save_leaderboard(self, file_name):
        with open(file_name, 'w') as f:
            for player in self.leaderboard.keys():
                f.write(player + " " + str(self.leaderboard[player]) + "\n")

    def save_game(self, player_number, save_name):
        with open("saves.txt", 'a') as f:
            f.write(save_name + "\n")
            f.write(str(player_number) + "\n")
            f.write("1\n" if self.pvp == True else "0\n")
            f.write(str(self.board_size) + "\n")
            f.write(str(self.dict_to_save_form(self.fleet)) + "\n")
            f.write(self.two_dim_arr_to_save_form(self.game_board_data_p1) + "\n")
            f.write(self.two_dim_arr_to_save_form(self.game_board_data_p2) + "\n")
            f.write(self.two_dim_arr_to_save_form(self.shots_p1) + "\n")
            f.write(self.two_dim_arr_to_save_form(self.shots_p2) + "\n")
            f.write(str(self.ships_alive_p1) + "\n")
            f.write(str(self.ships_alive_p2) + "\n")

    def dict_to_save_form(self, dict):
        out = ""
        for key, value in dict.items():
            out += str(key) + " " + str(value) + "\t"
        return out

    def two_dim_arr_to_save_form(self, arr):
        out = ""
        for row in range(len(arr)):
            for col in range(len(arr[row])):
                out += str(arr[row][col]) + " "
            out += "\t"
        return out

    def list_game_saves(self):
        out = []
        with open("saves.txt", 'r') as f:
            lines = f.readlines()
            i = 0
            try:
                while True:
                    out.append(lines[i].strip())
                    i += 11
            except IndexError:
                None
        return out

    def game_from_save(self, save_name):
        game = BattleshipsGame()
        data = []
        with open("saves.txt", 'r') as f:
            lines = f.readlines()
            i = 0
            try:
                while True:
                    if lines[i].strip() == save_name:
                        for j in range(i, i + 11):
                            data.append(lines[j].strip())
                        break
                    i = i + 11
            except IndexError:
                print("Corrupted save file!")
                return

        player_number = int(data[1])
        game.pvp = (data[2] == "1")
        game.board_size = int(data[3])
        game.fleet = self.dict_from_save_form(data[4])
        game.game_board_data_p1 = self.two_dim_arr_from_save_form(data[5])
        game.game_board_data_p2 = self.two_dim_arr_from_save_form(data[6])
        game.shots_p1 = self.two_dim_arr_from_save_form(data[7])
        game.shots_p2 = self.two_dim_arr_from_save_form(data[8])
        game.ships_alive_p1 = (None if data[9] == "None" else int(data[9]))
        game.ships_alive_p2 = (None if data[10] == "None" else int(data[10]))

        return game, player_number

    def dict_from_save_form(self, text):
        out = {}
        for i in text.split("\t"):
            items = i.split(" ")
            out[items[0]] = int(items[1])
        return out

    def two_dim_arr_from_save_form(self, text):
        out = []
        for i in text.split("\t"):
            row = []
            for j in i.strip().split(" "):
                row.append(int(j))
            out.append(row)
        return out
