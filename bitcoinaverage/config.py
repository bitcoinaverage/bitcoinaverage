from decimal import Decimal
import bitcoinaverage.server

API_FILES = {'TICKER_PATH': 'ticker/',
             'EXCHANGES_PATH': 'exchanges/',
             'ALL_FILE': 'all',
             'IGNORED_FILE': 'ignored',
             }

API_REQUEST_HEADERS = {'User-Agent': 'bitcoinaverage.com query bot',
                       'Origin': 'bitcoinaverage.com'}


#seconds between calls to various exchanges APIs
API_QUERY_FREQUENCY = {'bitcoincharts': 900,
                       'mtgox': 20,
                       'bitstamp': 20,
                       'btce': 20,
                       'bitcurex': 20,
                       'vircurex': 20,
                       'bitbargain': 20,
                       'localbitcoins': 20,
                       'cryptotrade': 20,
                       'rocktrading': 20,
                       'bitcash': 20,
                       'intersango': 20,
                       'bit2c': 20,
                       'kapiton': 20,
                       'rmbtb': 20,
                       'default': 15,
}

if hasattr(bitcoinaverage.server, 'DEFAULT_API_QUERY_FREQUENCY_OVERRIDE'):
    API_QUERY_FREQUENCY['default'] = bitcoinaverage.server.DEFAULT_API_QUERY_FREQUENCY_OVERRIDE

#seconds before a consequently failing API will be put into ignored list
#(before that data will be taken from cache)
API_IGNORE_TIMEOUT = 60
FRONTEND_QUERY_FREQUENCY = 5000 #milliseconds between AJAX requests from frontend to our API

DEC_PLACES = Decimal('0.00')

CURRENCY_LIST = ('USD',
                 'CNY',
                 'EUR',
                 'GBP',
                 'JPY',
                 'CAD',
                 'PLN',
                 'RUB',
                 'AUD',
                 'SEK',
                 'BRL',
                 'CZK',
                 'NZD',
                 'SGD',
                 # 'DKK',
                 # 'ILS',
                 # 'CHF',
                 # 'HKD',
                 # 'THB',
                    )

CURRENCY_LIST_NOGOX = ('USD',
                       'EUR',
                       'GBP',
)

BITCOIN_CHARTS_API_URL = 'http://api.bitcoincharts.com/v1/markets.json'

EXCHANGE_LIST = {
                    'mtgox': {'usd_api_url': 'http://data.mtgox.com/api/2/BTCUSD/money/ticker',
                              'eur_api_url': 'http://data.mtgox.com/api/2/BTCEUR/money/ticker',
                              'gbp_api_url': 'http://data.mtgox.com/api/2/BTCGBP/money/ticker',
                              'cad_api_url': 'http://data.mtgox.com/api/2/BTCCAD/money/ticker',
                              'pln_api_url': 'http://data.mtgox.com/api/2/BTCPLN/money/ticker',
                              'rub_api_url': 'http://data.mtgox.com/api/2/BTCRUB/money/ticker',
                              'aud_api_url': 'http://data.mtgox.com/api/2/BTCAUD/money/ticker',
                              'chf_api_url': 'http://data.mtgox.com/api/2/BTCCHF/money/ticker',
                              'cny_api_url': 'http://data.mtgox.com/api/2/BTCCNY/money/ticker',
                              'dkk_api_url': 'http://data.mtgox.com/api/2/BTCDKK/money/ticker',
                              'hkd_api_url': 'http://data.mtgox.com/api/2/BTCHKD/money/ticker',
                              'jpy_api_url': 'http://data.mtgox.com/api/2/BTCJPY/money/ticker',
                              'nzd_api_url': 'http://data.mtgox.com/api/2/BTCNZD/money/ticker',
                              'sgd_api_url': 'http://data.mtgox.com/api/2/BTCSGD/money/ticker',
                                  },
                    'bitstamp': {'api_url': 'https://www.bitstamp.net/api/ticker/',
                                   },
                    'btce': {'usd_api_url': 'https://btc-e.com/api/2/btc_usd/ticker',
                             'eur_api_url': 'https://btc-e.com/api/2/btc_eur/ticker',
                             'rur_api_url': 'https://btc-e.com/api/2/btc_rur/ticker',
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
                                         },

                    'cryptotrade':{'usd_api_url': 'https://crypto-trade.com/api/1/ticker/btc_usd',
                                   'eur_api_url': 'https://crypto-trade.com/api/1/ticker/btc_eur',
                                   },
                    'rocktrading':{'usd_ticker_url': 'https://www.therocktrading.com/api/ticker/BTCUSD',
                                   'usd_trades_url': 'https://www.therocktrading.com/api/trades/BTCUSD',
                                   'eur_ticker_url': 'https://www.therocktrading.com/api/ticker/BTCEUR',
                                   'eur_trades_url': 'https://www.therocktrading.com/api/trades/BTCEUR',
                                    },

                    'bitcash': {'czk_api_url': 'https://bitcash.cz/market/api/BTCCZK/ticker.json',
                                  },
                    #with intersango only EUR is used, because trader needs to convert to EUR to add/withdraw with it
                    'intersango': {'ticker_url': 'https://intersango.com/api/ticker.php',
                                   },

                    'bit2c': {'ticker_url' : 'https://www.bit2c.co.il/Exchanges/NIS/Ticker.json',
                              'orders_url' : 'https://www.bit2c.co.il/Exchanges/NIS/orderbook.json',
                              'trades_url' : 'https://www.bit2c.co.il/Exchanges/NIS/trades.json',
                                },
                    'kapiton': {'ticker_url': 'https://kapiton.se/api/0/ticker',
                                },

                    'rmbtb': {'ticker_url': 'https://www.rmbtb.com/api/secure/BTCCNY/ticker',
                                },





                    'campbx': {'bitcoincharts_symbols': {'USD': 'cbxUSD'},
                                 },

                    'cavirtex': {'bitcoincharts_symbols': {'CAD': 'virtexCAD',
                                                           },
                                 },
                    'bitbox': {'bitcoincharts_symbols': {'USD': 'bitboxUSD',
                                                         },
                                 },
                    'bitkonan': {'bitcoincharts_symbols': {'USD': 'bitkonanUSD',
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
                                                        'CAD': 'weexCAD',
                                                        'USD': 'weexUSD',
                                                           },
                                 },
                    'mercado':  {'bitcoincharts_symbols': {'BRL': 'mrcdBRL',
                                                           },
                                 },
                    'btcchina':  {'bitcoincharts_symbols': {'CNY': 'btcnCNY',
                                                           },
                                 },
                    'bitnz':  {'bitcoincharts_symbols': {'NZD': 'bitNZD',
                                                           },
                                 },
                    'fybse':  {'bitcoincharts_symbols': {'SEK': 'fybseSEK',
                                                           },
                                 },
                    'fybsg':  {'bitcoincharts_symbols': {'SGD': 'fybsgSGD'
                                                           },
                                 },

                }
