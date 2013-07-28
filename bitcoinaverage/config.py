from decimal import Decimal
import bitcoinaverage.server

API_DOCUMENT_ROOT = bitcoinaverage.server.API_DOCUMENT_ROOT
API_FILES = {'TICKER_PATH': 'ticker/',
             'EXCHANGES_PATH': 'exchanges/',
             'ALL_FILE': 'all',
             'IGNORED_FILE': 'ignored',
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
                    'btce': {'usd_api_url': 'https://btc-e.com/api/2/btc_usd/ticker',
                             'eur_api_url': 'https://btc-e.com/api/2/btc_eur/ticker',
                             'rur_api_url': 'https://btc-e.com/api/2/btc_rur/ticker',
                                 },
                    'bitcurex': { 'eur_api_url': 'https://eur.bitcurex.com/data/ticker.json',
                                    },
                    'vircurex': { 'usd_api_url': 'https://vircurex.com/api/get_info_for_1_currency.json?base=BTC&alt=USD',
                                  'eur_api_url': 'https://vircurex.com/api/get_info_for_1_currency.json?base=BTC&alt=EUR',
                                    },


                    'campbx': {'api_url': 'http://campbx.com/api/xticker.php',  #no volume data now
                                 },

                    'cavirtex': False,
                    'libertybit': False,
                    'canadianbitcoins': False,
                    }

