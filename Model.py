from utils import keys, responses_path
import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Tuple

base_url_odds_api = 'https://api.the-odds-api.com'


# American odds
def calculate_arbitrage_two_way(odds1, odds2, stake1) -> Tuple[int, int]:
    odds1 = american_to_decimal(odds1)
    odds2 = american_to_decimal(odds2)
    odds1_payout = round(odds1 * stake1, 2)

    stake2 = round(odds1_payout / odds2, 2)
    profit = round(odds1_payout - (stake1 + stake2), 3)
    return stake2, profit


def calculate_arbitrage_three_way(odds1, odds2, odds3, stake1) -> Tuple[int, int, int]:
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


def parse_json_odds_api(json_data, date_time_string):

    sports_data = {}
    for game in json_data:
        game_data = {'time': date_time_string}
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


def find_arb_opportunities_two_way(match, home_win_stake, date_time_string) -> List[Tuple[int, str]]:
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
            roi = round(profit / (home_win_stake + away_stake), 2)
            description = f"{date_time_string} ${home_win_stake} on {home_team} @ {home_odds} ({home_bookie}) " \
                          f"and ${away_stake} on {away_team} " \
                          f"@ {away_odds} ({away_bookie}) for {roi}% ROI and a profit of ${profit}"
            results.append((profit, description))

    return results


def find_arb_opportunities_three_way(match, home_win_stake, date_time_string) -> List[Tuple[int, str]]:
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
                roi = round(profit / (home_win_stake + away_stake + draw_stake), 2)
                description = f"{date_time_string} ${home_win_stake} on {home_team} @ {home_odds} ({home_bookie}), " \
                              f"${away_stake} on {away_team} " \
                              f"@ {away_odds} ({away_bookie}), and {draw_stake} for draw @ {draw_odds} " \
                              f"({draw_bookie}) for {roi}% ROI and a profit of ${profit}"
                results.append((profit, description))

    return results


def find_arbitrage_opportunities(games_data, stake) -> List[Tuple[int, str]]:
    results = []
    for match in games_data:
        match = games_data.get(match)
        date_time_string = match['time']
        if match['three_way']:
            results.extend(find_arb_opportunities_three_way(match, stake, date_time_string))
        else:
            results.extend(find_arb_opportunities_two_way(match, stake, date_time_string))

    results = sorted(results, key=lambda x: x[0], reverse=True)
    return results


# Finds the index of the first positive element in arb_list
# Returns -1 if there are no positive numbers
def find_first_pos_index(arb_list: List[Tuple[int, str]], low, high):
    if high >= low:
        mid = int((high + low) / 2)
        if arb_list[mid][0] >= 0:
            if mid == 0 or arb_list[mid - 1][0] < 0:
                return mid
            else:
                return find_first_pos_index(arb_list, low, mid - 1)
        else:
            return find_first_pos_index(arb_list, mid + 1, high)
    return -1


class Model:
    def __init__(self):
        self.arb_opportunities = set()
        self.games_data_list = []

        load_dotenv("LOGIN.env")
        self.API_KEY = os.environ['API_KEY']

    # Gets the opportunities from an api and market, calculates arbitrage, and adds them to the arb_opportunities
    def get_data_and_find_arbitrage(self, api, market):
        if api == 'odds-api':
            sports_key = keys.get(api).get(market)
            date_time_string, json_data = self.get_odds_json_odds_api(base_url_odds_api, sports_key, 'us', 'h2h')
            sports_data = parse_json_odds_api(json_data, date_time_string)
        elif api == 'odds-jam':
            print("This api is not supported yet")
            return
        else:
            raise Exception("Unrecognized api")

        self.games_data_list.append(sports_data)
        arb_results = find_arbitrage_opportunities(sports_data, 100)

        for tup in arb_results:
            self.arb_opportunities.add(tup)

    def get_odds_json_odds_api(self, url, sports_key, region, markets):
        current_time = datetime.now()

        response = requests.get(f'{url}/v4/sports/{sports_key}/odds/?apiKey={self.API_KEY}'
                                f'&regions={region}&markets={markets},spreads&oddsFormat=american')

        data_response = json.loads(response.text)

        date_time_string = f'{current_time.year}-{current_time.month}-{current_time.day}-{current_time.hour}' \
                           f'-{current_time.minute}-{current_time.second}'

        if not os.path.exists(responses_path):
            os.mkdir(responses_path)

        with open(responses_path + '/' + date_time_string + ' odds-api ' + sports_key + '.json', 'w') as file:
            json.dump(data_response, file)
        return date_time_string, response.json()

    def get_opportunities(self) -> List[str]:
        arb_opp_list = list(self.arb_opportunities)
        arb_opp_list = sorted(arb_opp_list, key=lambda x: x[0], reverse=True)
        arb_opportunities_only_str = []
        for profit, desc in arb_opp_list:
            arb_opportunities_only_str.append(desc)
        if len(arb_opportunities_only_str) <= 20:
            # Less than 20 elements
            return arb_opp_list
        elif find_first_pos_index(arb_opp_list, 0, len(arb_opp_list) - 1) == -1:
            # Greater than 20 elements but no positive arbitrage
            return arb_opportunities_only_str[:20]
        elif find_first_pos_index(arb_opp_list, 0, len(arb_opp_list) - 1) > -1:
            pos_index = find_first_pos_index(arb_opp_list, 0, len(arb_opp_list) - 1)
            # Greater than 20 elements and there is a positive arbitrage
            return arb_opportunities_only_str[:min(pos_index + 5, len(arb_opp_list) - 1)]

        return arb_opportunities_only_str[:20]

    def clear_opportunities(self):
        self.arb_opportunities = set()
        self.games_data_list = []

    def load_data_from_file(self, path):
        file_name = path.split("/")[len(path.split("/"))- 1]
        split_by_space = file_name.split(" ")
        date_string = split_by_space[0]
        api = split_by_space[1]

        with open(path, 'r') as file:
            json_data = json.load(file)

        if api == 'odds-api':
            sports_data = parse_json_odds_api(json_data, date_string)
        else:
            raise Exception('Unrecognized API. The file name must be in the format: "{date} {api} ..."')

        self.games_data_list.append(sports_data)
        arb_results = find_arbitrage_opportunities(sports_data, 100)

        for tup in arb_results:
            self.arb_opportunities.add(tup)


