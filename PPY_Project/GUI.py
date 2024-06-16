import random
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox, Treeview
import copy
from BattleshipsGame import BattleshipsGame


class GUI(Tk):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.ship_size = IntVar()
        self.orientation = "horizontal"
        self.available_fleet = {}
        self.title("Battleships")
        self.start_menu_ui()
        self.last_hovered = (0, 0)
        self.force_paint = False
        self.player_can_shoot = True

    def start_menu_ui(self):
        self.clear_frame()
        self.geometry("300x200")
        Button(self, text="Start new game", command=lambda: self.configure_game_ui()).pack(pady=5)
        Button(self, text="Load game", command=self.load_save_ui).pack(pady=5)
        Button(self, text="Show leaderboard", command=self.show_leaderboard_ui).pack(pady=5)
        Button(self, text="Quit", command=self.quit_game).pack(pady=5)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def configure_game_ui(self):
        self.clear_frame()
        self.geometry("")

        main_label = Label(self, text="Select options for your game")
        main_label.pack()

        # mode selection container(Frame)
        mode_selection_cont = Frame(self)
        Label(mode_selection_cont, text="Select mode:").grid(row=0, column=0, sticky=E)
        mode = Combobox(mode_selection_cont, values=["Player vs Player", "Player vs Computer"])
        mode.set("Player vs Player" if self.game.pvp else "Player vs Computer")
        mode.bind("<<ComboboxSelected>>", lambda event: self.game.update_pvp(event.widget.get()))
        mode.grid(row=0, column=1, sticky=W)
        mode_selection_cont.pack()

        # board size selection container
        board_size_cont = Frame(self)
        Label(board_size_cont, text="Select board size:").grid(row=2, column=1, sticky=E)
        board_size_selector = Scale(board_size_cont, from_=1, to=100, orient=HORIZONTAL,
                                    command=self.game.update_board_size)
        board_size_selector.set(self.game.board_size)
        board_size_selector.grid(row=2, column=2, sticky=W)
        board_size_cont.pack()

        # label that show your fleet
        ships_string = "Your fleet consists of following ships:\n" + self.game.get_fleet_info()
        ships_label = Label(self, text=ships_string)
        ships_label.pack()

        # ships managing container
        ships_cont = Frame(self)
        Label(ships_cont, text="Add or remove a ship:").grid(row=0, column=0, columnspan=6)
        Label(ships_cont, text="Size:").grid(row=1, column=0)
        size_field = Entry(ships_cont)
        size_field.grid(row=1, column=1)
        Label(ships_cont, text="Quantity:").grid(row=1, column=2)
        quantity_field = Entry(ships_cont)
        quantity_field.grid(row=1, column=3)
        (Button(ships_cont, text="Add",
                command=lambda: self.fleet_change(ships_label, True, size_field.get(), quantity_field.get()))
         .grid(row=1, column=4))
        (Button(ships_cont, text="Remove",
                command=lambda: self.fleet_change(ships_label, False, size_field.get(), quantity_field.get()))
         .grid(row=1, column=5))
        ships_cont.pack()

        # buttons to proceed
        proceed_buttons_cont = Frame(self)
        next_button = Button(proceed_buttons_cont, text="Next",
                             command=lambda: self.prepare_battleship_board_ui(self.game.board_size, 1))
        back_button = Button(proceed_buttons_cont, text="Back", command=lambda: self.start_menu_ui())
        (Label(proceed_buttons_cont, text="\nProceed to placing ships or return to main menu")
         .grid(row=0, column=1, columnspan=2))
        back_button.grid(row=1, column=0, sticky=W)
        next_button.grid(row=1, column=3, sticky=E)
        proceed_buttons_cont.pack()

    def fleet_change(self, label, mode, size, quantity):
        self.game.update_fleet(mode, size, quantity)
        label.config(text="Your fleet consists of following ships:\n" + self.game.get_fleet_info())

    def prepare_battleship_board_ui(self, board_size, player_number):
        self.clear_frame()
        self.geometry("")
        self.game.shots_p1 = [[0 for _ in range(board_size)] for _ in range(board_size)]  # 0-unknown, 1-shot
        self.game.shots_p2 = [[0 for _ in range(board_size)] for _ in range(board_size)]
        if player_number == 1:
            self.game.game_board_data_p1 = [[0 for _ in range(board_size)] for _ in range(board_size)]
        else:
            self.game.game_board_data_p2 = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.available_fleet = copy.copy(self.game.fleet)  # fleet available to place on the board

        if not self.game.pvp:
            self.game.game_board_data_p2 = [[0 for _ in range(board_size)] for _ in range(board_size)]
            self.computer_battleship_placement()

        # fleet info
        ships_string = "Ships remaining:\n" + self.game.get_fleet_info()
        ships_label = Label(self, text=ships_string)
        ships_label.pack()

        # canvas representing the game board
        cell_size = int(400 / board_size)
        canvas, board = self.init_canvas(cell_size)
        canvas.pack()

        (canvas.bind("<Button-1>", lambda event:
        self.place_ship(event, canvas, cell_size, board, self.ship_size.get(), self.orientation, ships_label,
                        ship_size_selector, player_number)))
        (canvas.bind("<Motion>", lambda event:
        self.hover_color(event, canvas, cell_size, board, self.ship_size.get(), self.orientation)))

        self.bind("<Key>", lambda event: self.rotate_ship(event, canvas, board, self.ship_size.get()))

        # select ship to place
        ship_selector_cont = Frame(self)
        Label(ship_selector_cont, text="Select ship size:").grid(row=0, column=0)
        ship_size_selector = Combobox(ship_selector_cont, textvariable=self.ship_size,
                                      values=list(sorted(self.game.fleet.keys(), reverse=True)), state="readonly")
        ship_size_selector.grid(row=0, column=1)
        self.ship_size.set(int(ship_size_selector["values"][0]))
        ship_selector_cont.pack()

        # navigation buttons
        proceed_buttons_cont = Frame(self)
        if self.game.pvp:
            if player_number == 1:
                next_button = Button(proceed_buttons_cont, text="Next",
                                     command=lambda: self.prepare_battleship_board_ui(self.game.board_size, 2))
                (Label(proceed_buttons_cont, text="\nProceed to placing ships for Player 2 or go back")
                 .grid(row=0, column=1, columnspan=2))
            else:
                next_button = Button(proceed_buttons_cont, text="Play",
                                     command=lambda: self.show_player_change_ui(1))
                (Label(proceed_buttons_cont, text="\nProceed to play Battleships or go back")
                 .grid(row=0, column=1, columnspan=2))
        else:
            next_button = Button(proceed_buttons_cont, text="Play", command=lambda: self.play_solo_ui())
            (Label(proceed_buttons_cont, text="\nProceed to play Battleships or go back")
             .grid(row=0, column=1, columnspan=2))
        back_button = Button(proceed_buttons_cont, text="Back", command=lambda: self.configure_game_ui())
        back_button.grid(row=1, column=0, sticky=W)
        next_button.grid(row=1, column=3, sticky=E)
        proceed_buttons_cont.pack()

    def place_ship(self, event, canvas, cell_size, board, ship_size, orientation, ships_label, ship_size_selector,
                   player_number):
        col = event.x // cell_size
        row = event.y // cell_size
        if self.can_place_ship(row, col, ship_size, orientation, player_number):
            self.game.add_ship_to_board(row, col, ship_size, orientation, player_number)
            self.update_available_ships(ship_size)

            ship_size_selector.config(value=list(sorted(self.available_fleet.keys(), reverse=True)))
            if len(self.available_fleet) == 0:
                ships_label.config(text="All ships placed. Click Next...")
            else:
                ship_size_selector.current(0)
                ships_label.config(text="Ships remaining:\n" + self.game.get_fleet_info(self.available_fleet))
            for i in range(ship_size):
                if orientation == "horizontal":
                    item = board[row][col + i]
                else:
                    item = board[row + i][col]
                canvas.itemconfig(item, fill='black')

    def can_place_ship(self, row, col, ship_size, orientation, player_number):
        if len(self.available_fleet) == 0:
            return False
        game_board = self.game.game_board_data_p1 if player_number == 1 else self.game.game_board_data_p2
        for i in range(ship_size):
            if orientation == "horizontal":
                if col + i >= self.game.board_size or game_board[row][col + i] != 0:
                    return False
            else:
                if row + i >= self.game.board_size or game_board[row + i][col] != 0:
                    return False
        return True

    def update_available_ships(self, ship_size):
        qty = self.available_fleet[ship_size]
        if qty > 1:
            self.available_fleet[ship_size] = qty - 1
        else:
            self.available_fleet.pop(ship_size)

    def hover_color(self, event, canvas, cell_size, cells, ship_size, orientation):
        if len(self.available_fleet) == 0:
            return

        col = event.x // cell_size
        row = event.y // cell_size
        col = col - 1 if col == self.game.board_size else col
        row = row - 1 if row == self.game.board_size else row

        if self.last_hovered != (row, col) or self.force_paint:
            if self.force_paint:
                self.force_paint = False
            prev_row, prev_col = self.last_hovered
            self.last_hovered = (row, col)
            self.paint(prev_row, prev_col, canvas, cells, ship_size, orientation, 'gray', 'white')
            self.paint(row, col, canvas, cells, ship_size, orientation, 'white', 'gray')

    def paint(self, row, col, canvas, cells, ship_size, orientation, previous_color, new_color):
        for i in range(ship_size):
            if orientation == "horizontal" and col + i < len(cells[row]):
                item = cells[row][col + i]
            elif orientation == "vertical" and row + i < len(cells):
                item = cells[row + i][col]
            else:
                continue
            if canvas.itemcget(item, 'fill') == previous_color:
                canvas.itemconfig(item, fill=new_color)

    def rotate_ship(self, event, canvas, cells, ship_size):
        if event.keysym in ["r", "R"]:
            self.paint(self.last_hovered[0], self.last_hovered[1], canvas, cells, ship_size, self.orientation, "gray",
                       "white")
            self.orientation = "vertical" if self.orientation == "horizontal" else "horizontal"
            self.force_paint = True

    def computer_battleship_placement(self):
        row = random.randint(0, self.game.board_size - 1)
        col = random.randint(0, self.game.board_size - 1)
        orientation = "horizontal" if random.randint(0, 1) == 0 else "vertical"
        available_fleet = copy.copy(self.game.fleet)

        for i in available_fleet.keys():
            for j in range(available_fleet[i]):
                while not self.can_place_ship(row, col, i, orientation, 2):
                    row = random.randint(0, self.game.board_size - 1)
                    col = random.randint(0, self.game.board_size - 1)
                    orientation = "horizontal" if random.randint(0, 1) == 0 else "vertical"
                self.game.add_ship_to_board(row, col, i, orientation, 2)

    def play_solo_ui(self):
        self.clear_frame()
        self.geometry("")
        self.unbind("<Key")
        cell_size = int(400 / self.game.board_size)

        player_board_info = Label(self, text="Your board:")
        opp_board_info = Label(self, text="Opponent's board:")
        player_board_info.grid(column=0, row=1)
        opp_board_info.grid(column=1, row=1)

        canvas_player, board_player = self.init_canvas(cell_size)
        canvas_opp, board_opp = self.init_canvas(cell_size)
        canvas_player.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        canvas_opp.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        next_button = Button(self, text="Next turn")
        next_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

    def play_pvp_ui(self, player_number):
        self.clear_frame()
        self.geometry("")
        self.player_can_shoot = True
        cell_size = int(400 / self.game.board_size)

        info = Label(self, text="Player " + str(player_number) + " turn")
        player_board_info = Label(self, text="Your board:")
        opp_board_info = Label(self, text="Opponent's board:")
        info.grid(column=0, row=0, columnspan=2)
        player_board_info.grid(column=0, row=1)
        opp_board_info.grid(column=1, row=1)

        canvas_player, board_player = self.init_canvas(cell_size)
        canvas_opp, board_opp = self.init_canvas(cell_size)
        canvas_player.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        canvas_opp.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        canvas_opp.bind("<Button-1>",
                        lambda event: self.shoot(event, canvas_opp, board_opp, 2 if player_number == 1 else 1))

        self.paint_game_board(canvas_player, board_player, False, player_number)
        self.paint_game_board(canvas_opp, board_opp, True, 2 if player_number == 1 else 1)

        next_button = Button(self, text="Next turn",
                             command=lambda: self.show_player_change_ui(2 if player_number == 1 else 1))
        next_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

    def init_canvas(self, cell_size):
        cols = self.game.board_size
        rows = self.game.board_size
        canvas = Canvas(self, width=cols * cell_size, height=rows * cell_size)

        board = []
        for row in range(rows):
            row_cells = []
            for col in range(cols):
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                rect = canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='black')
                row_cells.append(rect)
            board.append(row_cells)

        return canvas, board

    def show_player_change_ui(self, player_number):
        self.clear_frame()
        self.geometry("300x350")
        self.unbind("<Key>")
        Label(self, text="Player {} move\nClick next...".format(player_number), justify="center", height=10,
              font=("Arial", 16)).pack()
        Button(self, text="Next", command=lambda: self.play_pvp_ui(player_number)).pack()
        Button(self, text="Save and quit to menu", command=lambda: self.save_game_ui(player_number)).pack()

    def paint_game_board(self, canvas, board, only_shots, player_number):
        board_data = self.game.game_board_data_p1 if player_number == 1 else self.game.game_board_data_p2
        shots = self.game.shots_p2 if player_number == 1 else self.game.shots_p1
        cell_size = int(400 / self.game.board_size)
        if only_shots:
            for i in range(self.game.board_size):
                for j in range(self.game.board_size):
                    if shots[i][j] == 1:
                        x1, y1 = j * cell_size, i * cell_size
                        x2, y2 = (j + 1) * cell_size, (i + 1) * cell_size
                        if board_data[i][j] == 1:
                            canvas.create_line(x1, y1, x2, y2, fill='red', width=2)
                            canvas.create_line(x1, y2, x2, y1, fill='red', width=2)
                        else:
                            canvas.create_line(x1, y1, x2, y2, fill='gray', width=2)
                            canvas.create_line(x1, y2, x2, y1, fill='gray', width=2)
        else:
            for i in range(self.game.board_size):
                for j in range(self.game.board_size):
                    x1, y1 = j * cell_size, i * cell_size
                    x2, y2 = (j + 1) * cell_size, (i + 1) * cell_size
                    cell = board[i][j]
                    if board_data[i][j] == 1:
                        canvas.itemconfig(cell, fill='black')
                        if shots[i][j] == 1:
                            canvas.create_line(x1, y1, x2, y2, fill='red', width=2)
                            canvas.create_line(x1, y2, x2, y1, fill='red', width=2)

                    elif shots[i][j] == 1:
                        canvas.create_line(x1, y1, x2, y2, fill='gray', width=2)
                        canvas.create_line(x1, y2, x2, y1, fill='gray', width=2)

    def shoot(self, event, canvas, board, player_number):
        if not self.player_can_shoot:
            return

        cell_size = int(400 / self.game.board_size)
        col = event.x // cell_size
        row = event.y // cell_size
        if self.game.if_already_shot(row, col, player_number):
            return

        self.player_can_shoot = False
        game_over = self.game.shoot(row, col, player_number)
        self.paint_game_board(canvas, board, True, player_number)
        if game_over:
            self.game_over(1 if player_number == 2 else 2)

    def game_over(self, player_number):
        self.clear_frame()
        self.geometry("")

        label = Label(self, text="Player {} won!\nPlease input your name:".format(player_number), justify="center",
                      height=10)
        label.pack()

        name_input = Entry(self, justify="center")
        name_input.pack()

        button = Button(self, text="Proceed", command=lambda: self.add_to_leaderboard(name_input.get()))
        button.pack()
        show_leaderboard_button = Button(self, text="Show leaderboard", command=lambda: self.show_leaderboard_ui())
        show_leaderboard_button.pack()

    def add_to_leaderboard(self, player_name):
        if player_name != "":
            self.game.add_to_leaderboard(player_name)
        self.start_menu_ui()

    def show_leaderboard_ui(self):
        popup = Toplevel(self)
        data = Treeview(popup, columns=("Player Name", "Wins"), show="headings")
        data.heading("Player Name", text="Player Name")
        data.heading("Wins", text="Wins")
        for i in sorted(self.game.leaderboard.items(), key=lambda item: item[1], reverse=True):
            data.insert("", END, values=(i[0], i[1]))

        data.pack()
        back = Button(popup, text="Back", command=popup.destroy)
        back.pack()

    def quit_game(self):
        self.game.save_leaderboard("leaderboard.txt")
        self.destroy()

    def save_game_ui(self, player_number):
        self.clear_frame()
        self.geometry("300x300")
        Label(self, text="Provide a name for a game save", justify="center").pack()
        name_input = Entry(self, justify="center")
        name_input.pack()
        Button(self, text="Next", command=lambda: self.save_game(player_number, name_input.get())).pack()

    def save_game(self, player_number, name):
        if name not in self.game.list_game_saves():
            self.game.save_game(player_number, name)
            self.start_menu_ui()
        else:
            messagebox.showerror("Name not unique", "Save with given name already exists!\nTry again...")

    def load_save_ui(self):
        self.clear_frame()
        self.geometry("300x300")

        saves = Listbox(self, justify="center")
        for i in self.game.list_game_saves():
            saves.insert(END, i)
        saves.pack()
        play_button = Button(self, text="Play", command=lambda: self.prepare_game_from_save(saves.get(ACTIVE)))
        back_button = Button(self, text="Back", command=self.start_menu_ui)
        play_button.pack()
        back_button.pack()

    def prepare_game_from_save(self, save_name):
        self.game, player_number = game.game_from_save(save_name)
        self.show_player_change_ui(player_number)


if __name__ == "__main__":
    game = BattleshipsGame()
    gui = GUI(game)
    gui.mainloop()
