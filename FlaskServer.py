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
        {"name": "Day events (screeners)", "description": "Changes to stocks over a specific day"},
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
        "/indexes/{exchange}": {
            "get": {
                "tags": ["Market info"],
                "summary": "Returns the indexes of a specific exchange",
                "deprecated": True,
                "parameters": [
                    {
                        "name": "exchange",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The name of the exchange to get the indexes from",
                        "enum": supported_exchange_list
                    }
                ],
                "responses": {"200": {"description": "Returns list of indexes"}}
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
                "tags": ["Day events (screeners)"],
                "summary": "Returns the most active stocks of the day in a specific market",
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
                "tags": ["Day events (screeners)"],
                "summary": "Returns the top gaining stocks of the day in a specific market",
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
                "tags": ["Day events (screeners)"],
                "summary": "Returns the top losing stocks of the day in a specific market",
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
                "tags": ["Day events (screeners)"],
                "summary": "Returns the trending stocks of the day",
                "responses": {"200": {"description": "Returns the trending stocks"}}
            }
        },
        "/day_etfs/": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the top ETFs of the day",
                "responses": {"200": {"description": "Returns the top ETFs"}}
            }
        },
        "/day_futures/{market}": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the futures latest data",
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get future data from",
                        "enum": ["us", "uk"]
                    }
                ],
                "responses": {"200": {"description": "Returns the latest futures data"}}
            }
        },
        "/day_world_indices": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the world indices latest data",
                "responses": {"200": {"description": "Returns the latest world indices data"}}
            }
        },
        "/day_forex_rates": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the latest forex rates of the day from GBP",
                "responses": {"200": {"description": "Returns the latest forex rates"}}
            }
        },
        "/day_us_bonds": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the US treasury bonds latest data",
                "responses": {"200": {"description": "Returns the latest US treasury bond data"}}
            }
        },
        "/day_crypto/{amount}": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the top cryptocurrencies of the day",
                "parameters": [
                    {
                        "name": "amount",
                        "in": "path",
                        "type": "integer",
                        "required": True,
                        "description": "The amount of cryptocurrencies to return in hundreds",
                        "default": "3"
                    }
                ],
                "responses": {"200": {"description": "Returns the top cryptocurrencies"}}
            }
        },
        "/day_aggressive_small_caps/{sort_by}": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the aggressive small caps of the day",
                "parameters": [
                    {
                        "name": "sort_by",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "Method to sort the stocks by",
                        "enum": ["percent_change", "market_cap"]
                    }
                ],
                "responses": {"200": {"description": "Returns the aggressive small caps"}}
            }
        },
        "/portfolio_anchors/{sort_by}": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the portfolio anchors of the day",
                "parameters": [
                    {
                        "name": "sort_by",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "Method to sort the stocks by",
                        "enum": ["percent_change", "market_cap"]
                    }
                ],
                "responses": {"200": {"description": "Returns the portfolio anchors"}}
            }
        },
        "/undervalued_growth/{sort_by}": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the undervalued growth stocks of the day",
                "parameters": [
                    {
                        "name": "sort_by",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "Method to sort the stocks by",
                        "enum": ["percent_change", "market_cap"]
                    }
                ],
                "responses": {"200": {"description": "Returns the undervalued growth stocks"}}
            }
        },
        "/undervalued_large_caps/{sort_by}": {
            "get": {
                "tags": ["Day events (screeners)"],
                "summary": "Returns the undervalued large caps of the day",
                "parameters": [
                    {
                        "name": "sort_by",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "Method to sort the stocks by",
                        "enum": ["percent_change", "market_cap"]
                    }
                ],
                "responses": {"200": {"description": "Returns the undervalued large caps"}}
            }
        },
        "/earnings_for_date/{market}/{date}": {
            "get": {
                "tags": ["Market info"],
                "summary": "Returns the earnings for a specific date from a specific market",
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get earnings from",
                        "enum": ["us", "uk"]
                    },
                    {
                        "name": "date",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "The date to get earnings from",
                        "default": "2024-05-17"
                    }
                ],
                "responses": {"200": {"description": "Returns the earnings for the date"}}
            }
        },
        "/earnings_in_date_range_us/{market}/{start_date}/{end_date}": {
            "get": {
                "tags": ["Market info"],
                "deprecated": True,
                "summary": "Returns the earnings for a date range from a specific market",
                "parameters": [
                    {
                        "name": "market",
                        "in": "path",
                        "type": "string", "required": True,
                        "description": "The market to get earnings from",
                        "enum": ["us", "uk"]
                    },
                    {
                        "name": "start_date",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "The start date of the earnings range",
                        "default": "2024-05-17"
                    },
                    {
                        "name": "end_date",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "The end date of the earnings range",
                        "default": "2024-05-17"
                    }
                ],
                "responses": {"200": {"description": "Returns the earnings for the date range"}}
            }
        },
    }
})


# app routing code below
@app.route('/')
def blank_page():
    return "This is a blank page, navigate to the API documentation at /apidocs"


@app.route('/index/<index_name>/<return_type>')
def get_index(index_name, return_type):
    print(index_name, return_type)
    return load_index(index_name, return_type)


# todo
@app.route('/indexes/<exchange>')
def get_indexes(exchange):
    return load_indexes(exchange)


@app.route('/exchange/<exchange>/<return_type>')
def get_exchange(exchange, return_type):
    return load_exchange(exchange, return_type)


# called when profile needs force update
@app.route('/profile/<ticker>')
def profile(ticker):
    return f"Profile for {ticker}"


# below flask routes rely on the day_stock_info.py functions

@app.route('/most_active/<market>/<sort_by>')
def most_active(market, sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    if market == "us":
        return raw_daily_info("us", "/most-active", multiple_pages=True, sort_by_element=element)
    elif market == "uk":
        return raw_daily_info("uk", f"/most-active", multiple_pages=True, sort_by_element=element)
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_gainers/<market>/<sort_by>')
def day_gainers(market, sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    if market == "us":
        return raw_daily_info("us", "/gainers", multiple_pages=True, sort_by_element=element)
    elif market == "uk":
        return raw_daily_info("uk", "/gainers", multiple_pages=True, sort_by_element=element)
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_losers/<market>')
def day_losers(market):
    if market == "us":
        return raw_daily_info("us", "/losers", multiple_pages=True)
    elif market == "uk":
        return raw_daily_info("uk", "/losers", multiple_pages=True)
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_trending_tickers')
def day_trending_tickers():
    return raw_daily_info("us", "/trending-tickers", skip=2)


@app.route('/day_etfs/')
def day_etfs():
    return raw_daily_info("us", "/etfs", multiple_pages=True)


@app.route('/day_futures/<market>')
def day_futures(market):
    if market == "us":
        result_table = table_to_dict(pandas.read_html(requests.get(f"{urlUS}/commodities",
                                                      headers=default_headers).text)[0], skip=1)
        return [str(value)[2:-3] for key, value in result_table.items()]
    elif market == "uk":
        result_table = table_to_dict(pandas.read_html(requests.get(f"{urlUK}/commodities",
                                                      headers=default_headers).text)[0], skip=1)
        return [str(value)[2:-3] for key, value in result_table.items()]
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/day_world_indices/')
def day_world_indices():
    return raw_daily_info("us", "/world-indices", skip=2)


@app.route('/day_forex_rates')
def day_forex_rates():
    return raw_daily_info("uk", "/currencies", skip=1)


@app.route('/day_us_bonds')
def day_us_bonds():
    return raw_daily_info("us", "/bonds", skip=1)


@app.route('/day_crypto/<amount>')
def day_crypto(amount):
    return raw_daily_info("us", "/crypto", multiple_pages=True, page_limit=int(amount), skip=1)


@app.route('/day_aggressive_small_caps/<sort_by>')
def day_aggressive_small_caps(sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    return raw_daily_info("us", "screener/predefined/aggressive_small_caps",
                          multiple_pages=True, sort_by_element=element)


@app.route('/portfolio_anchors/<sort_by>')
def portfolio_anchors(sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    return raw_daily_info("us", "screener/predefined/portfolio_anchors",
                          multiple_pages=True, sort_by_element=element)


@app.route('/undervalued_growth/<sort_by>')
def undervalued_growth(sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    return raw_daily_info("us", "screener/predefined/undervalued_growth_stocks",
                          multiple_pages=True, sort_by_element=element)


@app.route('/undervalued_large_caps/<sort_by>')
def undervalued_large_caps(sort_by):
    if sort_by == "percent_change":
        element = 4
    else:
        element = 7
    return raw_daily_info("us", "screener/predefined/undervalued_large_caps",
                          multiple_pages=True, sort_by_element=element)


@app.route('/earnings_for_date/<market>/<date>')
def earnings_for_date(market, date):
    if market == "us":
        return earnings_for_date_us(date)
    elif market == "uk":
        return earnings_for_date_uk(date)
    else:
        return "Market not found, available markets are 'us' and 'uk'"


@app.route('/earnings_in_date_range_us/<market>/<start_date>/<end_date>')
def earnings_in_date_range_us(market, start_date, end_date):
    if market == "us":
        return earnings_in_date_range_us(start_date, end_date)
    elif market == "uk":
        return earnings_in_date_range_uk(start_date, end_date)
