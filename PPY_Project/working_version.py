from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
import copy


class BattleshipsGame:
    def __init__(self):
        self.pvp = True
        self.board_size = 10
        self.fleet = {5: 1, 4: 1, 3: 2, 2: 1}
        self.game_board = [[]]  # 2-dimensional int array, 0:empty, 1:ship, 2:sunken

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

    def add_ship_to_board(self, row, column, ship_size, orientation):
        if orientation == "horizontal":
            for i in range(ship_size):
                self.game_board[row][column + i] = 1
        else:
            for i in range(ship_size):
                self.game_board[row + i][column] = 1


class GUI(Tk):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.ship_size = IntVar()
        self.orientation = "horizontal"
        self.available_fleet = {}
        self.title("Battleships")
        self.start_menu_ui()

    def start_menu_ui(self):
        self.clear_frame()
        self.geometry("200x100")
        Button(self, text="Start new game", command=lambda: self.configure_game_ui()).pack(pady=5)
        Button(self, text="Load game").pack(pady=5)

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
                             command=lambda: self.prepare_battleship_board_ui(self.game.board_size))
        back_button = Button(proceed_buttons_cont, text="Back", command=lambda: self.start_menu_ui())
        (Label(proceed_buttons_cont, text="\nProceed to placing ships or return to main menu")
         .grid(row=0, column=1, columnspan=2))
        back_button.grid(row=1, column=0, sticky=W)
        next_button.grid(row=1, column=3, sticky=E)
        proceed_buttons_cont.pack()

    def fleet_change(self, label, mode, size, quantity):
        self.game.update_fleet(mode, size, quantity)
        label.config(text="Your fleet consists of following ships:\n" + self.game.get_fleet_info())

    def prepare_battleship_board_ui(self, board_size):
        self.clear_frame()
        self.geometry("")
        self.game.game_board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.available_fleet = copy.copy(self.game.fleet)  # fleet available to place on the board

        # fleet info
        ships_string = "Ships remaining:\n" + self.game.get_fleet_info()
        ships_label = Label(self, text=ships_string)
        ships_label.pack()

        # canvas representing the game board
        cols = board_size
        rows = board_size
        cell_size = int(400 / board_size)
        canvas = Canvas(self, width=cols * cell_size, height=rows * cell_size)
        canvas.pack()

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

        (canvas.bind("<Button-1>", lambda event:
        self.place_ship(event, canvas, cell_size, board, self.ship_size.get(), self.orientation, ships_label, ship_size_selector)))

        # select ship to place
        ship_selector_cont = Frame(self)
        Label(ship_selector_cont, text="Select ship size:").grid(row=0, column=0)
        ship_size_selector = Combobox(ship_selector_cont, textvariable=self.ship_size,
                                      values=list(sorted(self.game.fleet.keys(), reverse=True)))
        ship_size_selector.grid(row=0, column=1)
        self.ship_size.set(int(ship_size_selector["values"][0]))
        ship_selector_cont.pack()

        # navigation buttons
        proceed_buttons_cont = Frame(self)
        if self.game.pvp:
            next_button = Button(proceed_buttons_cont, text="Next")
            (Label(proceed_buttons_cont, text="\nProceed to placing ships for Player 2 or go back")
             .grid(row=0, column=1, columnspan=2))
        else:
            next_button = Button(proceed_buttons_cont, text="Play")
            (Label(proceed_buttons_cont, text="\nProceed to play Battleships or go back")
             .grid(row=0, column=1, columnspan=2))
        back_button = Button(proceed_buttons_cont, text="Back", command=lambda: self.configure_game_ui())
        back_button.grid(row=1, column=0, sticky=W)
        next_button.grid(row=1, column=3, sticky=E)
        proceed_buttons_cont.pack()

    def place_ship(self, event, canvas, cell_size, board, ship_size, orientation, ships_label, ship_size_selector):
        col = event.x // cell_size
        row = event.y // cell_size
        if self.can_place_ship(canvas, row, col, ship_size, board, orientation):
            self.game.add_ship_to_board(row, col, ship_size, orientation)
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

            #     hover_state["clicked"][(row, col + i) if orientation[0] == "horizontal" else (row + i, col)] = True
            # ships.append((row, col, ship_size, orientation[0]))

    def can_place_ship(self, canvas, row, col, ship_size, board, orientation):
        if len(self.available_fleet) == 0:
            return False
        for i in range(ship_size):
            if orientation == "horizontal":
                if col + i >= len(board[row]) or canvas.itemcget(board[row][col + i], 'fill') == 'black':
                    return False
            else:
                if row + i >= len(board) or canvas.itemcget(board[row + i][col], 'fill') == 'black':
                    return False
        return True

    def update_available_ships(self, ship_size):
        qty = self.available_fleet[ship_size]
        if qty > 1:
            self.available_fleet[ship_size] = qty - 1
        else:
            self.available_fleet.pop(ship_size)

if __name__ == "__main__":
    game = BattleshipsGame()
    gui = GUI(game)
    gui.mainloop()
