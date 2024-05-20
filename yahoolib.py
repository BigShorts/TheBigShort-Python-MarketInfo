from index_and_exchange_cache import *
import datetime
import os
import requests
import random
import yfinance
import sqlite3

# below is loader code for the index and exchange cache

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
def create_exchange_table(exchange_name):
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS {exchange_name} (ticker TEXT PRIMARY KEY, company_name TEXT, "
                      "other_info TEXT, refresh_time TEXT, address TEXT, trading_currency TEXT, industry TEXT, "
                      "sector TEXT, quote_type TEXT, business_summary TEXT, employees INT, company_officers TEXT, "
                      "dividend_yield FLOAT, dividend_date TIMESTAMP, trailing_PE FLOAT, forward_PE FLOAT, beta FLOAT, "
                      "market_cap FLOAT, enterprise_value FLOAT, total_debt FLOAT, average_volume FLOAT, "
                      "average_volume_10days FLOAT, profit_margin FLOAT, shares_outstanding FLOAT, shares_short FLOAT, "
                      "held_percent_insiders FLOAT, held_percent_institutions FLOAT, earnings_quarterly_growth FLOAT, "
                      "target_median_price FLOAT, target_mean_price FLOAT, recommendation TEXT, "
                      "return_on_assets FLOAT, return_on_equity FLOAT, operating_cash_flow FLOAT, "
                      "free_cash_flow FLOAT, gross_margins FLOAT, operating_margins FLOAT, profile_data TEXT, "
                      "recommendation_analysed INT, valuation FLOAT, UNIQUE(ticker))")
    _index_db.execute(f"CREATE TABLE IF NOT EXISTS exc_refresh_times (exchange_name TEXT PRIMARY KEY, refresh_time TEXT)")


# list of supported exchanges
supported_exchange_list = ["NASDAQ", "NASDAQ_OTHER", "LSE", "LSE_OTHER"]

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


def load_exchange(exchange, return_type="tickers", refresh_days=3):
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
for exchange in supported_exchange_list:
    load_exchange(exchange, refresh_days=31)


def get_profile(_exchange, _ticker):
    try:
        t_object = yfinance.Ticker(_ticker)
        t_info = t_object.info
    except requests.exceptions.HTTPError:
        print(f"Ticker {_ticker} profile failed to load: HTTPError")
        return {}
    r_day_add, r_hour_add = random.randint(0, 5), random.randint(0, 23)

    # the below keys are perceived as mostly live data (gained from get_ticker_data()), so excluded from the cache
    ex_keys = ["previousClose", "open", "dayLow", "dayHigh", "regularMarketPreviousClose", "regularMarketOpen",
               "regularMarketDayLow", "regularMarketDayHigh", "bid", "ask", "bidSize", "askSize", "symbol",
               "underlyingSymbol", "currentPrice", "longName", "exchange", "shortName", "sector", "sectorDisp",
               "industry", "industryDisp", "currency", ]

    def updator(keys, value_type=str):
        data_field = ""

        if len(keys) > 1:
            for key in keys:
                if key in t_info.keys():
                    data_field += f"{key}: {t_info[key]}§"
                    t_info.pop(key)
        elif keys[0] in t_info.keys():
            data_field = t_info[keys[0]]
            t_info.pop(keys[0])
        if data_field == "":
            if value_type == int:
                return 0
            else:
                return None
        else:
            if len(keys) > 1:
                return data_field[:-1]
            else:
                return data_field

    address = updator(["address1", "address2", "city", "state", "zip", "country", "phone", "website"])
    trading_currency = updator(["financialCurrency"])
    industry = updator(["industryKey"])
    sector = updator(["sectorKey"])
    quote_type = updator(["quoteType"])
    business_summary = updator(["longBusinessSummary"])
    employees = updator(["fullTimeEmployees"])
    company_officers = str(updator(["companyOfficers"]))
    dividend_yield = updator(["dividendYield"])
    dividend_date = updator(["exDividendDate"])
    trailing_PE = updator(["trailingPE"])
    forward_PE = updator(["forwardPE"])
    beta = updator(["beta"])
    market_cap = updator(["marketCap"])
    enterprise_value = updator(["enterpriseValue"])
    total_debt = updator(["totalDebt"])
    average_volume = updator(["averageVolume"])
    average_volume_10days = updator(["averageVolume10days"])
    profit_margin = updator(["profitMargins"])
    shares_outstanding = updator(["sharesOutstanding"])
    shares_short = updator(["sharesShort"])
    held_percent_insiders = updator(["heldPercentInsiders"])
    held_percent_institutions = updator(["heldPercentInstitutions"])
    earnings_quarterly_growth = updator(["earningsQuarterlyGrowth"])
    target_median_price = updator(["targetMedianPrice"])
    target_mean_price = updator(["targetMeanPrice"])
    recommendation = updator(["recommendationKey", "recommendationMean", "numberOfAnalystOpinions"])
    return_on_assets = updator(["returnOnAssets"])
    return_on_equity = updator(["returnOnEquity"])
    operating_cash_flow = updator(["operatingCashflow"])
    free_cash_flow = updator(["freeCashflow"])
    gross_margins = updator(["grossMargins"])
    operating_margins = updator(["operatingMargins"])

    profile_to_write = ""
    for _key in t_info.keys():
        if _key not in ex_keys:
            t_info[_key] = str(t_info[_key]).replace("\n", "")
            profile_to_write += f"{_key}§{t_info[_key]}\n"

    print(profile_to_write)

    # todo insert into DB.
    #company_name, other_info = _index_db.execute(f"SELECT company_name, other_info FROM {_exchange} "
    #                                             f"WHERE ticker = '{_ticker}'").fetchone()

    _index_db.execute(f"UPDATE {_exchange} SET refresh_time = '{datetime.datetime.now() + 
                        datetime.timedelta(days=r_day_add, hours=r_hour_add)}', address = '{address}', "
                      f"trading_currency = '{trading_currency}', industry = '{industry}', sector = '{sector}', "
                      f"quote_type = '{quote_type}', business_summary = '{business_summary}', "
                      f"employees = {employees} WHERE ticker = '{_ticker}'")
                      #f" company_officers = '{company_officers}' WHERE ticker = '{_ticker}'")
                      #f"dividend_yield = {dividend_yield}, dividend_date = '{dividend_date}', "
                      #f"trailing_PE = {trailing_PE}, forward_PE = {forward_PE}, beta = {beta}, "
                      #f"market_cap = {market_cap}, enterprise_value = {enterprise_value}, total_debt = {total_debt}, "
                      #f"average_volume = {average_volume}, average_volume_10days = {average_volume_10days}, "
                      #f"profit_margin = {profit_margin}, shares_outstanding = {shares_outstanding}, "
                      #f"shares_short = {shares_short}, held_percent_insiders = {held_percent_insiders}, "
                      #f"held_percent_institutions = {held_percent_institutions}, "
                      #f"earnings_quarterly_growth = {earnings_quarterly_growth}, "
                      #f"target_median_price = {target_median_price}, target_mean_price = {target_mean_price}, "
                      #f"recommendation = '{recommendation}', return_on_assets = {return_on_assets}, "
                      #f"return_on_equity = {return_on_equity}, operating_cash_flow = {operating_cash_flow}, "
                      #f"free_cash_flow = {free_cash_flow}, gross_margins = {gross_margins}, "
                      #f"operating_margins = {operating_margins}, profile_data = '{profile_to_write}' "
                      #f"WHERE ticker = '{_ticker}'")

    _index_db.commit()
                      

    input()


# check for profile refreshes # todo make max hourly check, threaded updates?
for exchange in supported_exchange_list:
    tickers = [str(index)[2:-3] for index in _index_db.execute(f"SELECT ticker FROM {exchange}").fetchall()]

    for ticker in tickers:
        # get refresh time
        refresh_time = _index_db.execute(f"SELECT refresh_time FROM {exchange} WHERE ticker = '{ticker}'").fetchone()

        scrape_profile = True
        if refresh_time != (None,):
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                print(f"Skipping {ticker} profile refresh")
                scrape_profile = False

        if scrape_profile:
            print(f"Refreshing {ticker} profile")
            profile_data = get_profile(exchange, ticker)




