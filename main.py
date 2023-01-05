import os
import json

from Controller import Controller
from Model import Model
from GUI import GUI

import requests
from dotenv import load_dotenv


load_dotenv("LOGIN.env")
base_url = 'https://api.the-odds-api.com'
odds_json_path = 'response.json'

API_KEY = os.environ['API_KEY']


# American odds
def calculate_arbitrage_two_way(odds1, odds2, stake1):
    odds1 = american_to_decimal(odds1)
    odds2 = american_to_decimal(odds2)
    odds1_payout = round(odds1 * stake1, 2)

    stake2 = round(odds1_payout / odds2, 2)
    profit = round(odds1_payout - (stake1 + stake2), 3)
    return stake2, profit


def calculate_arbitrage_three_way(odds1, odds2, odds3, stake1):
    odds1 = american_to_decimal(odds1)
    odds2 = american_to_decimal(odds2)
    odds3 = american_to_decimal(odds3)

    odds1_payout = round(odds1 * stake1, 2)
    stake2 = round(odds1_payout / odds2, 2)
    stake3 = round(odds1_payout / odds3, 2)
    profit = round(odds1_payout - (stake1 + stake2 + stake3), 3)
    return stake2, stake3, profit


def american_to_decimal(odds):
    if odds < 0:
        return -100 / odds + 1
    else:
        return odds / 100 + 1


def get_odds_json(sports_key, region, markets):
    response = requests.get(f'{base_url}/v4/sports/{sports_key}/odds/?apiKey={API_KEY}'
                            f'&regions={region}&markets={markets},spreads&oddsFormat=american')

    data_response = json.loads(response.text)

    with open('response.json', 'w') as file:
        json.dump(data_response, file)
    return response.json()


def parse_json(json_data):
    sports_data = {}
    for game in json_data:
        game_data = {}
        home_team = game['home_team']
        away_team = game['away_team']
        game_name = f'{away_team} at {home_team}'
        game_data['home_team'] = home_team
        game_data['away_team'] = away_team
        home_prices = []
        away_prices = []
        draw_prices = []
        for bookmaker in game['bookmakers']:
            bookmaker_key = bookmaker['key']
            bookmaker_title = bookmaker['title']
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == home_team:
                            home_price = outcome['price']
                            home_prices.append((home_price, bookmaker_title))
                        elif outcome['name'] == away_team:
                            away_price = outcome['price']
                            away_prices.append((away_price, bookmaker_title))
                        elif outcome['name'] == 'Draw':
                            draw_price = outcome['price']
                            draw_prices.append((draw_price, bookmaker_title))
                        else:
                            print(outcome['name'])
                            raise Exception(f"Team not home or away")
                    break
                else:
                    continue

        game_data['home_prices'] = home_prices
        game_data['away_prices'] = away_prices
        game_data['draw_prices'] = draw_prices
        if len(draw_prices) == 0:
            game_data['three_way'] = False
        else:
            game_data['three_way'] = True
        sports_data[game_name] = game_data

    # print(sports_data)
    return sports_data


def find_arb_opportunities_two_way(match, home_win_stake):
    results = []

    home_prices = match['home_prices']
    away_prices = match['away_prices']
    home_team = match['home_team']
    away_team = match['away_team']
    for i in range(0, len(home_prices)):
        for j in range(0, len(away_prices)):
            home_odds = home_prices[i][0]
            home_bookie = home_prices[i][1]
            away_odds = away_prices[j][0]
            away_bookie = away_prices[j][1]
            away_stake, profit = calculate_arbitrage_two_way(home_odds, away_odds, home_win_stake)
            description = f"${home_win_stake} on {home_team} @ {home_odds} ({home_bookie}) and ${away_stake} on {away_team} " \
                          f"@ {away_odds} ({away_bookie}) for profit of {profit}"
            results.append((profit, description))

    return results


def find_arb_opportunities_three_way(match, home_win_stake):
    results = []

    home_prices = match['home_prices']
    away_prices = match['away_prices']
    draw_prices = match['draw_prices']
    home_team = match['home_team']
    away_team = match['away_team']
    for i in range(0, len(home_prices)):
        for j in range(0, len(away_prices)):
            for u in range(0, len(draw_prices)):
                home_odds = home_prices[i][0]
                home_bookie = home_prices[i][1]
                away_odds = away_prices[j][0]
                away_bookie = away_prices[j][1]
                draw_odds = draw_prices[u][0]
                draw_bookie = draw_prices[u][1]
                away_stake, draw_stake, profit = \
                    calculate_arbitrage_three_way(home_odds, away_odds, draw_odds, home_win_stake)
                description = f"${home_win_stake} on {home_team} @ {home_odds} ({home_bookie}), ${away_stake} on {away_team} " \
                              f"@ {away_odds} ({away_bookie}), and {draw_stake} for draw @ {draw_odds} " \
                              f"({draw_bookie}) for profit of {profit}"
                results.append((profit, description))

    return results


def find_arbitrage(games_data, stake):
    results = []
    for match in games_data:
        match = games_data.get(match)
        if match['three_way']:
            results.extend(find_arb_opportunities_three_way(match, stake))
        else:
            results.extend(find_arb_opportunities_two_way(match, stake))

    results = sorted(results, key=lambda x: x[0], reverse=True)
    return results


if __name__ == '__main__':
    model = Model()
    gui = GUI()
    controller = Controller(model, gui)

    controller.start()

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


