apis = ['odds-api', 'odds-jam']

markets = {
    'odds-api': [
        'NCAAF US College Football',
        'NFL US Football',
        'Aussie Football',
        'Euroleague Basketball',
        'NBA Basketball',
        'US College Basketball',
        'Cricket Big Bash League',
        'Cricket International Twenty20',
        'NHL Ice Hockey',
        'Mixed Martial Arts',
        'Aussie Rugby League',
        'Aussie Soccer'
    ],
    'odds-jam': [
        'NBA',
        'WNBA',
    ]
}

# Api request information, separated by api
keys = {
    'odds-api': {
        'NCAAF US College Football': 'americanfootball_ncaaf',
        'NFL US Football': 'americanfootball_nfl',
        'Aussie Football': 'aussierules_afl',
        'Euroleague Basketball': 'basketball_euroleague',
        'NBA Basketball': 'basketball_nba',
        'US College Basketball': 'basketball_ncaab',
        'Cricket Big Bash League': 'cricket_big_bash',
        'International Twenty20': 'cricket_international_t20',
        'NHL Ice Hockey': 'icehockey_nhl',
        'Mixed Martial Arts': 'mma_mixed_martial_arts',  # Working
        'Aussie Rugby League': 'rugbyleague_nrl',  # Working

    },
    'odds-jam': {
        
    }
}


responses_path = './responses'

