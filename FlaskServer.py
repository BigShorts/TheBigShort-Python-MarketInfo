from flask import Flask
import index_and_exchange_cache as iec
import sqlite3
import datetime
import os

app = Flask(__name__)

# below is loader code

# create the directory for the ticker data if it does not exist
if not os.path.exists("TickerData"):
    os.mkdir("TickerData")

# connect to the ticker database
_ticker_db = sqlite3.connect("TickerData/ticker.db", check_same_thread=False)
_ticker_db.execute("CREATE TABLE IF NOT EXISTS profile (ticker TEXT PRIMARY KEY, refresh_time TEXT, profile_data TEXT,"
                   " UNIQUE(ticker))")

# connect to the index database
_index_db = sqlite3.connect("TickerData/indexes.db", check_same_thread=False)


# code to create the index tables
def create_index_table(index_name):
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS {index_name} (tickers TEXT PRIMARY KEY, company_names TEXT, "
                      f"other_info TEXT)")
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS refresh_times (index_name TEXT PRIMARY KEY, refresh_time TEXT)")


# list of supported indexes, can be expanded
# format: exchange-index_name: [exchange, refresh_days, (tickers, names, other_info)]
supported_index_list = ["SP500", "DOW", "NIFTY50", "FTSE100", "FTSE250"]
# todo not call the functions on every load
supported_index_dict = {"NASDAQ_SP500": [1, iec.get_sp500()], "NASDAQ_DOW": [5, iec.get_dow()],
                        "NSE_NIFTY50": [7, iec.get_nifty50()], "LSE_FTSE100": [1, iec.get_ftse100()],
                        "LSE_FTSE250": [1, iec.get_ftse250()]}

# loop to create the index tables
for index in supported_index_dict.keys():
    create_index_table(index)


def write_index(index_name, refresh_days, tickers, names, other_info):
    for i in range(len(tickers)):
        _index_db.execute(f"INSERT OR REPLACE INTO {index_name} (tickers, company_names, other_info) "
                          f"VALUES (?, ?, ?)",(tickers[i], names[i], other_info[i]))
    _index_db.execute(f"INSERT OR REPLACE INTO refresh_times (index_name, refresh_time) VALUES (?, ?)",
                      (index_name, datetime.datetime.now() + datetime.timedelta(days=refresh_days)))
    _index_db.commit()


def load_index(index_name, return_type="tickers"):
    if index_name == "S&P500":
        index_name = "SP500"

    if index_name in supported_index_list:
        for name in supported_index_dict.keys():
            print(index_name, name)
            if index_name == name.split("_")[1]:
                index_name = name
                exchange = name.split("_")[0]

        try:
            # check if the index needs to be refreshed by checking the refresh time
            refresh_time = _index_db.execute(f"SELECT refresh_time FROM refresh_times WHERE index_name = '{index_name}'").fetchone()
            if datetime.datetime.now() > datetime.datetime.strptime(refresh_time, "%Y-%m-%d %H:%M:%S.%f"):
                tickers = None
            else:
                tickers, names, other_info = (_index_db.execute(f"SELECT * FROM {index_name}").fetchone())
        except TypeError:
            tickers = None

        if tickers is None:
            refresh_days = supported_index_dict[index_name][0]
            tickers, names, other_info = supported_index_dict[index_name][1]
            write_index(index_name, refresh_days, tickers, names, other_info)

        if return_type == "tickers":
            return tickers
        elif return_type == "names":
            return names
        elif return_type == "other_info":
            return other_info
        elif return_type == "all":
            return exchange+"\n"+tickers+"\n"+names+"\n"+other_info
    else:
        return "Index not found"


# check for index refreshes
for index in supported_index_list:
    load_index(index)


def load_indexes(exchange):
    if exchange == "nasdaq":
        # check if nasdaq is in the database
        cursor = _index_db.execute("SELECT  FROM profile WHERE exchange = 'nasdaq'")

    return "ticker_info"


# app routing code below
@app.route('/')
def test():
    return "Hello World!"


@app.route('/index/<index_name>/<return_type>')
def get_index(index_name, return_type="tickers"):
    return load_index(index_name, return_type)


@app.route('/indexes/<exchange>')
def get_indexes(exchange):
    return load_indexes(exchange)


# called when profile needs force update
@app.route('/profile/<ticker>')
def profile(ticker):
    return f"Profile for {ticker}"


@app.route('/trigger')
def trigger():
    return iec.tickers_nasdaq()

