from decimal import Decimal

COUCHDB = {'RATES_URL': 'http://88.198.122.134:5984/ba/rates',
           }

API_QUERY_FREQUENCY = 15

DEC_PLACES = Decimal('0.00')

CURRENCY_LIST = {'USD':'USD',
                 'EUR':'EUR',
                 'GBP':'GBP',
                 'CAD':'CAD',
                 'RUR':'RUR'}

EXCHANGE_LIST = {
                    'mtgox': {'usd_api_url': 'http://data.mtgox.com/api/2/BTCUSD/money/ticker',
                              'eur_api_url': 'http://data.mtgox.com/api/2/BTCEUR/money/ticker',
                              'gbp_api_url': 'http://data.mtgox.com/api/2/BTCGBP/money/ticker',
                              'cad_api_url': 'http://data.mtgox.com/api/2/BTCCAD/money/ticker',
                              'rur_api_url': 'http://data.mtgox.com/api/2/BTCRUB/money/ticker',
                                  },
                    'bitstamp': {'api_url': 'https://www.bitstamp.net/api/ticker/',
                                   },
                    'campbx': {'api_url': 'http://campbx.com/api/xticker.php',
                                 },
                    'btce': {'usd_api_url': 'https://btc-e.com/api/2/btc_usd/ticker',
                             'eur_api_url': 'https://btc-e.com/api/2/btc_eur/ticker',
                             'rur_api_url': 'https://btc-e.com/api/2/btc_rur/ticker',
                                 },
                    }

