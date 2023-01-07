from GUI import GUI, ask_confirmation, load_file, prompt_for_number, show_error_message
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
            try:
                self.model.get_data_and_find_arbitrage(api, market)
            except ValueError as error:
                show_error_message("No games found", error.args[0])
            except NameError as error:
                show_error_message("API error", error.args[0])
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
        try:
            self.model.load_data_from_file(path)
        except ValueError as error:
            show_error_message("Loading error", error.args[0])
        except NameError as error:
            show_error_message("Name error", error.args[0])

        self.gui.update_scrollable_info(self.model.get_opportunities())
