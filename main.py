import os
import json

import requests
from dotenv import load_dotenv

load_dotenv("LOGIN.env")
base_url = 'https://api.the-odds-api.com'
odds_json_path = 'response.json'

API_KEY = os.environ['API_KEY']


# American odds
def calculate_arbitrage(odds1, odds2, stake1):
    odds1 = american_to_decimal(odds1)
    odds2 = american_to_decimal(odds2)
    odds1_payout = round(odds1 * stake1, 2)

    stake2 = round(odds1_payout / odds2, 2)
    profit = round(odds1_payout - (stake1 + stake2), 3)
    return stake2, profit


def american_to_decimal(odds):
    if odds < 0:
        return -100 / odds + 1
    else:
        return odds / 100 + 1


def get_odds_json(sports_key, region, markets):
    sports_key = 'americanfootball_nfl'
    region = "us"
    markets = "h2h"
    response = requests.get(f'{base_url}/v4/sports/{sports_key}/odds/?apiKey={API_KEY}'
                            f'&regions={region}&markets={markets},spreads&oddsFormat=american')

    data_response = json.loads(response.text)

    with open('response.json', 'w') as file:
        json.dump(data_response, file)
    return response.json()


def parse_json_moneyline(json_data):
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
                        else:
                            raise Exception("Team not home or away")
                    break
                else:
                    continue

        game_data['home_prices'] = home_prices
        game_data['away_prices'] = away_prices
        sports_data[game_name] = game_data

    # print(sports_data)
    return sports_data


def find_arb_opportunities(games_data):
    results = []
    for match in games_data:
        match = games_data.get(match)
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
                home_stake = 100
                away_stake, profit = calculate_arbitrage(home_odds, away_odds, home_stake)
                description = f"{home_stake} on {home_team} (@ {home_odds} {home_bookie}) and {away_stake} on {away_team} " \
                              f"(@ {away_odds} {away_bookie}) for profit of {profit}"
                results.append((profit, description))
    results = sorted(results, key=lambda x: x[0], reverse=True)
    return results


if __name__ == '__main__':
    with open(odds_json_path) as file:
        data = json.load(file)
    games_data = parse_json_moneyline(data)
    # print(games_data)
    arbitrage_results = find_arb_opportunities(games_data)
    for tup in arbitrage_results:
        print(tup[1])
    # print(american_to_decimal(210))
    # print(calculate_arbitrage(210, -120, 100))

    # get_odds_json('americanfootball_nfl', 'us', 'h2h')
