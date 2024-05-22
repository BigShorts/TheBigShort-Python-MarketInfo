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
index_db = sqlite3.connect("TickerData/indexes.db", check_same_thread=False)


# code to create the index tables
def create_index_table(index_name):
    index_db.execute(f"CREATE TABLE IF NOT EXISTS {index_name} (ticker TEXT PRIMARY KEY, company_name TEXT, "
                     f"other_info TEXT)")
    index_db.execute(f"CREATE TABLE IF NOT EXISTS idx_refresh_times (index_name TEXT PRIMARY KEY, refresh_time TEXT)")


# list of supported indexes, can be expanded
supported_index_dict = {"SP500": ["NASDAQ", 1], "DOW": ["NASDAQ", 5], "NIFTY50": ["NSE", 7], "FTSE100": ["LSE", 1],
                        "FTSE250": ["LSE", 1]}
supported_index_list = [supported_index_dict[index][0]+"_"+index for index in supported_index_dict.keys()]

# loop to create the index tables
[create_index_table(index) for index in supported_index_list]


# price_target average, growth_estimate in %, action_suggest is buy/hold/sell as a float,
# valuation is under or overweight as a float.
def create_exchange_table(exchange_name):
    index_db.execute(f"CREATE TABLE IF NOT EXISTS {exchange_name} (ticker TEXT PRIMARY KEY, company_name TEXT, "
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
    index_db.execute(f"CREATE TABLE IF NOT EXISTS exc_refresh_times (exchange_name TEXT PRIMARY KEY, refresh_time TEXT)")


# list of supported exchanges # LSE_OTHER was removed as 20k irrelevant tickers
supported_exchange_list = ["NASDAQ", "NASDAQ_OTHER", "LSE"]#, "LSE_OTHER"]

# loop to create the exchange tables
[create_exchange_table(exchange) for exchange in supported_exchange_list]


def write_index(index_name, refresh_days, tickers, names, other_info):
    for i in range(len(tickers)):
        index_db.execute(f"INSERT OR REPLACE INTO {index_name} (ticker, company_name, other_info) "
                          f"VALUES (?, ?, ?)", (tickers[i], names[i], other_info[i]))
    index_db.execute(f"INSERT OR REPLACE INTO idx_refresh_times (index_name, refresh_time) VALUES (?, ?)",
                      (index_name, datetime.datetime.now() + datetime.timedelta(days=refresh_days)))
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
        refresh_time = index_db.execute(f"SELECT refresh_time FROM idx_refresh_times WHERE "
                                         f"index_name = '{index_full_name}'").fetchone()
        tickers = None
        if refresh_time:
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                tickers = [str(index)[2:-3] for index in (index_db.execute(f"SELECT ticker FROM {index_full_name}").fetchall())]
                names = [str(name)[2:-3] for name in index_db.execute(f"SELECT company_name FROM {index_full_name}").fetchall()]
                other_info = [str(info)[2:-3] for info in index_db.execute(f"SELECT other_info FROM {index_full_name}").fetchall()]
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
        index_db.execute(f"INSERT OR REPLACE INTO {exchange} (ticker, company_name, other_info) VALUES (?, ?, ?)",
                          (tickers[i], company_names[i], other_info[i]))
    index_db.execute(f"INSERT OR REPLACE INTO exc_refresh_times (exchange_name, refresh_time) VALUES (?, ?)",
                      (exchange, datetime.datetime.now() + datetime.timedelta(refresh_days)))
    index_db.commit()


def load_exchange(exchange, return_type="tickers", refresh_days=3):
    if exchange in supported_exchange_list:
        # check if the exchange needs to be refreshed by checking the refresh time
        refresh_time = index_db.execute(f"SELECT refresh_time FROM exc_refresh_times WHERE "
                                         f"exchange_name = '{exchange}'").fetchone()
        tickers = None
        if refresh_time:
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                tickers = [str(index)[2:-3] for index in index_db.execute(f"SELECT ticker FROM {exchange}").fetchall()]
                names = [str(name)[2:-3] for name in index_db.execute(f"SELECT company_name FROM {exchange}").fetchall()]
                other_info = [str(info)[2:-3] for info in index_db.execute(f"SELECT other_info FROM {exchange}").fetchall()]
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

    sql_to_ex = f"UPDATE {_exchange} SET refresh_time = '{datetime.datetime.now() + 
                  datetime.timedelta(days=21+r_day_add, hours=r_hour_add)}', "

    sql_to_ex = updator_wrapper(sql_to_ex, "address", ["address1", "address2", "city", "state",
                                                       "zip", "country", "phone", "website"], "str")
    sql_to_ex = updator_wrapper(sql_to_ex, "trading_currency", ["financialCurrency"], "str")
    sql_to_ex = updator_wrapper(sql_to_ex, "industry", ["industryKey"], "str")
    sql_to_ex = updator_wrapper(sql_to_ex, "sector", ["sectorKey"], "str")
    sql_to_ex = updator_wrapper(sql_to_ex, "quote_type", ["quoteType"], "str")
    sql_to_ex = updator_wrapper(sql_to_ex, "business_summary", ["longBusinessSummary"], "str")
    sql_to_ex = updator_wrapper(sql_to_ex, "employees", ["fullTimeEmployees"])

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

    sql_to_ex = updator_wrapper(sql_to_ex, "dividend_yield", ["dividendYield"])
    sql_to_ex = updator_wrapper(sql_to_ex, "dividend_date", ["exDividendDate"])
    sql_to_ex = updator_wrapper(sql_to_ex, "trailing_PE", ["trailingPE"])
    sql_to_ex = updator_wrapper(sql_to_ex, "forward_PE", ["forwardPE"])
    sql_to_ex = updator_wrapper(sql_to_ex, "beta", ["beta"])
    sql_to_ex = updator_wrapper(sql_to_ex, "market_cap", ["marketCap"])
    sql_to_ex = updator_wrapper(sql_to_ex, "enterprise_value", ["enterpriseValue"])
    sql_to_ex = updator_wrapper(sql_to_ex, "total_debt", ["totalDebt"])
    sql_to_ex = updator_wrapper(sql_to_ex, "average_volume", ["averageVolume"])
    sql_to_ex = updator_wrapper(sql_to_ex, "average_volume_10days", ["averageVolume10days"])
    sql_to_ex = updator_wrapper(sql_to_ex, "profit_margin", ["profitMargins"])
    sql_to_ex = updator_wrapper(sql_to_ex, "shares_outstanding", ["sharesOutstanding"])
    sql_to_ex = updator_wrapper(sql_to_ex, "shares_short", ["sharesShort"])
    sql_to_ex = updator_wrapper(sql_to_ex, "held_percent_insiders", ["heldPercentInsiders"])
    sql_to_ex = updator_wrapper(sql_to_ex, "held_percent_institutions", ["heldPercentInstitutions"])
    sql_to_ex = updator_wrapper(sql_to_ex, "earnings_quarterly_growth", ["earningsQuarterlyGrowth"])
    sql_to_ex = updator_wrapper(sql_to_ex, "target_median_price", ["targetMedianPrice"])
    sql_to_ex = updator_wrapper(sql_to_ex, "target_mean_price", ["targetMeanPrice"])

    recommendation = updator(["recommendationKey", "recommendationMean", "numberOfAnalystOpinions"])
    if recommendation and recommendation != "recommendationKey: none":
        sql_to_ex += f"recommendation = '{recommendation}', "

    sql_to_ex = updator_wrapper(sql_to_ex, "return_on_assets", ["returnOnAssets"])
    sql_to_ex = updator_wrapper(sql_to_ex, "return_on_equity", ["returnOnEquity"])
    sql_to_ex = updator_wrapper(sql_to_ex, "operating_cash_flow", ["operatingCashflow"])
    sql_to_ex = updator_wrapper(sql_to_ex, "free_cash_flow", ["freeCashflow"])
    sql_to_ex = updator_wrapper(sql_to_ex, "gross_margins", ["grossMargins"])
    sql_to_ex = updator_wrapper(sql_to_ex, "operating_margins", ["operatingMargins"])

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
        refresh_time = index_db.execute(f"SELECT refresh_time FROM {exchange} WHERE ticker = '{ticker}'").fetchone()

        scrape_profile = True
        if refresh_time != (None,):
            if datetime.datetime.now() < datetime.datetime.fromisoformat(refresh_time[0]):
                scrape_profile = False

        if scrape_profile:
            print(f"Refreshing {exchange} -- {ticker} profile --- {counter}/{total_tickers}")
            profile_data = get_profile(exchange, ticker)

print("Profile refreshes complete")

# todo watchlist db here
