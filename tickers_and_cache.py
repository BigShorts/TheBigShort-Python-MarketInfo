import json
import requests_html
from OldCode.tickerlib_old import *

# This file contains functions that scrape data from Yahoo Finance
# This file should be called when the program starts

_urlUS_ = "https://finance.yahoo.com/"
_urlUK_ = "https://uk.finance.yahoo.com"


def _force_float_(elt):
    try:
        return float(elt)
    except ValueError:
        return elt


def _convert_to_numeric_(s):
    if isinstance(s, float):
        return s

    if "M" in s:
        s = s.strip("M")
        return _force_float_(s) * 1_000_000

    if "B" in s:
        s = s.strip("B")
        return _force_float_(s) * 1_000_000_000

    return _force_float_(s)


def __raw_daily_info__(site, uk=False, skip=0):
    session = requests_html.HTMLSession()
    resp = session.get(site)
    tables = pandas.read_html(resp.html.raw_html)
    df = tables[0].copy()
    df.columns = tables[0].columns

    if uk:
        del df["52-week range"]
        df["% change"] = df["% change"].map(lambda x: float(x.strip("%").replace(",", "")))
        fields_to_change = [x for x in df.columns.tolist() if "Vol" in x or x == "Market cap"]
    else:
        del df["52 Week Range"]
        df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%+").replace(",", "")))
        fields_to_change = [x for x in df.columns.tolist() if "Vol" in x or x == "Market Cap"]

    for field in fields_to_change:
        if isinstance(df[field][0], str):
            df[field] = df[field].map(_convert_to_numeric_)

    session.close()

    return table_to_dict(df, skip=skip)


def day_most_active_us(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUS_}/most-active?offset={offset}&count={count}")


def day_most_active_uk(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUK_}/most-active?offset={offset}&count={count}", True)


def day_gainers_us(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUS_}/gainers?offset={offset}&count={count}")


def day_gainers_uk(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUK_}/gainers?offset={offset}&count={count}", True)


def day_losers_us(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUS_}/losers?offset={offset}&count={count}")


def day_losers_uk(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUK_}/losers?offset={offset}&count={count}", True)


def day_trending_tickers():
    return __raw_daily_info__(f"{_urlUS_}/trending-tickers", skip=2)


def day_top_etfs_us(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUS_}/etfs?offset={offset}&count={count}")


def day_top_etfs_uk(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"https://uk.finance.yahoo.com/etfs?offset={offset}&count={count}", True)


def day_top_mutual_us(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUS_}/mutualfunds?offset={offset}&count={count}")


def day_top_mutual_uk(offset: int = 0, count: int = 100):
    return __raw_daily_info__(f"{_urlUK_}/mutualfunds?offset={offset}&count={count}", True)


def day_top_futures_us():
    # why is there an unnamed column???
    return table_to_dict(pandas.read_html(requests.get(f"{_urlUS_}/commodities",headers=default_headers).text)[0],
                         skip=1)


def day_top_futures_uk():
    # why is there an unnamed column???
    return table_to_dict(pandas.read_html(requests.get(f"{_urlUK_}/commodities", headers=default_headers).text)[0],
                         skip=1)


def day_highest_open_interest(offset: int = 0, count: int = 100):
    # uses a different table format than other daily infos
    return table_to_dict(pandas.read_html(requests.get(f"{_urlUS_}/options/highest-open-interest?"
                                          f"offset={offset}&count={count}", headers=default_headers).text)[0])


def day_highest_implied_volatility(offset: int = 0, count: int = 100):
    # uses a different table format than other daily infos
    return table_to_dict(pandas.read_html(requests.get(f"{_urlUS_}/options/highest-implied-volatility?"
                                          f"offset={offset}&count={count}", headers=default_headers).text)[0])


def day_top_world_indices():
    return __raw_daily_info__(f"{_urlUS_}/world-indices", skip=2)


def day_top_forex_rates():
    return __raw_daily_info__(f"{_urlUS_}/currencies", skip=1)


def day_top_us_bonds():
    return __raw_daily_info__(f"{_urlUS_}/bonds", skip=1)


def day_top_crypto(offset: int = 0, count: int = 100):
    session = requests_html.HTMLSession()
    resp = session.get(f"{_urlUS_}/cryptocurrencies?offset={offset}&count={count}")
    df = pandas.read_html(resp.html.raw_html)[0].copy()
    df["% Change"] = df["% Change"].map(lambda x: float(str(x).strip("%").strip("+").replace(",", "")))
    del df["52 Week Range"]
    del df["Day Chart"]

    fields_to_change = [x for x in df.columns.tolist() if "Volume" in x
                        or x == "Market Cap" or x == "Circulating Supply"]

    for field in fields_to_change:
        if isinstance(df[field][0], str):
            df[field] = df[field].map(lambda x: _convert_to_numeric_(str(x)))

    session.close()

    return table_to_dict(df)


# Earnings functions
def _parse_earnings_json(url):
    resp = requests.get(url, headers=default_headers)
    content = resp.content.decode(encoding='utf-8', errors='strict')
    page_data = [row for row in content.split('\n') if row.startswith('root.App.main = ')][0][:-1]
    page_data = page_data.split('root.App.main = ', 1)[1]

    return json.loads(page_data)


# todo finish rewriting
# Returns a dictionary of stock tickers with earnings expected EPS values for each stock.
def earnings_for_date_us(date=datetime.datetime.today()):
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    offset = 0
    tables = []
    while True:
        try:
            url = f"{_urlUS_}/calendar/earnings?day={date}&offset={offset}&size=100"
            tables += table_to_dict(pandas.read_html(requests.get(url, headers=default_headers).text)[0])
            offset += 100
        except ValueError:
            break
    # todo combine tables and number correctly
    return tables


# Returns a dictionary of stock tickers with earnings expected EPS values for each stock.
def earnings_for_date_uk(date=datetime.datetime.today(), offset=0, count=100):
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    url = f"https://uk.finance.yahoo.com/calendar/earnings?day={date}&offset={offset}&size={count}"
    try:
        return table_to_dict(pandas.read_html(requests.get(url, headers=default_headers).text)[0])
    except ValueError:
        return {}


def _earnings_in_date_(start_date, end_date, market):
    earnings_data = {}
    days_diff = (pandas.Timestamp(end_date)-pandas.Timestamp(start_date)).days
    dates = [pandas.Timestamp(start_date)+datetime.timedelta(diff) for diff in range(days_diff+1)]

    for date in dates:
        if market == "uk":
            earnings_data.update({str(date)[:-9]: earnings_for_date_uk(date)})
        elif market == "us":
            earnings_data.update({str(date)[:-9]: earnings_for_date_us(date)})

    return earnings_data


# Returns the stock tickers with expected EPS data for all dates in the input range
def earnings_in_date_range_us(start_date, end_date):
    return _earnings_in_date_(start_date, end_date, "us")


# Returns the stock tickers with expected EPS data for all dates in the input range
def earnings_in_date_range_uk(start_date, end_date):
    return _earnings_in_date_(start_date, end_date, "uk")


def currencies():  # Returns the currencies table from Yahoo Finance
    site = "{site_base}/currencies"
    return table_to_dict(pandas.read_html(requests.get(site, headers=default_headers).text)[0], skip=2)


def futures():  # Returns the futures table from Yahoo Finance
    site = "{site_base}/commodities"
    return table_to_dict(pandas.read_html(requests.get(site, headers=default_headers).text)[0], skip=1)


# Returns the undervalued large caps table from Yahoo Finance
def undervalued_large_caps_us(offset: int = 0, count: int = 100):
    site = f"{_urlUS_}/screener/predefined/undervalued_large_caps?offset={offset}&count={count}"
    return table_to_dict(pandas.read_html(requests.get(site, headers=default_headers).text)[0], skip=1)


def undervalued_large_caps_uk(offset: int = 0, count: int = 100):
    # Returns the undervalued large caps table from Yahoo Finance
    site = f"https://uk.finance.yahoo.com/screener/predefined/undervalued_large_caps?offset={offset}&count={count}"
    return table_to_dict(pandas.read_html(requests.get(site, headers=default_headers).text)[0], skip=1)
