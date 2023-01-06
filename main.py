import os
import json

from Controller import Controller
from Model import Model
from GUI import GUI

if __name__ == '__main__':
    model = Model()
    gui = GUI()
    controller = Controller(model, gui)

    gui.controller.start()

    # get_odds_json('soccer_uefa_champs_league', 'us', 'h2h')
    #
    # with open(odds_json_path) as file:
    #     data = json.load(file)
    # games_data = parse_json(data)
    # # print(games_data)
    #
    # arbitrage_results = find_arbitrage(games_data, 100)
    # for tup in arbitrage_results:
    #     print(tup[1])

    # print(american_to_decimal(210))
    # print(calculate_arbitrage(210, -120, 100))

    # get_odds_json('americanfootball_nfl', 'us', 'h2h')


