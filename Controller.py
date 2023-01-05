from GUI import GUI
from Model import Model


class Controller:
    def __init__(self, model, gui):
        self.model = model
        self.gui = gui

    def start(self):
        self.gui.start_gui()
