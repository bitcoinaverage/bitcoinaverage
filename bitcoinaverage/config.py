from decimal import Decimal

import bitcoinaverage.server

INDEX_DOCUMENT_NAME = 'default' #directory index document name, needs to match webserver setting
CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME = 'currencies'
CHARTS_DUMMY_PAGES_SUBFOLDER_NAME = 'charts'

FRONTEND_LEGEND_SLOTS = 20
FRONTEND_MAJOR_CURRENCIES = 6

API_FILES = {'TICKER_PATH': 'ticker/',
             'EXCHANGES_PATH': 'exchanges/',
             'ALL_FILE': 'all',
             'IGNORED_FILE': 'ignored',
             }

API_REQUEST_HEADERS = {'User-Agent': 'bitcoinaverage.com query bot',
                       'Origin': 'bitcoinaverage.com'}

if hasattr(bitcoinaverage.server, 'DEFAULT_API_QUERY_REQUEST_HEADER_USER_AGENT_OVERRIDE'):
    API_REQUEST_HEADERS['User-Agent'] = bitcoinaverage.server.DEFAULT_API_QUERY_REQUEST_HEADER_USER_AGENT_OVERRIDE

FRONTEND_QUERY_FREQUENCY = 15 #seconds between AJAX requests from frontend to our API
HISTORY_QUERY_FREQUENCY = 15 #seconds between history_daemon requests
FIAT_RATES_QUERY_FREQUENCY = 3600 #seconds between requests for fiat exchange rates
API_CALL_TIMEOUT_THRESHOLD = 15 #seconds before exchange API call timeout. exchange may have multiple calls
                                #and total time spent querying one exchange will be threshold * number of calls

#seconds between calls to various exchanges APIs
API_QUERY_FREQUENCY = {
                        'default': 60,
                        'bitcoincharts': 900,
                        'mtgox': 55,
                        'bitstamp': 55,
                        'btce': 55,
                        'bitcurex': 55,
                        'vircurex': 55,
                        'bitbargain': 55,
                        'localbitcoins': 55,
                        'cryptotrade': 55,
                        'rocktrading': 55,
                        'bitcash': 55,
                        'intersango': 55,
                        'bit2c': 55,
                        'kapiton': 55,
                        'rmbtb': 55,
                        'btcchina': 55,
                        'fxbtc': 55,
                        'bter': 55,
                        'goxbtc': 55,
                        'okcoin': 55,
                        'mercado': 55,
                        'bitx': 55,
                        'btctrade': 55,
                        'justcoin': 55,
                        'kraken': 55,
                        'bitkonan': 55,
}


if hasattr(bitcoinaverage.server, 'DEFAULT_API_QUERY_FREQUENCY_OVERRIDE'):
    API_QUERY_FREQUENCY['default'] = bitcoinaverage.server.DEFAULT_API_QUERY_FREQUENCY_OVERRIDE

#seconds before a consequently failing API will be put into ignored list (in the mean time data will be taken from cache)
API_IGNORE_TIMEOUT = 1800

DEC_PLACES = Decimal('0.00')

CURRENCY_LIST = ('USD',
                 'EUR',
                 'GBP',
                 'CNY',
                 'CAD',
                 'PLN',
                 'JPY',
                 'RUB',
                 'AUD',
                 'SEK',
                 'BRL',
                 'CZK',
                 'NZD',
                 'SGD',
                 'ZAR',
                 'NOK',
                 'ILS',
                 # 'DKK',
                 # 'CHF',
                 # 'HKD',
                 # 'THB',
                    )

BITCOIN_CHARTS_API_URL = 'https://api.bitcoincharts.com/v1/markets.json'

EXCHANGE_LIST = {
                    'mtgox': {'usd_api_url': 'https://data.mtgox.com/api/2/BTCUSD/money/ticker',
                              'eur_api_url': 'https://data.mtgox.com/api/2/BTCEUR/money/ticker',
                              'gbp_api_url': 'https://data.mtgox.com/api/2/BTCGBP/money/ticker',
                              'cad_api_url': 'https://data.mtgox.com/api/2/BTCCAD/money/ticker',
                              'pln_api_url': 'https://data.mtgox.com/api/2/BTCPLN/money/ticker',
                              'rub_api_url': 'https://data.mtgox.com/api/2/BTCRUB/money/ticker',
                              'aud_api_url': 'https://data.mtgox.com/api/2/BTCAUD/money/ticker',
                              'chf_api_url': 'https://data.mtgox.com/api/2/BTCCHF/money/ticker',
                              'cny_api_url': 'https://data.mtgox.com/api/2/BTCCNY/money/ticker',
                              'dkk_api_url': 'https://data.mtgox.com/api/2/BTCDKK/money/ticker',
                              'hkd_api_url': 'https://data.mtgox.com/api/2/BTCHKD/money/ticker',
                              'jpy_api_url': 'https://data.mtgox.com/api/2/BTCJPY/money/ticker',
                              'nzd_api_url': 'https://data.mtgox.com/api/2/BTCNZD/money/ticker',
                              'sgd_api_url': 'https://data.mtgox.com/api/2/BTCSGD/money/ticker',
                              'sek_api_url': 'https://data.mtgox.com/api/2/BTCSEK/money/ticker',
                              'bitcoincharts_symbols': {'USD': 'mtgoxUSD',
                                                        'EUR': 'mtgoxEUR',
                                                        'GBP': 'mtgoxGBP',
                                                        'CAD': 'mtgoxCAD',
                                                        'PLN': 'mtgoxPLN',
                                                        'RUB': 'mtgoxRUB',
                                                        'AUD': 'mtgoxAUD',
                                                        'CHF': 'mtgoxCHF',
                                                        'CNY': 'mtgoxCNY',
                                                        'DKK': 'mtgoxDKK',
                                                        'HKD': 'mtgoxHKD',
                                                        'JPY': 'mtgoxJPY',
                                                        'NZD': 'mtgoxNZD',
                                                        'SGD': 'mtgoxSGD',
                                                        'SEK': 'mtgoxSEK',
                                                        },

                                  },
                    'bitstamp': {'api_url': 'https://www.bitstamp.net/api/ticker/',
                                 'bitcoincharts_symbols': {'USD': 'bitstampUSD',
                                                           },
                                   },
                    'btce': {'usd_api_url': 'https://btc-e.com/api/2/btc_usd/ticker',
                             'eur_api_url': 'https://btc-e.com/api/2/btc_eur/ticker',
                             'rur_api_url': 'https://btc-e.com/api/2/btc_rur/ticker',
                                 'bitcoincharts_symbols': {'USD': 'btceUSD',
                                                           },
                                 },
                    'bitcurex': { 'eur_ticker_url': 'https://eur.bitcurex.com/data/ticker.json',
                                  'eur_trades_url': 'https://eur.bitcurex.com/data/trades.json',
                                  'pln_ticker_url': 'https://pln.bitcurex.com/data/ticker.json',
                                  'pln_trades_url': 'https://pln.bitcurex.com/data/trades.json',
                                    },
                    'vircurex': { 'usd_api_url': 'https://vircurex.com/api/get_info_for_1_currency.json?base=BTC&alt=USD',
                                  'eur_api_url': 'https://vircurex.com/api/get_info_for_1_currency.json?base=BTC&alt=EUR',
                                    },

                    'bitbargain': {'gbp_api_url': 'https://bitbargain.co.uk/api/bbticker'},

                    'localbitcoins': {'api_url': 'https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/',
                                      'bitcoincharts_symbols': {'USD': 'localbtcUSD',
                                                                'EUR': 'localbtcEUR',
                                                                'GBP': 'localbtcGBP',
                                                                'CAD': 'localbtcCAD',
                                                                'NOK': 'localbtcNOK',
                                                                'CZK': 'localbtcCZK',
                                                                'NZD': 'localbtcNZD',
                                                                'ZAR': 'localbtcZAR',
                                                                'SEK': 'localbtcSEK',
                                                                'SGD': 'localbtcSGD',
                                                                'AUD': 'localbtcAUD',
                                                                'BRL': 'localbtcBRL',
                                                                },
                                         },

                    'cryptotrade':{'usd_api_url': 'https://crypto-trade.com/api/1/ticker/btc_usd',
                                      'bitcoincharts_symbols': {'USD': 'crytrUSD',
                                                                },
                                   },
                    'rocktrading':{# 'usd_ticker_url': 'https://www.therocktrading.com/api/ticker/BTCUSD',
                                   # 'usd_trades_url': 'https://www.therocktrading.com/api/trades/BTCUSD',
                                   'eur_ticker_url': 'https://www.therocktrading.com/api/ticker/BTCEUR',
                                   'eur_trades_url': 'https://www.therocktrading.com/api/trades/BTCEUR',
                                    },

                    'bitcash': {'czk_api_url': 'https://bitcash.cz/market/api/BTCCZK/ticker.json',
                                'bitcoincharts_symbols': {'CZK': 'bitcashCZK',
                                                           },
                                  },
                    #with intersango only EUR is used, because trader needs to convert to EUR to add/withdraw with it
                    'intersango': {'ticker_url': 'https://intersango.com/api/ticker.php',
                                   },

                    'bit2c': {'ticker_url' : 'https://www.bit2c.co.il/Exchanges/BtcNis/Ticker.json',
                                },
                    'kapiton': {'ticker_url': 'https://kapiton.se/api/0/ticker',
                                },

                    'rmbtb': {'ticker_url': 'https://www.rmbtb.com/api/thirdparty/ticker/',
                                },

                    'btcchina':  {'ticker_url': 'https://data.btcchina.com/data/ticker',
                                    },
                    'fxbtc':  {'ticker_url': 'https://data.fxbtc.com/api?op=query_ticker&symbol=btc_cny',
                                    },
                    'bter':  {'ticker_url': 'https://bter.com/api/1/ticker/btc_cny',
                                    },
                    'goxbtc':  {'ticker_url': 'https://goxbtc.com/api/btc_cny/ticker.htm',
                                    },
                    'okcoin':  {'ticker_url': 'https://www.okcoin.com/api/ticker.do',
                                    },
                    'mercado':  {'ticker_url': 'https://www.mercadobitcoin.com.br/api/ticker/',
                                 'bitcoincharts_symbols': {'BRL': 'mrcdBRL',
                                                           },
                                    },
                    'bitx':  {'ticker_url': 'https://bitx.co.za/api/1/BTCZAR/ticker',
                                    },
                    'btctrade':  {'ticker_url': 'http://www.btctrade.com/api/ticker',
                                     },
                    'justcoin':  {'ticker_url': 'https://justcoin.com/api/v1/markets',
                                    },
                    'kraken':  {'ticker_url': 'https://api.kraken.com/0/public/Ticker?pair=BTCEUR',
                                    },
                    'bitkonan': {'ticker_url': 'https://bitkonan.com/api/ticker',
                                 'bitcoincharts_symbols': {'USD': 'bitkonanUSD',
                                                           },
                                 },
                    'bittylicious': {'ticker_url': 'https://bittylicious.com/api/v1/ticker',
                                 },
                    # 'ibwt': {'ticker_url': 'https://ibwt.co.uk/API/trades',
                    #              },




                    'campbx': {'bitcoincharts_symbols': {'USD': 'cbxUSD'},
                                 },

                    'cavirtex': {'bitcoincharts_symbols': {'CAD': 'virtexCAD',
                                                           },
                                 },
                    'bitbox': {'bitcoincharts_symbols': {'USD': 'bitboxUSD',
                                                         },
                                 },
                    'bitcoin_de': {'bitcoincharts_symbols':  {'EUR': 'btcdeEUR',
                                                             },
                                 },
                    'fbtc': {'bitcoincharts_symbols':  {'EUR': 'fbtcEUR',
                                                        'USD': 'fbtcUSD',
                                                           },
                                 },
                    'icbit': {'bitcoincharts_symbols': {'USD': 'icbitUSD',
                                                           },
                                 },
                    'weex':  {'bitcoincharts_symbols': {'AUD': 'weexAUD',
                                                        #'CAD': 'weexCAD',
                                                        # 'USD': 'weexUSD',
                                                           },
                                 },
                    'bitnz':  {'bitcoincharts_symbols': {'NZD': 'bitnzNZD',
                                                           },
                                 },
                    'fybse':  {'bitcoincharts_symbols': {'SEK': 'fybseSEK',
                                                           },
                                 },
                    'fybsg':  {'bitcoincharts_symbols': {'SGD': 'fybsgSGD'
                                                           },
                                 },
                }
