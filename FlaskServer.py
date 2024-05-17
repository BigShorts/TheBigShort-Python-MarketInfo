from flask import Flask
from yahoolib import *
from day_stock_info import *
from flasgger import Swagger

# file for the Flask server code to run the "yahoolib.py" functions

app = Flask(__name__)
swagger = Swagger(app, template={
    "info": {
        "title": "Python tickerlib.py python API",
        "description": "Examples of how to use the projects python stock API",
        "version": "0.0.1"
    },
    # put the below into paths for "day changes" and "stock info"

    "tags": [
        {"name": "Day changer events", "description": "Changes to stocks over a specific day"},
        {"name": "Market info", "description": "Information on specific markets and/or indexes"},
        {"name": "Stock info", "description": "Information on a specific stock(s)"}
    ],


    "paths": {
        "/index/{index_name}/{return_type}": {
            "get": {
                "tags": ["Market info"],
                "parameters": [
                    {
                        "name": "index_name",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The name of the index to get",
                        "enum": list(supported_index_dict.keys())

                    },
                    {
                        "name": "return_type",
                        "in": "path", "type": "string",
                        "required": True,
                        "enum": ["tickers", "names", "other_info", "all"],
                    }
                ],
                "responses": {"200": {"description": "Returns the index data"}}
            }
        },
        "/exchange/{exchange}/{return_type}": {
            "get": {
                "tags": ["Market info"],
                "parameters": [
                    {
                        "name": "exchange",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The name of the exchange to get",
                        "enum": supported_exchange_list
                    },
                    {
                        "name": "return_type",
                        "in": "path", "type": "string",
                        "required": True,
                        "enum": ["tickers", "names", "other_info"],
                    }
                ],
                "responses": {"200": {"description": "Returns the exchange data"}}
            }
        },
        "/most_active/{market}/{sort_by}": {
            "get": {
                "tags": ["Day changer events"],
                "description": "Returns the most active stocks of the day in a specific market",
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get the most active stocks from",
                        "enum": ["us", "uk"]
                    },
                    {
                        "name": "sort_by",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "Method to sort the stocks by",
                        "enum": ["percent_change", "market_cap"]
                    }
                ],
                "responses": {"200": {"description": "Returns the most active stocks"}}
            }
        },
        "/day_gainers/{market}/{sort_by}": {
            "get": {
                "tags": ["Day changer events"],
                "description": "Returns the top gaining stocks of the day in a specific market",
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get the top gaining stocks from",
                        "enum": ["us", "uk"]
                    },
                    {
                        "name": "sort_by",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "Method to sort the stocks by",
                        "enum": ["percent_change", "market_cap"]
                    }
                ],
                "responses": {"200": {"description": "Returns the top gaining stocks"}}
            }
        },
        "/day_losers/{market}": {
            "get": {
                "tags": ["Day changer events"],
                "description": "Returns the top losing stocks of the day in a specific market",
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get the top losing stocks from",
                        "enum": ["us", "uk"]
                    }
                ],
                "responses": {"200": {"description": "Returns the top losing stocks"}}
            }
        },
        "/day_trending_tickers": {
            "get": {
                "tags": ["Day changer events"],
                "responses": {"200": {"description": "Returns the trending stocks"}}
            }
        },
        "/day_top_etfs/{market}": {
            "get": {
                "tags": ["Day changer events"],
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get the top ETFs from",
                        "enum": ["us", "uk"]
                    }
                ],
                "responses": {"200": {"description": "Returns the top ETFs"}}
            }
        },
        "/day_top_mutual/{market}": {
            "get": {
                "tags": ["Day changer events"],
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get the top mutual funds from",
                        "enum": ["us", "uk"]
                    }
                ],
                "responses": {"200": {"description": "Returns the top mutual funds"}}
            }
        },
        "/day_top_futures/{market}": {
            "get": {
                "tags": ["Day changer events"],
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get the top futures from",
                        "enum": ["us", "uk"]
                    }
                ],
                "responses": {"200": {"description": "Returns the top futures"}}
            }
        },
        "/day_highest_open_interest": {
            "get": {
                "tags": ["Day changer events"],
                "responses": {"200": {"description": "Returns the highest open interest stocks"}}
            }
        },
        "/day_top_world_indices": {
            "get": {
                "tags": ["Day changer events"],
                "responses": {"200": {"description": "Returns the top world indices"}}
            }
        },
        "/day_top_forex_rates": {
            "get": {
                "tags": ["Day changer events"],
                "responses": {"200": {"description": "Returns the top forex rates"}}
            }
        },
        "/day_top_us_bonds": {
            "get": {
                "tags": ["Day changer events"],
                "responses": {"200": {"description": "Returns the top US bonds"}}
            }
        },
        "/day_top_crypto": {
            "get": {
                "tags": ["Day changer events"],
                "responses": {"200": {"description": "Returns the top cryptocurrencies"}}
            }
        }
    }
})


# app routing code below
@app.route('/')
def test():
    return "Hello World!"


@app.route('/index/<index_name>/<return_type>')
def get_index(index_name, return_type):
    print(index_name, return_type)
    return load_index(index_name, return_type)


# todo
#@app.route('/indexes/<exchange>')
#def get_indexes(exchange):
#    return load_indexes(exchange)


@app.route('/exchange/<exchange>/<return_type>')
def get_exchange(exchange, return_type):
    return load_exchange(exchange, return_type)


# called when profile needs force update
@app.route('/profile/<ticker>')
def profile(ticker):
    return f"Profile for {ticker}"


# below flask routes rely on the day_stock_info.py functions
# todo rewrite out of that file into this one

_urlUS_ = "https://finance.yahoo.com"
_urlUK_ = "https://uk.finance.yahoo.com"
_urlDE_ = "https://de.finance.yahoo.com"  # todo add de (germany)


# todo sort by market cap or change
@app.route('/most_active/<market>/<sort_by>')
def most_active(market, sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    if market == "us":
        return raw_daily_info(f"{_urlUS_}/most-active", "us", multiple_pages=True, sort_by_element=element)
    elif market == "uk":
        return raw_daily_info(f"{_urlUK_}/most-active", "uk", multiple_pages=True, sort_by_element=element)
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_gainers/<market>/<sort_by>')
def day_gainers(market, sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    if market == "us":
        return raw_daily_info(f"{_urlUS_}/gainers", "us", multiple_pages=True, sort_by_element=element)
    elif market == "uk":
        return raw_daily_info(f"{_urlUK_}/gainers", "uk", multiple_pages=True, sort_by_element=element)
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_losers/<market>')
def day_losers(market):
    if market == "us":
        return day_losers_us()
    elif market == "uk":
        return day_losers_uk()
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_trending_tickers')
def day_trending_tickers():
    return day_trending_tickers()


@app.route('/day_top_etfs/<market>')
def day_top_etfs(market):
    if market == "us":
        return day_top_etfs_us()
    elif market == "uk":
        return day_top_etfs_uk()
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_top_mutual/<market>')
def day_top_mutual(market):
    if market == "us":
        return day_top_mutual_us()
    elif market == "uk":
        return day_top_mutual_uk()
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_top_futures/<market>')
def day_top_futures(market):
    if market == "us":
        return day_top_futures_us()
    elif market == "uk":
        return day_top_futures_uk()
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_highest_open_interest')
def day_highest_open_interest():
    return day_highest_open_interest()


@app.route('/day_top_world_indices/')
def day_top_world_indices():
    return day_top_world_indices()


@app.route('/day_top_forex_rates')
def day_top_forex_rates():
    return day_top_forex_rates()


@app.route('/day_top_us_bonds')
def day_top_us_bonds():
    return day_top_us_bonds()


@app.route('/day_top_crypto')
def day_top_crypto():
    return day_top_crypto()
