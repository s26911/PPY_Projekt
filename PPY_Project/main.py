from tkinter import *
from tkinter.ttk import Combobox

from Configuration import Config

config = Config()


class tkinterApp(Tk):
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        self.geometry("300x200")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, ConfigurationPage, BattleshipSelectionPage):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# first window frame startpage

class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        button1 = Button(self, text="Start new game",
                         command=lambda: controller.show_frame(ConfigurationPage))
        button2 = Button(self, text="Load game",
                         command=lambda: controller.show_frame(BattleshipSelectionPage))

        button1.pack(pady=5)
        button2.pack(pady=5)


class ConfigurationPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        mainLabel = Label(self, text="Select options for your game")
        mainLabel.grid(row=0, column=0, columnspan=2)

        modeLabel = Label(self, text="Select mode:")
        mode = Combobox(self, values=["Player vs Player", "Player vs Computer"])
        mode.set("Player vs Player")
        modeLabel.grid(row=1, column=0)
        mode.grid(row=1, column=1)

        nextButton = Button(self, text="Next", command=lambda: self.next(controller, mode.get()))
        # backButton = Button(self, text="Back", command=lambda: controller.show_frame(StartPage))

        nextButton.grid(row=2, column=0, columnspan=2)

    def next(self, controller, selected_option):
        if selected_option == "Player vs Player":
            config.pvp = True
        else:
            config.pvp = False
        controller.show_frame(BattleshipSelectionPage)


# third window frame page2
class BattleshipSelectionPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="୧༼ಠ益ಠ╭∩╮༽")
        label.pack()


app = tkinterApp()
app.mainloop()
