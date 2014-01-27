from decimal import Decimal
import time

import bitcoinaverage.server

INDEX_DOCUMENT_NAME = 'default' #directory index document name, needs to match webserver setting
CURRENCY_DUMMY_PAGES_SUBFOLDER_NAME = 'currencies'
CHARTS_DUMMY_PAGES_SUBFOLDER_NAME = 'charts'

FRONTEND_LEGEND_SLOTS = 20
FRONTEND_MAJOR_CURRENCIES = 5
FRONTEND_SCALE_DIVIZER = 1000 #millibits
FRONTEND_PRECISION = 3 #digits after dot

API_FILES = {'TICKER_PATH': 'ticker/',
             'GLOBAL_TICKER_PATH': 'ticker/global/',
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
FIAT_RATES_QUERY_FREQUENCY = 3600 #seconds between requests for fiat exchange rates, must be not less than an hour,
                                  # as total API queries amount limited at 1000/month
API_CALL_TIMEOUT_THRESHOLD = 15 #seconds before exchange API call timeout. exchange may have multiple calls
                                #and total time spent querying one exchange will be threshold * number of calls

#seconds between calls to various exchanges APIs
API_QUERY_FREQUENCY = { 'default': 60,
                        'bitcoincharts': 900,
                        }


if hasattr(bitcoinaverage.server, 'DEFAULT_API_QUERY_FREQUENCY_OVERRIDE'):
    API_QUERY_FREQUENCY['default'] = bitcoinaverage.server.DEFAULT_API_QUERY_FREQUENCY_OVERRIDE

#seconds before a consequently failing API will be put into ignored list (in the mean time data will be taken from cache)
API_IGNORE_TIMEOUT = 1800

DEC_PLACES = Decimal('0.00')

CURRENCY_LIST = ('USD',
                 'EUR',
                 'CNY',
                 'GBP',
                 'CAD',
                 'PLN',
                 'JPY',
                 'RUB',
                 'AUD',
                 'SEK',
                 'BRL',
                 # 'CZK',
                 'NZD',
                 'SGD',
                 'ZAR',
                 'NOK',
                 'ILS',
                 'CHF',
                 'TRY',
                 # 'DKK',
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
                              'display_name': 'MtGox',
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
                                 'display_name': 'Bitstamp',
                                 'bitcoincharts_symbols': {'USD': 'bitstampUSD',
                                                           },
                                   },
                    'btce': {'usd_api_url': 'https://btc-e.com/api/2/btc_usd/ticker',
                             'eur_api_url': 'https://btc-e.com/api/2/btc_eur/ticker',
                             'rur_api_url': 'https://btc-e.com/api/2/btc_rur/ticker',
                                 'display_name': 'BTC-e',
                                 'bitcoincharts_symbols': {'USD': 'btceUSD',
                                                           },
                                 },
                    'bitcurex': { 'eur_ticker_url': 'https://eur.bitcurex.com/data/ticker.json',
                                  'eur_trades_url': 'https://eur.bitcurex.com/data/trades.json',
                                  'pln_ticker_url': 'https://pln.bitcurex.com/data/ticker.json',
                                  'pln_trades_url': 'https://pln.bitcurex.com/data/trades.json',
                                  'display_name': 'Bitcurex',
                                    },
                    'vircurex': { 'usd_api_url': 'https://vircurex.com/api/get_info_for_1_currency.json?base=BTC&alt=USD',
                                  'eur_api_url': 'https://vircurex.com/api/get_info_for_1_currency.json?base=BTC&alt=EUR',
                                  'display_name': 'Vircurex',
                                    },

                    'bitbargain': {'volume_api_url': 'https://bitbargain.co.uk/api/bbticker',
                                   'ticker_api_url': 'https://bitbargain.co.uk/api/btcavg',
                                   'display_name': 'BitBargain',
                                   },

                    'localbitcoins': {'api_url': 'https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/',
                                      'display_name': 'LocalBitcoins',
                                         },

                    'cryptotrade':{'usd_api_url': 'https://crypto-trade.com/api/1/ticker/btc_usd',
                                   'display_name': 'Crypto-Trade',
                                   'bitcoincharts_symbols': {'USD': 'crytrUSD',
                                                                },
                                   },
                    'rocktrading':{'usd_ticker_url': 'https://www.therocktrading.com/api/ticker/BTCUSD',
                                   'usd_trades_url': 'https://www.therocktrading.com/api/trades/BTCUSD',
                                   'eur_ticker_url': 'https://www.therocktrading.com/api/ticker/BTCEUR',
                                   'eur_trades_url': 'https://www.therocktrading.com/api/trades/BTCEUR',
                                   'display_name': 'Rock Trading',
                                    },

                    # 'bitcash': {'czk_api_url': 'https://bitcash.cz/market/api/BTCCZK/ticker.json',
                    #             'bitcoincharts_symbols': {'CZK': 'bitcashCZK',
                    #                                        },
                    #               },

                    #with intersango only EUR is used, because trader needs to convert to EUR to add/withdraw with it
                    'intersango': {'ticker_url': 'https://intersango.com/api/ticker.php',
                                   'display_name': 'Intersango',
                                   },

                    'bit2c': {'ticker_url' : 'https://www.bit2c.co.il/Exchanges/BtcNis/Ticker.json',
                              'display_name': 'Bit2C',
                                },
                    'kapiton': {'ticker_url': 'https://kapiton.se/api/0/ticker',
                                'display_name': 'Kapiton',
                                },

                    'rmbtb': {'ticker_url': 'https://www.rmbtb.com/api/thirdparty/ticker/',
                              'display_name': 'RMBTB',
                                },

                    'btcchina':  {'ticker_url': 'https://data.btcchina.com/data/ticker',
                                  'display_name': 'BTC China',
                                    },
                    'fxbtc':  {'ticker_url': 'https://data.fxbtc.com/api?op=query_ticker&symbol=btc_cny',
                               'trades_url_template': 'https://data.fxbtc.com/api?op=query_history_trades&symbol=btc_cny&since={timestamp_sec}000000', #zeroes for millisec
                               'display_name': 'FXBTC',
                                    },
                    'bter':  {'ticker_url': 'https://bter.com/api/1/ticker/btc_cny',
                              'display_name': 'Bter',
                                    },
                    'goxbtc':  {'ticker_url': 'https://goxbtc.com/api/btc_cny/ticker.htm',
                                'display_name': 'GoXBTC',
                                    },
                    'mercado':  {'ticker_url': 'https://www.mercadobitcoin.com.br/api/ticker/',
                                 'display_name': 'Mercado Bitcoin',
                                 'bitcoincharts_symbols': {'BRL': 'mrcdBRL',
                                                           },
                                    },
                    'bitx':  {'ticker_url': 'https://bitx.co.za/api/1/BTCZAR/ticker',
                              'display_name': 'BitX',
                                  },
                    'justcoin':  {'ticker_url': 'https://justcoin.com/api/v1/markets',
                                  'display_name': 'Justcoin',
                                    },
                    'kraken':  {'usd_ticker_url': 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD',
                                'eur_ticker_url': 'https://api.kraken.com/0/public/Ticker?pair=XBTEUR',
                                'display_name': 'Kraken',
                                    },
                    'bitkonan': {'ticker_url': 'https://bitkonan.com/api/ticker',
                                 'display_name': 'BitKonan',
                                 'bitcoincharts_symbols': {'USD': 'bitkonanUSD',
                                                           },
                                 },
                    'bittylicious': {'ticker_url': 'https://bittylicious.com/api/v1/ticker',
                                     'display_name': 'Bittylicious',
                                     },
                    'bitxf': {'ticker_url': 'https://bitxf.com/api/v0/CNY/ticker.json',
                              'display_name': 'BitXF',
                                 },
                    'cavirtex': {'ticker_url': 'https://www.cavirtex.com/api/CAD/ticker.json',
                                 'orderbook_url': 'https://www.cavirtex.com/api/CAD/orderbook.json',
                                 'display_name': 'VirtEx',
                                 'bitcoincharts_symbols': {'CAD': 'virtexCAD',
                                                           },
                                 },
                    'bitfinex': {'ticker_url': 'https://api.bitfinex.com/v1/ticker/btcusd',
                                 'trades_url': 'https://api.bitfinex.com/v1/trades/btcusd?limit_trades=9999', # limit_trades might need increase if daily trading will go above it
                                 'display_name': 'Bitfinex',
                                 },
                    'fybsg': {'ticker_url': 'https://www.fybsg.com/api/SGD/ticker.json',
                              'trades_url': 'https://www.fybsg.com/api/SGD/trades.json', # this URL queries all trades for this exchange since beginning of time, this is not effective, ideally they should allow API to query by date.
                              'display_name': 'FYB-SG',
                              'bitcoincharts_symbols': {'SGD': 'fybsgSGD'
                                                           },
                                },
                    'fybse':  {'ticker_url': 'https://www.fybse.se/api/SEK/ticker.json',
                               'trades_url': 'https://www.fybse.se/api/SEK/trades.json', # this URL queries all trades for this exchange since beginning of time, this is not effective, ideally they should allow API to query by date.
                               'display_name': 'FYB-SE',
                               'bitcoincharts_symbols': {'SEK': 'fybseSEK',
                                                           },
                                 },
                    'bitcoin_de': {'rates_url': 'https://bitcoinapi.de/v1/{api_key}/rate.json',
                                   'trades_url': 'https://bitcoinapi.de/v1/{api_key}/trades.json',
                                   'display_name': 'Bitcoin.de',
                                 },
                    'bitcoin_central': {'ticker_url': 'https://bitcoin-central.net/api/data/eur/ticker',
                                        'depth_url': 'https://bitcoin-central.net/api/data/eur/depth',
                                        'display_name': 'Bitcoin Central',
                                         },
                    'btcturk': {'ticker_url': 'https://www.btcturk.com/api/ticker',
                                'display_name': 'BTCTurk',
                                         },
                    'bitonic': {'ticker_url': 'https://bitonic.nl/api/price',
                                'display_name': 'Bitonic',
                                         },
                    'itbit':  { 'usd_orders_url': 'https://www.itbit.com/api/v2/markets/XBTUSD/orders',
                                'usd_trades_url': 'https://www.itbit.com/api/v2/markets/XBTUSD/trades?since=0',
                                'sgd_orders_url': 'https://www.itbit.com/api/v2/markets/XBTSGD/orders',
                                'sgd_trades_url': 'https://www.itbit.com/api/v2/markets/XBTSGD/trades?since=0',
                                'eur_orders_url': 'https://www.itbit.com/api/v2/markets/XBTEUR/orders',
                                'eur_trades_url': 'https://www.itbit.com/api/v2/markets/XBTEUR/trades?since=0',
                                'display_name': 'itBit',
                                 },

                    'vaultofsatoshi':  {'usd_ticker_url': 'https://api.vaultofsatoshi.com/public/ticker?order_currency=BTC&payment_currency=USD',
                                        'eur_ticker_url': 'https://api.vaultofsatoshi.com/public/ticker?order_currency=BTC&payment_currency=EUR',
                                        'display_name': 'Vault of Satoshi',
                                        },

                    'quickbitcoin':  {'gbp_ticker_url': 'https://quickbitcoin.co.uk/ticker',
                                      'display_name': 'QuickBitcoin',
                                        },




                    # ignored until bitcoincharts.com will sort out their internal issues
                    'campbx': {'bitcoincharts_symbols': {'USD': 'cbxUSD',
                                                            },
                               'display_name': 'CampBX',
                                 },

                    'btcmarkets': {'bitcoincharts_symbols': {'AUD': 'btcmarketsAUD',
                                                                },
                                   'display_name': 'BTC Markets',
                                    },

                    'bitnz':  {'bitcoincharts_symbols': {'NZD': 'bitnzNZD',
                                                           },
                               'display_name': 'bitNZ',
                                 },

                    'anx_hk':  {'bitcoincharts_symbols': {'USD': 'anxhkUSD',
                                                          'HKD': 'anxhkHKD',
                                                          'CNY': 'anxhkCNY',
                                                           },
                                'display_name': 'ANX.HK',
                                 },
                    'weex':  {'bitcoincharts_symbols': {'AUD': 'weexAUD',
                                                        #'CAD': 'weexCAD',
                                                        #'USD': 'weexUSD',
                                                           },
                              'display_name': 'Weex',
                                 },




                    'okcoin':  {'ticker_url': 'https://www.okcoin.com/api/ticker.do',
                                'display_name': 'OKCoin',
                                'ignored': True,
                                'ignore_reason': 'volume data suspected to be fake',
                                },
                    'btctrade':  {'ticker_url': 'http://www.btctrade.com/api/ticker',
                                  'display_name': 'btctrade',
                                  'ignored': True,
                                  'ignore_reason': 'volume data suspected to be fake',
                                   },
                    'coinmkt':  {'display_name': 'CoinMKT',
                                 'ignored': True,
                                 'ignore_reason': 'no API available',
                                 },
                    'coinbase':  {'display_name': 'Coinbase',
                                  'ignored': True,
                                  'ignore_reason': 'volume data not published',
                                  },

                    ### not integrated
                    # CNY - btc100.org
                    # CNY - chbtc.com
                    # CNY - huobi.com
                    # CNY - 42BTC.com



                    # these exchanges seem to be dead
                    #'bitbox': {'bitcoincharts_symbols': {'USD': 'bitboxUSD',
                    #                                      },
                    #              },
                    #'fbtc': {'bitcoincharts_symbols':  {'EUR': 'fbtcEUR',
                    #                                    'USD': 'fbtcUSD',
                    #                                       },
                    #             },
                    #'icbit': {'bitcoincharts_symbols': {'USD': 'icbitUSD',
                    #                                       },
                    #             },


                }



