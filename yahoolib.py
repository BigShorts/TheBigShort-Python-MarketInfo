from index_and_exchange_cache import *
import sqlite3
import datetime
import os

# below is loader code

# create the directory for the ticker data if it does not exist
if not os.path.exists("TickerData"):
    os.mkdir("TickerData")

# connect to the index database
_index_db = sqlite3.connect("TickerData/indexes.db", check_same_thread=False)


# code to create the index tables
def create_index_table(index_name):
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS {index_name} (ticker TEXT PRIMARY KEY, company_name TEXT, "
                      f"other_info TEXT)")
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS idx_refresh_times (index_name TEXT PRIMARY KEY, refresh_time TEXT)")


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
                      f"other_info TEXT, refresh_time TEXT, profile_data TEXT, price_target FLOAT, "
                      f"growth_estimate FLOAT, action_suggest FLOAT, valuation FLOAT, UNIQUE(ticker))")
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS exc_refresh_times (exchange_name TEXT PRIMARY KEY, refresh_time TEXT)")


# list of supported exchanges
supported_exchange_list = ["NASDAQ", "NASDAQ_OTHER", "NYSE", "LSE"]#, "LSE_NON_EQ"]

# loop to create the exchange tables
[create_exchange_table(exchange) for exchange in supported_exchange_list]


def write_index(index_name, refresh_days, tickers, names, other_info):
    for i in range(len(tickers)):
        _index_db.execute(f"INSERT OR REPLACE INTO {index_name} (ticker, company_name, other_info) "
                          f"VALUES (?, ?, ?)", (tickers[i], names[i], other_info[i]))
    _index_db.execute(f"INSERT OR REPLACE INTO idx_refresh_times (index_name, refresh_time) VALUES (?, ?)",
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
        refresh_time = _index_db.execute(f"SELECT refresh_time FROM idx_refresh_times WHERE "
                                         f"index_name = '{index_full_name}'").fetchone()
        tickers = None
        if refresh_time:
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                tickers = [str(index)[2:-3] for index in (_index_db.execute(f"SELECT ticker FROM {index_full_name}").fetchall())]
                names = [str(name)[2:-3] for name in _index_db.execute(f"SELECT company_name FROM {index_full_name}").fetchall()]
                other_info = [str(info)[2:-3] for info in _index_db.execute(f"SELECT other_info FROM {index_full_name}").fetchall()]
        if not tickers:
            refresh_days = supported_index_dict[index_name][1]
            tickers, names, other_info = get_index(index_name)
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
for index in supported_index_dict.keys():
    load_index(index)


def write_exchange(exchange, refresh_days, tickers, company_names, other_info):
    for i in range(len(tickers)):
        _index_db.execute(f"INSERT OR REPLACE INTO {exchange} (ticker, company_name, other_info) VALUES (?, ?, ?)",
                          (tickers[i], company_names[i], other_info[i]))
    _index_db.execute(f"INSERT OR REPLACE INTO exc_refresh_times (exchange_name, refresh_time) VALUES (?, ?)",
                      (exchange, datetime.datetime.now() + datetime.timedelta(refresh_days)))
    _index_db.commit()


def load_exchange(exchange, return_type="tickers"):
    if exchange in supported_exchange_list:
        # check if the exchange needs to be refreshed by checking the refresh time
        refresh_time = _index_db.execute(f"SELECT refresh_time FROM exc_refresh_times WHERE "
                                         f"exchange_name = '{exchange}'").fetchone()
        tickers = None
        if refresh_time:
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                tickers = [str(index)[2:-3] for index in _index_db.execute(f"SELECT ticker FROM {exchange}").fetchall()]
                names = [str(name)[2:-3] for name in _index_db.execute(f"SELECT company_name FROM {exchange}").fetchall()]
                other_info = [str(info)[2:-3] for info in _index_db.execute(f"SELECT other_info FROM {exchange}").fetchall()]
        if not tickers:
            refresh_days = 3
            tickers, names, other_info = get_exchange(exchange)
            write_exchange(exchange, refresh_days, tickers, names, other_info)
        if return_type == "tickers":
            return tickers
        elif return_type == "names":
            return names
        elif return_type == "other_info":
            return str(tickers)+"\n"+str(other_info)
    else:
        return "Exchange not found"


# check for exchange refreshes
#for exchange in supported_exchange_list:
#    load_exchange(exchange)
load_exchange("NASDAQ")
load_exchange("NASDAQ_OTHER")
#load_exchange("LSE")


def load_indexes(exchange):
    if exchange == "nasdaq":
        # check if nasdaq is in the database
        cursor = _index_db.execute("SELECT  FROM profile WHERE exchange = 'nasdaq'")

    return "ticker_info"

