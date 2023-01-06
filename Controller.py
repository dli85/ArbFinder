from GUI import GUI, ask_confirmation, load_file, prompt_for_number
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

    def update_stake(self):
        new_stake = prompt_for_number()
        self.model.update_stake(new_stake)
        self.gui.update_scrollable_info(self.model.get_opportunities())

    def load_json(self):
        path = load_file()
        self.model.load_data_from_file(path)
        self.gui.update_scrollable_info(self.model.get_opportunities())
