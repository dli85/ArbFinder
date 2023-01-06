from GUI import GUI, ask_confirmation
from Model import Model


class Controller:
    def __init__(self, model: Model, gui: GUI):
        self.model = model
        self.gui = gui
        self.gui.set_controller(self)

    def start(self):
        self.gui.start_gui()

    def get_data_and_update_info(self):
        if ask_confirmation():
            api, market = self.gui.get_api_market()
            self.model.get_data_and_find_arbitrage(api, market)
            self.gui.update_scrollable_info(self.model.get_opportunities())

    def clear_list(self):
        self.gui.update_scrollable_info([])
        self.model.clear_opportunities()
