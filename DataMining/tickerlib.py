import requests
import re
import ftplib
import io
import random
import warnings
import os
import datetime
import pandas
import yfinance
import sqlite3

# This file contains TNS, cache based functions and the Ticker class
# HEAVILY MODIFIED FROM YAHOO-FIN LIBRARY AT: https://pypi.org/project/yahoo-fin/#history
# TNS links TICKERS, INDEXES and COMPANIES together

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


# connect to the ticker database
_ticker_db = sqlite3.connect("DataMining/TickerData/ticker.db")
_ticker_db.execute("CREATE TABLE IF NOT EXISTS profile (ticker TEXT PRIMARY KEY, refresh_time TEXT, profile_data TEXT,"
                   " UNIQUE(ticker))")


def _site_scraper_(site):  # load website so all contents can be scraped
    _data = {}
    for table in pandas.read_html(requests.get(site, headers=default_headers).text):
        for value in table.values:
            _data.update({value[0]: str(value[1:])[2:-2]})

    return _data


def table_to_dict(table, skip: int = 0):
    _data_ = {}
    for i, value in enumerate(table.values):
        if skip > 0:
            _data_.update({str(table.index[i]): [x for x in value[:-skip]]})
        else:
            _data_.update({str(table.index[i]): [x for x in value]})
        # filtering disabled as it has the potential to mess up indexes
        # _data.update({value[0]: [x for x in value[1:] if str(x) not in ["", "-", "nan", "NaN"]]})

    return _data_


def _tickers_sp500_():  # Downloads list of tickers currently listed in the S&P 500
    sp500 = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers = []
    for i in range(len(sp500)):
        sp_tickers.append(f"{sp500.values[i][0]}§{sp500.values[i][1]}§{sp500.values[i][2]}§"
                          f" {sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")

    return sp_tickers


def _nasdaq_trader_(search_param):  # Downloads list of nasdaq tickers
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = io.BytesIO()
    ftp.retrbinary(f'RETR {search_param}.txt', r.write)

    info = r.getvalue().decode()
    splits = info.split("|")

    ticker_list = [x for x in splits if len(x) > 1]
    ticker_data = []
    for i in range(len(ticker_list)-4):
        if ticker_list[i] == "100" and "-" in ticker_list[i+2]:
            stock_ticker = ticker_list[i+1].split('\r\n')[1]
            stock_name = ticker_list[i+2].split(" - ")[0]
            stock_type = str(ticker_list[i+2].split(" - ")[1:])[2:-2]
            if ".W" not in stock_ticker:
                ticker_data.append(f"{stock_ticker}§{stock_name}§{stock_type}")
        elif ticker_list[i] == "100" and "-" not in ticker_list[i+2] and "test stock" not in ticker_list[i+2].lower():
            stock_ticker = ticker_list[i+1].split('\r\n')[1]
            if ".W" not in stock_ticker:
                ticker_data.append(f"{stock_ticker}§{ticker_list[i+2]}")

    return ticker_data


def _tickers_nasdaq_():  # Nasdaq stocks
    return _nasdaq_trader_("nasdaqlisted")


def _tickers_us_other_():  # Nasdaq other, funds, etfs, etc.
    return _nasdaq_trader_("otherlisted")


def _tickers_dow_():  # Dow_Jones_Industrial_Average
    site = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    table = pandas.read_html(site, attrs={"id": "constituents"})[0]
    dow_tickers = []
    for i in range(len(table)):
        dow_tickers.append(f"{table.values[i][2]}§{table.values[i][0]}§{table.values[i][6]}§{table.values[i][1]}§"
                           f"{table.values[i][3]}")

    return dow_tickers


def _tickers_nifty50_():  # NIFTY 50, India
    site = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = pandas.read_html(site, attrs={"id": "constituents"})[0]
    _nifty50 = []
    for i in range(len(table)):
        _nifty50.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return _nifty50


def _tickers_ftse100_():  # UK 100
    table = pandas.read_html("https://en.wikipedia.org/wiki/FTSE_100_Index", attrs={"id": "constituents"})[0]
    _ftse100 = []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            _ftse100.append(f"{table.values[i][1]}L§{table.values[i][0]}§{table.values[i][2]}")
        else:
            _ftse100.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")
    return _ftse100


def _tickers_ftse250_():  # UK 250
    table = pandas.read_html("https://en.wikipedia.org/wiki/FTSE_250_Index", attrs={"id": "constituents"})[0]
    _ftse250 = []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            _ftse250.append(f"{table.values[i][1]}L§{table.values[i][0]}§{table.values[i][2]}")
        else:
            _ftse250.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")
    return _ftse250


def __writer__(file, refresh_days):
    with open(f"DataMining/TickerData/{file}.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.datetime.now()+datetime.timedelta(days=refresh_days)}\n")
        if file == "sp_500":
            ticker_data = _tickers_sp500_()
        elif file == "nasdaq":
            ticker_data = _tickers_nasdaq_()
        elif file == "nasdaq_other":
            ticker_data = _tickers_us_other_()
        elif file == "dow_jones":
            ticker_data = _tickers_dow_()
        elif file == "nifty50":
            ticker_data = _tickers_nifty50_()
        elif file == "ftse100":
            ticker_data = _tickers_ftse100_()
        elif file == "ftse250":
            ticker_data = _tickers_ftse250_()

        ticker_info = []
        for ticker in ticker_data:
            f.write(f"{ticker}\n")
            ticker_info.append(ticker.split("§"))

    return ticker_info


def _refresh_ticker_data_(file, refresh_days):
    if not os.path.exists(f"DataMining/TickerData/{file}.txt"):
        print(f"Downloading {file} tickers...")
        ticker_info = __writer__(file, refresh_days)
    else:
        with open(f"DataMining/TickerData/{file}.txt", "r", encoding="utf-8") as f:
            file_time = datetime.datetime.strptime(f.readline().split("+")[2].replace("\n", ""),
                                                   "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.datetime.now():
                ticker_info = __writer__(file, refresh_days)
                print(f"Found and refreshed {file} tickers...")
            else:
                print(f"Found {file} tickers...")
                ticker_info = []
                for ticker in f.readlines():
                    ticker_info.append(ticker.replace("\n", "").split("§"))
    return ticker_info


def __lse_writer__(lse_data, file, refresh_days):
    with open(f"DataMining/TickerData/{file}.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.datetime.now() + datetime.timedelta(days=refresh_days)}\n")
        for ticker in lse_data:
            line = ""
            for i in range(len(ticker)):
                if i == 0:
                    if ticker[i].endswith("."):
                        line += f"{ticker[i]}L§"
                    else:
                        line += f"{ticker[i]}.L§"
                else:
                    line += f"{ticker[i]}§"
            f.write(f"{line[:-1]}\n")


def __lse_reader__():
    if not os.path.exists(f"DataMining/TickerData/lse.xlsx"):
        print("LSE tickers not found, please download the file from "
              "https://www.londonstockexchange.com/reports?tab=instruments, then save it as lse.xlsx in the "
              "TickerData folder")
        exit()
    else:
        print(f"Downloading lse tickers...")
        _data = pandas.read_excel(f"DataMining/TickerData/lse.xlsx", None)
        all_eq = _data['1.0 All Equity'].values.tolist()[8:]
        all_no_eq = _data['2.0 All Non-Equity'].values.tolist()[8:]
        __lse_writer__(all_eq, "lse", 31)
        __lse_writer__(all_no_eq, "lse_eq", 31)
        os.rename("DataMining/TickerData/lse.xlsx", "DataMining/TickerData/lse_old.xlsx")
        return all_eq, all_no_eq


def _refresh_lse_tickers_():
    if not os.path.exists(f"DataMining/TickerData/lse.txt") or not os.path.exists(f"DataMining/TickerData/lse_eq.txt"):
        return __lse_reader__()
    else:
        with open(f"DataMining/TickerData/lse.txt", "r", encoding="utf-8") as f:
            file_time = datetime.datetime.strptime(f.readline().split("+")[2].replace("\n", ""),
                                                   "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.datetime.now():
                return __lse_reader__()
            else:
                print(f"Found lse and lse_eq tickers...")
                _lse_ = []
                for ticker in f.readlines():
                    _lse_.append(ticker.replace("\n", "").split("§"))
                _lse_eq_ = []
                with open(f"DataMining/TickerData/lse_eq.txt", "r", encoding="utf-8") as g:
                    for ticker in g.readlines()[1:]:
                        _lse_eq_.append(ticker.replace("\n", "").split("§"))
                return _lse_, _lse_eq_


def __ticker_info_writer__(_ticker):
    try:
        t_object = yfinance.Ticker(_ticker)
        t_info = t_object.info
    except requests.exceptions.HTTPError:
        print(f"Ticker {_ticker} profile failed to load: HTTPError")
        return {}
    ticker_profile = {}
    r_day_add, r_hour_add = random.randint(0, 5), random.randint(0, 23)
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

    data_to_write = ""
    for _key in t_info.keys():
        if _key not in ex_keys:
            t_info[_key] = str(t_info[_key]).replace("\n", "")
            data_to_write += f"{_key}§{t_info[_key]}\n"
            ticker_profile.update({_key: t_info[_key]})

    _ticker_db.execute("INSERT INTO profile VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET "
                       "refresh_time = ?, profile_data = ?",
                       (_ticker, datetime.datetime.now() +
                        datetime.timedelta(days=25+r_day_add, hours=r_hour_add),
                        data_to_write, datetime.datetime.now()+datetime.timedelta(days=25+r_day_add, hours=r_hour_add),
                        data_to_write))
    _ticker_db.commit()
    return ticker_profile


# loads company profile from cache or downloads it, returns profile data
def load_ticker_info(_ticker):
    try:
        refresh_time, profile_data = _ticker_db.execute(f"SELECT refresh_time, profile_data FROM "
                                                        f"profile WHERE ticker = '{_ticker}'").fetchone()
        refresh_time = datetime.datetime.strptime(refresh_time, "%Y-%m-%d %H:%M:%S.%f")
        if refresh_time < datetime.datetime.now():
            ticker_profile = __ticker_info_writer__(_ticker)
            print(f"Reloaded ticker profile for {_ticker}")
        else:
            ticker_profile = {}
            for line in profile_data.split("\n"):
                if len(line) > 0:
                    key, value = line.replace("\n", "").split("§")
                    ticker_profile.update({key: value})
        return ticker_profile
    except TypeError:
        ticker_profile = __ticker_info_writer__(_ticker)
        print(f"Generated profile: {_ticker}")
        return ticker_profile

#########################################################################
# START OF CACHE LOAD SYSTEM - Before this line no file manipulation


if not os.path.exists("DataMining/TickerData"):
    os.mkdir("DataMining/TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")

# type ticker: [ticker, company/type (e.g. bond, etf), other data]
# type index: [ticker, company, other data]
# type weighted index: [ticker, company, weight, other data]

_sp_500 = _refresh_ticker_data_("sp_500", 7)  # type index
_nasdaq = _refresh_ticker_data_("nasdaq", 7)  # type tickers
_nasdaq_other = _refresh_ticker_data_("nasdaq_other", 7)  # type tickers
_dow_jones = _refresh_ticker_data_("dow_jones", 7)  # type weighted index
_nifty50 = _refresh_ticker_data_("nifty50", 7)  # type index
_ftse100 = _refresh_ticker_data_("ftse100", 7)  # type index
_ftse250 = _refresh_ticker_data_("ftse250", 7)  # type index
_lse, _lse_eq = _refresh_lse_tickers_()  # type tickers

_tickers = {'nasdaq': _nasdaq, 'lse': _lse}
_tickers_other = {'nasdaq_other': _nasdaq_other, 'lse_eq': _lse_eq}
_tickers_all = {'nasdaq': _nasdaq, 'nasdaq_other': _nasdaq_other, 'lse': _lse, 'lse_eq': _lse_eq}
_indexes = {'sp_500': _sp_500, 'dow_jones': _dow_jones, 'nifty50': _nifty50,
            'ftse100': _ftse100, 'ftse250': _ftse250}

print("Loaded tickers and indexes successfully...\n-------------------------------------------")


def _tns_dict_from_search_(search, ticker_list, index_list, search_dict=None):
    if not search_dict:
        search_dict = {}
    for key in ticker_list.keys():
        for ticker in ticker_list[key]:
            if re.search(r"\b"+re.escape(search.lower())+r"\b", ticker[1].lower()):
                relevant_indexes = []
                for index in index_list.keys():
                    for _ticker in index_list[index]:
                        if ticker[0] == _ticker[0]:
                            relevant_indexes.append(index)
                search_dict.update({ticker[0]: ticker[1:]+[[relevant_indexes]]})
    return search_dict


# ticker name system  # todo add ETF/TYPE searching support
def _tns_(names, search_all):
    ticker_results = {}
    for name in names:
        related_tickers = _tns_dict_from_search_(name, _tickers, _indexes)

        # if no tickers found in {tickers} or if other=True, search {_tickers_other}
        if not related_tickers or search_all:
            related_tickers = _tns_dict_from_search_(name, _tickers_other, _indexes, related_tickers)

        # remove empty values from related_tickers
        for key in related_tickers.keys():
            for value in related_tickers[key]:
                if value == "":
                    related_tickers[key].remove(value)
        ticker_results.update({name: related_tickers})
    return ticker_results


# extra TNS code to try to detect if invalid ticker is returned from TNS and fix ticker
# code also returns ticker data
# def tns_check(ticker, name):
#    ticker_live = get_ticker_data(ticker)
#    fixed = True
#    try:
#        ticker_live['Open']
#    except KeyError:
#        fixed = False
#    for key in ticker_live.keys():
#        if re.search(r"\b"+re.escape(name.lower())+r"\b", ticker_live[key].lower()):
#            print(f"TNS Check fixed: {ticker[0][0]} --> {key}")
#            ticker = [[key, ticker_live[key]]]
#            ticker_live = get_ticker_data(ticker[0][0])
#            fixed = True
#            break
#    if not fixed:
#        print(ticker_live)
#        exit(f"Ticker error: TNS Check failed to resolve ticker")
#    return ticker_live


# loads or generates profile data for all tickers
def load_profiles():
    exec_dict = {}
    comp_names_l = {}
    comp_names_s = {}
    total_tickers = 0
    for key in _tickers_all.keys():
        total_tickers += len(_tickers_all[key])
    counter = 0
    for key in _tickers_all.keys():
        for ticker in _tickers_all[key]:
            counter += 1
            ticker_profile = load_ticker_info(ticker[0])
            if ticker_profile:
                if counter % 2500 == 0:
                    print(f"{counter}/{total_tickers} - {ticker[0]}")
                if "companyOfficers" in ticker_profile:
                    exec_dict.update({ticker[0]: eval(ticker_profile["companyOfficers"])})
                if "longName" in ticker_profile:
                    comp_names_l.update({ticker[0]: ticker_profile["longName"]})
                if "shortName" in ticker_profile:
                    comp_names_s.update({ticker[0]: ticker_profile["shortName"]})

    return exec_dict, comp_names_l, comp_names_s


# class of wrappers to return data from profile data
class _Data:
    def __init__(self):
        print("Loading profile data...")
        self.exec_dict, self.comp_names_l, self.comp_names_s = load_profiles()
        print("Loaded profile data successfully...\nFinished loading...\n"
              "-------------------------------------------")
        self.tickers = _tickers
        self.tickers_all = _tickers_all
        self.tickers_other = _tickers_other
        self.indexes = _indexes


data = _Data()


# The ticker name system class
class TNS:
    def __init__(self, company_list, search_all=False):
        self.tickers = _tns_(company_list, search_all)
        if not self.tickers:
            print("Ticker not found: TNS failed to resolve ticker(s)")

    def get_objects(self):
        ticker_objects = {}
        for key in self.tickers.keys():
            # getting only the 0 index means only the first result will be turned into an object
            key = [key for key in self.tickers[key].keys()][0]
            ticker_objects.update({key: _Ticker(key)})
        return ticker_objects

    def get_results(self):
        return self.tickers

    def get_objects_and_results(self):
        return self.get_objects(), self.get_results()


class _Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self._ticker_obj_ = yfinance.Ticker(ticker)
        self._profile_ = None

    def profile(self):  # returns profile data from cache
        if self._profile_:
            return self._profile_
        else:
            self._profile_ = load_ticker_info(self.ticker)
            return self._profile_

    def ticker_data(self):  # Scrapes data elements found on Yahoo Finance's quote page
        site = f"https://finance.yahoo.com/quote/{self.ticker}?p={self.ticker}"
        return _site_scraper_(site)

    def ticker_stats(self):  # Scrapes information from the statistics page on Yahoo Finance
        stats_site = f"https://finance.yahoo.com/quote/{self.ticker}/key-statistics?p={self.ticker}"
        ticker_stats = _site_scraper_(stats_site)
        if "Previous Close" in ticker_stats.keys():
            print("Ticker doesnt have stats")
            return {}
        else:
            return ticker_stats

    # this function does the same as t_object.institutional_holders,
    # t_object.major_holders, t_object.mutualfund_holders
    def holders(self):  # Scrapes the Holders page from Yahoo Finance for an input ticker
        holders_site = f"https://finance.yahoo.com/quote/{self.ticker}/holders?p={self.ticker}"
        holders_data = []
        for table in pandas.read_html(requests.get(holders_site, headers=default_headers).text):
            if isinstance(table, pandas.DataFrame):
                holders_data.append(table_to_dict(table))
            else:
                holders_data.append(table)

        return holders_data

    def analysts_info(self):  # Scrapes the Analysts page from Yahoo Finance for an input ticker
        analysts_site = f"https://finance.yahoo.com/quote/{self.ticker}/analysts?p={self.ticker}"
        analysts_data = []
        for table in pandas.read_html(requests.get(analysts_site, headers=default_headers).text):
            if isinstance(table, pandas.DataFrame):
                analysts_data.append(table_to_dict(table))
            else:
                analysts_data.append(table)

        return analysts_data

    def earnings_history(self):  # Scrapes the earnings calendar of ticker with EPS actual vs. expected.
        url = f"https://finance.yahoo.com/calendar/earnings?symbol={self.ticker}"
        return table_to_dict(pandas.read_html(requests.get(url, headers=default_headers).text)[0])

    def actions(self):  # returns dividends and stock split dates
        return table_to_dict(self._ticker_obj_.actions)

    def balance_sheet(self):
        return table_to_dict(self._ticker_obj_.balance_sheet)

    # print(t_object.capital_gains)  # returns blank

    def cash_flow(self):
        return table_to_dict(self._ticker_obj_.cash_flow)

    # print(t_object.dividends.values)  # returns blank

    def earnings_dates(self):  # returns table of earnings dates (EPS Estimate, EPS Actual, Surprise %)
        return table_to_dict(self._ticker_obj_.earnings_dates)

    def financials(self):
        return table_to_dict(self._ticker_obj_.financials)

    # todo check this is all the possible input parameters - function to get price history
    # print(t_object.history(start="2021-01-01", end="2021-01-10", interval="1d"))  # example of calling history
    def history(self, start=None, end=None, period=None, interval=None):
        return table_to_dict(self._ticker_obj_.history(start=start, end=end, period=period, interval=interval))

    def history_metadata(self):  # returns list and table 5 rows, 6 columns
        history_metadata = self._ticker_obj_.history_metadata
        history_metadata["tradingPeriods"] = table_to_dict(history_metadata["tradingPeriods"])
        return history_metadata

    def income_statement(self):
        return table_to_dict(self._ticker_obj_.income_stmt)

    def institutional_holders(self):  # returns table 10 rows, 5 columns
        return table_to_dict(self._ticker_obj_.institutional_holders)

    def major_holders(self):  # returns basic table 4 deep
        return table_to_dict(self._ticker_obj_.major_holders)

    def mutual_fund_holders(self):  # returns table of 10 rows, 5 columns
        return table_to_dict(self._ticker_obj_.mutualfund_holders)

    def news(self):  # returns yahoo finance news links in a dict
        return self._ticker_obj_.news

    # print(t_object.option_chain('2021-10-15'))
    # get option chain for specific expiration
    # opt = msft.option_chain('YYYY-MM-DD')
    # data available via: opt.calls, opt.puts
    def options(self):  # returns list of dates to use in option_chain (19 dates for example)
        return self._ticker_obj_.options

    def option_chain(self, date):  # returns table of 101x14, and table of 79x14 and metadata list
        option_data = []
        for table in self._ticker_obj_.option_chain(date):
            if isinstance(table, pandas.DataFrame):
                option_data.append(table_to_dict(table))
            else:
                option_data.append(table)
        return option_data

    def quarterly_balance_sheet(self):  # returns table 78 rows, 4 columns
        return table_to_dict(self._ticker_obj_.quarterly_balance_sheet)

    def quarterly_cash_flow(self):  # returns table 53 rows, 4 columns
        return table_to_dict(self._ticker_obj_.quarterly_cash_flow)

    def quarterly_financials(self):  # returns table 46 rows, 4 columns
        return table_to_dict(self._ticker_obj_.quarterly_financials)

    def quarterly_income_statement(self):  # returns table 46 rows, 4 columns
        return table_to_dict(self._ticker_obj_.quarterly_income_stmt)

    def splits(self):  # returns table of splits
        split_data = self._ticker_obj_.splits
        split_dict = {}
        for index in split_data.index:
            split_dict.update({str(index): split_data[index]})
        return split_dict

    # todo table_to_dict this function
    def shares_full(self, start=None, end=None):  # returns table
        return self._ticker_obj_.get_shares_full(start=start, end=end)
