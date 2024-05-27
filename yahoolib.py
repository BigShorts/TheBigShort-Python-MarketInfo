from index_and_exchange_downloader import *
from day_stock_info import *
from settings import *
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
index_db = sqlite3.connect("TickerData/indexes.db", check_same_thread=False)


# code to create the index tables
def create_index_table(index_name):
    index_db.execute(f"CREATE TABLE IF NOT EXISTS {index_name} (ticker TEXT PRIMARY KEY, company_name TEXT, "
                     f"other_info TEXT)")
    index_db.execute(f"CREATE TABLE IF NOT EXISTS idx_refresh_times (index_name TEXT PRIMARY KEY,"
                     f" last_refresh_time TEXT)")


# list of supported indexes, can be expanded
supported_index_list = [supported_index_dict[index][0]+"_"+index for index in supported_index_dict.keys()]

# loop to create the index tables
[create_index_table(index) for index in supported_index_list]


# price_target average, growth_estimate in %, action_suggest is buy/hold/sell as a float,
# valuation is under or overweight as a float.
def create_exchange_table(exchange_name):
    index_db.execute(f"CREATE TABLE IF NOT EXISTS {exchange_name} (ticker TEXT PRIMARY KEY, company_name TEXT, "
                     "other_info TEXT, last_refresh_time TEXT, next_refresh_time TEXT, quote_type TEXT, address TEXT, "
                     "business_summary TEXT, trading_currency TEXT, industry TEXT, sector TEXT, company_officers TEXT, "
                     "recommendation TEXT, average_volume FLOAT, average_volume_10days FLOAT, dividend_yield FLOAT, "
                     "dividend_date TIMESTAMP, target_median_price FLOAT, target_mean_price FLOAT, market_cap FLOAT, "
                     "enterprise_value FLOAT, profit_margin FLOAT, total_debt FLOAT, operating_cash_flow FLOAT, "
                     "free_cash_flow FLOAT, gross_margins FLOAT, operating_margins FLOAT, shares_outstanding FLOAT, "
                     "shares_short FLOAT, held_percent_insiders FLOAT, held_percent_institutions FLOAT, employees INT,"
                     "earnings_quarterly_growth FLOAT, return_on_assets FLOAT, return_on_equity FLOAT, beta FLOAT, "
                     "trailing_PE FLOAT, forward_PE FLOAT, profile_data TEXT, recommendation_analysed INT, "
                     "valuation FLOAT, UNIQUE(ticker))")
    index_db.execute(f"CREATE TABLE IF NOT EXISTS exc_refresh_times (exchange_name TEXT PRIMARY KEY, "
                     f"last_refresh_time TEXT)")


# loop to create the exchange tables
[create_exchange_table(exchange) for exchange in supported_exchange_list]


def write_index(index_name, _tickers, _names, _other_info):
    for i in range(len(_tickers)):
        index_db.execute(f"INSERT OR REPLACE INTO {index_name} (ticker, company_name, other_info) "
                         f"VALUES (?, ?, ?)", (_tickers[i], _names[i], _other_info[i]))
    index_db.execute(f"INSERT OR REPLACE INTO idx_refresh_times (index_name, last_refresh_time) VALUES (?, ?)",
                     (index_name, datetime.datetime.now()))
    index_db.commit()


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
        _refresh_time = index_db.execute(f"SELECT last_refresh_time FROM idx_refresh_times WHERE "
                                         f"index_name = '{index_full_name}'").fetchone()
        _tickers, _names, _other_info = [None, None, None]
        if _refresh_time:
            if (datetime.datetime.now() < datetime.datetime.fromisoformat(_refresh_time[0]) +
                    datetime.timedelta(days=supported_index_dict[index_name][1])):
                _tickers = [str(index)[2:-3] for index in (index_db.execute(f"SELECT ticker FROM {index_full_name}").fetchall())]
                _names = [str(name)[2:-3] for name in index_db.execute(f"SELECT company_name FROM {index_full_name}").fetchall()]
                _other_info = [str(info)[2:-3] for info in index_db.execute(f"SELECT other_info FROM {index_full_name}").fetchall()]
        if not _tickers:
            _tickers, _names, _other_info = get_index(index_name)
            write_index(index_full_name, _tickers, _names, _other_info)

        if return_type == "tickers":
            return _tickers
        elif return_type == "_names":
            return _names
        elif return_type == "other_info":
            return _other_info
        elif return_type == "all":
            return exchange+"\n"+_tickers+"\n"+_names+"\n"+_other_info
    else:
        return "Index not found"


# check for index refreshes
for index in supported_index_dict.keys():
    load_index(index)


def write_exchange(exchange, _tickers, company_names, other_info):
    for i in range(len(_tickers)):
        index_db.execute(f"INSERT OR REPLACE INTO {exchange} (ticker, company_name, other_info) VALUES (?, ?, ?)",
                         (_tickers[i], company_names[i], other_info[i]))
    index_db.execute(f"INSERT OR REPLACE INTO exc_refresh_times (exchange_name, last_refresh_time) VALUES (?, ?)",
                     (exchange, datetime.datetime.now()))
    index_db.commit()


def load_exchange(exchange, return_type="tickers"):
    if exchange in supported_exchange_list:
        # check if the exchange needs to be refreshed by checking the refresh time
        _refresh_time = index_db.execute(f"SELECT last_refresh_time FROM exc_refresh_times WHERE "
                                         f"exchange_name = '{exchange}'").fetchone()
        _tickers, _names, _other_info = [None, None, None]
        if _refresh_time:
            if (datetime.datetime.now() < datetime.datetime.fromisoformat(_refresh_time[0]) +
                    datetime.timedelta(days=exchange_refresh_time)):
                _tickers = [str(index)[2:-3] for index in index_db.execute(f"SELECT ticker FROM {exchange}").fetchall()]
                _names = [str(name)[2:-3] for name in index_db.execute(f"SELECT company_name FROM {exchange}").fetchall()]
                _other_info = [str(info)[2:-3] for info in index_db.execute(f"SELECT other_info FROM {exchange}").fetchall()]
        if not _tickers:
            _tickers, _names, _other_info = get_exchange(exchange)
            write_exchange(exchange, _tickers, _names, _other_info)
        if return_type == "tickers":
            return _tickers
        elif return_type == "names":
            return _names
        elif return_type == "other_info":
            return str(_tickers)+"\n"+str(_other_info)
    else:
        return "Exchange not found"


# check for exchange refreshes
for exchange in supported_exchange_list:
    load_exchange(exchange)


def get_profile(_exchange, _ticker):
    try:
        t_info = yfinance.Ticker(_ticker).info
    except requests.exceptions.HTTPError:
        print(f"Ticker {_ticker} profile failed to load: HTTPError")
        return {}
    r_day_add, r_hour_add = random.randint(0, 5), random.randint(0, 23)

    # the below keys are perceived as mostly live data (gained from get_ticker_data()), so excluded from the cache
    ex_keys = ["previousClose", "open", "dayLow", "dayHigh", "regularMarketPreviousClose", "regularMarketOpen",
               "regularMarketDayLow", "regularMarketDayHigh", "bid", "ask", "bidSize", "askSize", "symbol",
               "underlyingSymbol", "currentPrice", "longName", "exchange", "shortName", "sector", "sectorDisp",
               "industry", "industryDisp", "currency", ]

    def updator(keys):
        data_field = ""

        if len(keys) > 1:
            for key in keys:
                if key in t_info.keys():
                    data_field += f"{key}: {t_info[key]}§"
                    t_info.pop(key)
        elif keys[0] in t_info.keys():
            data_field = t_info[keys[0]]
            t_info.pop(keys[0])
        if data_field in ["", "Infinity"]:
            return None
        else:
            if len(keys) > 1:
                return data_field[:-1]
            else:
                return data_field

    def updator_wrapper(_sql_to_ex, field_name, keys, field_type="float"):
        data_field = updator(keys)
        if data_field:
            if field_type in ["str"]:
                data_field = data_field.replace("'", "").replace('"', "").replace("’", "")
                _sql_to_ex += f"{field_name} = '{data_field}', "
            else:
                _sql_to_ex += f"{field_name} = {data_field}, "
        return _sql_to_ex

    sql_to_ex = (f"UPDATE {_exchange} SET last_refresh_time = '{datetime.datetime.now()}', "
                 f"next_refresh_time = '{(datetime.datetime.now() + 
                 datetime.timedelta(days=exchange_profiles_refresh_time+r_day_add, hours=r_hour_add))}', ")

    sql_builder = [["address", ["address1", "address2", "city", "state", "zip", "country", "phone", "website"], "str"],
                   ["trading_currency", ["financialCurrency"], "str"], ["industry", ["industryKey"], "str"],
                   ["sector", ["sectorKey"], "str"], ["quote_type", ["quoteType"], "str"],
                   ["business_summary", ["longBusinessSummary"], "str"], ["employees", ["fullTimeEmployees"]],
                   ["dividend_yield", ["dividendYield"]], ["dividend_date", ["exDividendDate"]],
                   ["trailing_PE", ["trailingPE"]], ["forward_PE", ["forwardPE"]],
                   ["beta", ["beta"]], ["market_cap", ["marketCap"]], ["enterprise_value", ["enterpriseValue"]],
                   ["total_debt", ["totalDebt"]], ["average_volume", ["averageVolume"]],
                   ["average_volume_10days", ["averageVolume10days"]], ["profit_margin", ["profitMargins"]],
                   ["shares_outstanding", ["sharesOutstanding"]], ["shares_short", ["sharesShort"]],
                   ["held_percent_insiders", ["heldPercentInsiders"]],
                   ["held_percent_institutions", ["heldPercentInstitutions"]],
                   ["earnings_quarterly_growth", ["earningsQuarterlyGrowth"]],
                   ["target_median_price", ["targetMedianPrice"]], ["target_mean_price", ["targetMeanPrice"]],
                   ["return_on_assets", ["returnOnAssets"]], ["return_on_equity", ["returnOnEquity"]],
                   ["operating_cash_flow", ["operatingCashflow"]], ["free_cash_flow", ["freeCashflow"]],
                   ["gross_margins", ["grossMargins"]], ["operating_margins", ["operatingMargins"]]]

    for field in sql_builder:
        if len(field) == 3:
            sql_to_ex = updator_wrapper(sql_to_ex, field[0], field[1], field[2])
        else:
            sql_to_ex = updator_wrapper(sql_to_ex, field[0], field[1])

    company_officers = updator(["companyOfficers"])
    if company_officers:
        company_officers_write = ""
        for officer in company_officers:
            for key in officer.keys():
                company_officers_write += f"{key}: {officer[key]}§"
            company_officers_write = company_officers_write[:-1]
            company_officers_write += "\n"
        company_officers_write = company_officers_write[:-1].replace("'", "").replace('"', "")
        sql_to_ex += f"company_officers = '{company_officers_write}', "

    recommendation = updator(["recommendationKey", "recommendationMean", "numberOfAnalystOpinions"])
    if recommendation and recommendation != "recommendationKey: none":
        sql_to_ex += f"recommendation = '{recommendation}', "

    profile_to_write = ""
    for _key in t_info.keys():
        if _key not in ex_keys:
            t_info[_key] = str(t_info[_key]).replace("\n", "")
            profile_to_write += f"{_key}§{t_info[_key].replace("'", "").replace('"', "")}\n"

    sql_to_ex += f"profile_data = '{profile_to_write}' WHERE ticker = '{_ticker}'"

    # execute the SQL command to write the profile data to the database
    index_db.execute(sql_to_ex)
    index_db.commit()


# count total tickers available
total_tickers = 0
for exchange in supported_exchange_list:
    total_tickers += len(index_db.execute(f"SELECT ticker FROM {exchange}").fetchall())

print(f"Total tickers: {total_tickers}")


# check for profile refreshes # todo make max hourly check, threaded updates?
counter = 0
for exchange in supported_exchange_list:
    tickers = [str(index)[2:-3] for index in index_db.execute(f"SELECT ticker FROM {exchange}").fetchall()]

    for ticker in tickers:
        counter += 1
        # get refresh time
        refresh_time = index_db.execute(f"SELECT next_refresh_time FROM {exchange} WHERE ticker = '{ticker}'").fetchone()

        scrape_profile = True
        if refresh_time != (None,):
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                scrape_profile = False

        if scrape_profile:
            print(f"Refreshing {exchange} -- {ticker} profile --- {counter}/{total_tickers}")
            profile_data = get_profile(exchange, ticker)

print("Profile refreshes complete")

# todo watchlist db here
# edit fields for compound fields, as storing same info twice dumb
#index_db.execute(f"CREATE TABLE IF NOT EXISTS watchlist (ticker TEXT PRIMARY KEY, company_name TEXT, "
#                 "other_info TEXT, last_refresh_time TEXT, next_refresh_time TEXT, quote_type TEXT, address TEXT, "
#                 "business_summary TEXT, trading_currency TEXT, industry TEXT, sector TEXT, company_officers TEXT, "
#                 "recommendation TEXT, average_volume FLOAT, average_volume_10days FLOAT, dividend_yield FLOAT, "
#                 "dividend_date TIMESTAMP, target_median_price FLOAT, target_mean_price FLOAT, market_cap FLOAT, "
#                 "enterprise_value FLOAT, profit_margin FLOAT, total_debt FLOAT, operating_cash_flow FLOAT, "
#                 "free_cash_flow FLOAT, gross_margins FLOAT, operating_margins FLOAT, shares_outstanding FLOAT, "
#                 "perecent_shares_short FLOAT, held_percent_insiders FLOAT, held_percent_institutions FLOAT, "
#                 "employees INT,earnings_quarterly_growth FLOAT, return_on_assets FLOAT, return_on_equity FLOAT, "
#                 "beta FLOAT, trailing_PE FLOAT, forward_PE FLOAT, profile_data TEXT, recommendation_analysed INT, "
#                 "valuation FLOAT, UNIQUE(ticker))")


# create the calendar tables
for country in site_dict.keys():
    index_db.execute(f"CREATE TABLE IF NOT EXISTS {country}_calendar (calender_date TEXT, ticker TEXT, "
                     f"company_name TEXT, event_name TEXT, market_time TEXT, EPS_estimate TEXT, EPS_reported TEXT, "
                     f"surprise TEXT, market_cap FLOAT, average_volume FLOAT)")


def load_earnings(market, date, sort_by):
    # try to load data from cache.
    return_list = index_db.execute(f"SELECT ticker, company_name, event_name, market_time, EPS_estimate, "
                                   f"EPS_reported, surprise, market_cap, average_volume FROM {market}_calendar WHERE "
                                   f"calender_date = '{date}'").fetchall()
    if return_list:
        return_list = [list(stock) for stock in return_list]
        print(return_list)
    else:
        return_list = []
        date = pandas.Timestamp(date).strftime("%Y-%m-%d")
        url = f"calendar/earnings?from=2024-05-26&to=2024-06-01&day={date}"
        calender = raw_daily_info(market, url, modify="&", convert_to_dict=False)

        if market == "us":
            exchange_list = ["nasdaq", "nyse", "nasdaq_other"]
        else:
            exchange_list = ["lse"]

        for stock in calender:
            for ex in exchange_list:
                try:
                    volume, market_cap = index_db.execute(f"SELECT average_volume_10days, market_cap FROM {ex} "
                                                          f"WHERE ticker = '{calender[stock][0]}'").fetchone()
                    if market_cap and volume:
                        if int(market_cap) > int(all_ex_watchlist_min_market_cap):
                            try:
                                if int(volume) > int(all_ex_watchlist_min_trade_volume):
                                    calender[stock].append(market_cap)
                                    calender[stock].append(volume)
                                    return_list.append(calender[stock])
                                    break
                            except TypeError:
                                pass
                except TypeError:
                    pass

        for stock in return_list:
            index_db.execute(f"INSERT INTO {market}_calendar (calender_date, ticker, company_name, "
                             f"event_name, market_time, EPS_estimate, EPS_reported, surprise, market_cap, "
                             f"average_volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (date, stock[0], stock[1], stock[2], stock[3], stock[4],
                              stock[5], stock[6], stock[7], stock[8]))
        index_db.commit()

    # sort return list by market cap or trade volume
    if sort_by == "market_cap":
        return_list.sort(key=lambda x: x[7], reverse=True)
    else:
        return_list.sort(key=lambda x: x[8], reverse=True)
    return return_list


# gets the stock splits for a given date
def get_stock_splits(date, sort_by):
    return_list = []
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    url = f"calendar/splits?from=2024-05-26&to=2024-06-01&day={date}"
    stock_splits = raw_daily_info("us", url, modify="&", convert_to_dict=False)
    for stock in stock_splits:
        for exchange in supported_exchange_list:
            try:
                volume, market_cap = index_db.execute(f"SELECT average_volume_10days, market_cap FROM {exchange} "
                                                      f"WHERE ticker = '{stock_splits[stock][0]}'").fetchone()
                if market_cap and volume:
                    if int(market_cap) > int(all_ex_watchlist_min_market_cap):
                        try:
                            if int(volume) > int(all_ex_watchlist_min_trade_volume):
                                stock_splits[stock].append(market_cap)
                                stock_splits[stock].append(volume)
                                return_list.append(stock_splits[stock])
                        except TypeError:
                            pass
            except TypeError:
                pass

    # sort return list by market cap or trade volume
    if sort_by == "market_cap":
        return_list.sort(key=lambda x: x[5], reverse=True)
    else:
        return_list.sort(key=lambda x: x[6], reverse=True)
    return return_list


def get_dated_calender(calender_name, date):
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    url = f"calendar/{calender_name}?from=2024-05-26&to=2024-06-01&day={date}"
    return raw_daily_info("us", url, modify="&")
