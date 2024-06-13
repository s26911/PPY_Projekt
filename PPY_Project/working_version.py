from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox


class BattleshipsGame:
    def __init__(self):
        self.pvp = True
        self.board_size = 10
        self.fleet = {5: 1, 4: 1, 3: 2, 2: 1}

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
            else:
                self.fleet[size] -= quantity
                if self.fleet[size] == 0:
                    self.fleet.pop(size)

    def get_fleet_info(self):
        string = "Your fleet consists of following ships:\n"
        for ship_size in sorted(self.fleet.keys(), reverse=True):
            string += "Size: {}, quantity: {}\n".format(ship_size, self.fleet[ship_size])
        return string


class GUI(Tk):
    def __init__(self, game):
        super().__init__()
        self.v = StringVar()
        self.game = game
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
        ships_string = self.game.get_fleet_info()
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
        next_button = Button(proceed_buttons_cont, text="Next")
        back_button = Button(proceed_buttons_cont, text="Back", command=lambda: self.start_menu_ui())
        (Label(proceed_buttons_cont, text="\nProceed to placing ships or return to main menu")
         .grid(row=0, column=1, columnspan=2))
        back_button.grid(row=1, column=0, sticky=W)
        next_button.grid(row=1, column=3, sticky=E)
        proceed_buttons_cont.pack()

    def fleet_change(self, label, mode, size, quantity):
        self.game.update_fleet(mode, size, quantity)
        label.config(text=self.game.get_fleet_info())


if __name__ == "__main__":
    game = BattleshipsGame()
    gui = GUI(game)
    gui.mainloop()
