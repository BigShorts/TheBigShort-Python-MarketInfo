from index_and_exchange_cache import *
import sqlite3
import datetime
import os

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
                      f"other_info TEXT, refresh_time TEXT, market_cap FLOAT, address TEXT, profile_data TEXT, "
                      f"price_target FLOAT, "
                      f"growth_estimate FLOAT, action_suggest FLOAT, valuation FLOAT, UNIQUE(ticker))")
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


# check for profile refreshes
# todo
import yfinance
t_object = yfinance.Ticker("NVDA")
nvda = t_object.info

# address
print(nvda["address1"])
#print(nvda["address2"])
print(nvda["city"])
print(nvda["state"])
print(nvda["country"])
print(nvda["zip"])
print(nvda["phone"])
print(nvda["website"])

# traded currency
print(nvda["financialCurrency"])

# industry
print(nvda["industryKey"])
# sector
print(nvda["sectorKey"])

# business_summary
print(nvda["longBusinessSummary"])

# employees
print(nvda["fullTimeEmployees"])

# company officers
print(nvda["companyOfficers"])

# dividend yield: as a percent of investment: £100 * yield of 4% = £4
# refer to https://www.investopedia.com/terms/e/ex-date.asp for info
print(nvda["dividendYield"])
print(nvda["exDividendDate"])  # timestamp of the ex-dividend date
# to get paid a dividend, you must own the stock before the ex-dividend date
# and 2 days before the record date (which is usually the day after ex-dividend date)
# --> summary, buy stock 1-2 days before ex-dividend date to get paid the dividend,
# --> hold to record date 1-2 days after ex-dividend date

# trailing PE ratio (Earnings per share history for last year)
print(nvda["trailingPE"])

# forward PE ratio (Earnings per share estimate for next year)
print(nvda["forwardPE"])

# beta (stock volatility relative to the S&P 500 which is 1.0) (less is more volatile)
print(nvda["beta"])

# market cap
print(nvda["marketCap"])  # shares value
print(nvda["enterpriseValue"])  # total value of company (including debt)
print(nvda["totalDebt"])  # total debt

# average traded volume
print(nvda["averageVolume"])  # average volume of shares traded per day
print(nvda["averageVolume10days"])  # average volume of shares traded per day over 10 days

# profit margin
print(nvda["profitMargins"])  # profit margin as a percentage of revenue

# shares outstanding
print(nvda["sharesOutstanding"])  # total number of shares issued by the company
print(nvda["sharesShort"])  # number of shares shorted

# held by insiders / institutions
print(nvda["heldPercentInsiders"])  # percentage of shares held by insiders
print(nvda["heldPercentInstitutions"])  # percentage of shares held by institutions

# earnings quarterly growth
print(nvda["earningsQuarterlyGrowth"])  # earnings growth from the previous quarter

# target median / mean price
print(nvda["targetMedianPrice"])  # median price target
print(nvda["targetMeanPrice"])  # mean price target

# yf recommendation
print(nvda["recommendationKey"])  # buy, hold, sell
print(nvda["recommendationMean"])  # mean recommendation
print(nvda["numberOfAnalystOpinions"])  # number of analyst opinions
# put the above into 1 line: such as "buy: 1.8, 15"

# return on assets / equity
print(nvda["returnOnAssets"])  # return on assets as a percentage, company efficiency on investments

# cash flow
print(nvda["operatingCashflow"])  # cash flow from operations
print(nvda["freeCashflow"])  # cash flow after accounting for capital expenditures

# gross margin
print(nvda["grossMargins"])  # gross profit margin as a percentage of revenue, company efficiency on production

# operating margins
print(nvda["operatingMargins"])  # profit per dollar of sales


# todo read through and remove items out of the list that are used above
# the below keys are perceived as mostly live data (gained from get_ticker_data()), so excluded from the cache
ex_keys = ["previousClose", "open", "dayLow", "dayHigh", "regularMarketPreviousClose", "regularMarketOpen",
           "regularMarketDayLow", "regularMarketDayHigh", "trailingPE", "forwardPE", "volume",
           "regularMarketVolume", "averageVolume", "averageVolume10days", "averageDailyVolume10Day", "bid",
           "ask", "bidSize", "askSize", "marketCap", "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "fiftyDayAverage",
           "twoHundredDayAverage", "trailingAnnualDividendRate", "trailingAnnualDividendYield",
           "enterpriseValue", "profitMargins", "floatShares", "sharesOutstanding", "sharesShort",
           "sharesShortPriorMonth", "sharesShortPreviousMonthDate", "sharesPercentSharesOut",
           "heldPercentInsiders", "heldPercentInstitutions", "shortRatio", "shortPercentOfFloat",
           "impliedSharesOutstanding", "bookValue", "priceToBook", "lastFiscalYearEnd", "nextFiscalYearEnd",
           "mostRecentQuarter", "earningsQuarterlyGrowth", "netIncomeToCommon", "trailingEps",
           "lastSplitFactor", "lastSplitDate", "enterpriseToRevenue", "enterpriseToEbitda", "52WeekChange",
           "SandP52WeekChange", "symbol", "underlyingSymbol", "currentPrice", "totalCash", "totalCashPerShare",
           "ebitda", "totalDebt", "currentRatio", "totalRevenue", "debtToEquity", "revenuePerShare",
           "returnOnAssets", "returnOnEquity", "grossProfits", "freeCashflow", "operatingCashflow",
           "revenueGrowth", "operatingMargins", "financialCurrency"]


