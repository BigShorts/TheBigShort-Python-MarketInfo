from index_and_exchange_cache import *
import sqlite3
import datetime
import os

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
supported_index_dict = {"SP500": ["NASDAQ", 1], "DOW": ["NASDAQ", 5], "NIFTY50": ["NSE", 7], "FTSE100": ["LSE", 1],
                        "FTSE250": ["LSE", 1]}
supported_index_list = [supported_index_dict[index][0]+"_"+index for index in supported_index_dict.keys()]

# loop to create the index tables
[create_index_table(index) for index in supported_index_list]


# price_target average, growth_estimate in %, action_suggest is buy/hold/sell as a float,
# valuation is under or overweight as a float.
# todo build this
def create_exchange_table(exchange_name):
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS {exchange_name} (ticker TEXT PRIMARY KEY, company_name TEXT, "
                      f"refresh_time TEXT, profile_data TEXT, price_target FLOAT, growth_estimate FLOAT, "
                      f"action_suggest FLOAT, valuation FLOAT, UNIQUE(ticker))")


# list of supported exchanges
supported_exchange_list = ["NASDAQ", "NYSE", "LSE"]

# loop to create the exchange tables
[create_exchange_table(exchange) for exchange in supported_exchange_list]


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

    if index_name in supported_index_dict.keys():
        for name in supported_index_list:
            if index_name == name.split("_")[1]:
                index_full_name = name
                exchange = name.split("_")[0]
                break

        # check if the index needs to be refreshed by checking the refresh time
        refresh_time = _index_db.execute(f"SELECT refresh_time FROM refresh_times WHERE "
                                         f"index_name = '{index_full_name}'").fetchone()
        if refresh_time:
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                tickers = [str(index)[2:-3] for index in (_index_db.execute(f"SELECT tickers FROM {index_full_name}").fetchall())]
                names = _index_db.execute(f"SELECT company_names FROM {index_full_name}").fetchall()
                other_info = _index_db.execute(f"SELECT other_info FROM {index_full_name}").fetchall()
        else:
            refresh_days = supported_index_dict[index_name][1]
            tickers, names, other_info = get_index(index_name)
            tickers.sort(), names.sort(), other_info.sort()
            write_index(index_full_name, refresh_days, tickers, names, other_info)

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

