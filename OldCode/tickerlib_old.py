import requests
import re
import random
import warnings
import os
import datetime
import pandas
import yfinance  # https://github.com/ranaroussi/yfinance
# todo check for new API access points, price targets and upgrades and downgrades useful

# This file contains TNS, cache based functions and the Ticker class
# HEAVILY MODIFIED FROM YAHOO-FIN LIBRARY AT: https://pypi.org/project/yahoo-fin/#history
# TNS links TICKERS, INDEXES and COMPANIES together

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


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


# todo rename and make more sense
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