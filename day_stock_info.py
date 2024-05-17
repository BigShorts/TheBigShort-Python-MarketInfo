import json
import requests_html
import pandas
import requests
import datetime

# This file contains functions that scrape data from Yahoo Finance
# This file should be called when the program starts

urlUS = "https://finance.yahoo.com"
urlUK = "https://uk.finance.yahoo.com"
urlDE = "https://de.finance.yahoo.com"  # todo add de (germany)
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


def _force_float_(elt):
    try:
        return float(elt)
    except ValueError:
        return elt


def _convert_to_numeric_(s):
    if isinstance(s, float):
        return s

    if "M" in s:
        return _force_float_(s.strip("M")) * 1_000_000

    if "B" in s:
        return _force_float_(s.strip("B")) * 1_000_000_000

    if "T" in s:
        return _force_float_(s.strip("T")) * 1_000_000_000_000

    return _force_float_(s)


def table_to_dict(table, skip: int = 0):
    _data_ = {}
    for i, value in enumerate(table.values):
        if skip > 0:
            _data_.update({str(table.index[i]): [x for x in value[:-skip]]})
        else:
            _data_.update({str(table.index[i]): [x for x in value]})

    return _data_


def raw_daily_info(market, site, multiple_pages=False, sort_by_element=None, page_limit=50, skip=0):
    if market == "uk":
        site = f"{urlUK}/{site}"
    elif market == "us":
        site = f"{urlUS}/{site}"
    print(f"{site}?count=100")
    tables_list = []
    session = requests_html.HTMLSession()
    resp = session.get(f"{site}?count=100")

    # splits the html page where it says, for example, "1-100 of 256 results" and gets the number of pages from this
    if multiple_pages:
        pages = (int(str(resp.html.raw_html).split("<span>1-")[1].split(" results</span>")[0].split(" of ")[1])//100)+1
    else:
        pages = 1
    if pages > page_limit:
        pages = page_limit

    for i in range(pages):
        if i != 0:
            resp = session.get(f"{site}?count=100&offset={i*100}")
        tables = pandas.read_html(resp.html.raw_html)
        df = tables[0].copy()
        df.columns = tables[0].columns

        # todo add german de market
        if market == "uk":
            del df["52-week range"]
            df["% change"] = df["% change"].map(lambda x: float(x.strip("%").replace(",", "")))
        if market == "us":
            del df["52 Week Range"]
            df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%").replace(",", "")))
        try:
            del df["Day Chart"]
        except KeyError:
            pass

        # convert the fields to numeric from string
        for field in df.columns.tolist()[5:]:
            df[field] = df[field].map(_convert_to_numeric_)

        session.close()

        new_table = table_to_dict(df, skip=skip)

        # replace nan's with 0.0
        new_table = {key: [0.0 if str(value) == "nan" else value for value in new_table[key]] for key in new_table}

        # replace the dict keys with counted numbers relative to the page
        tables_list.append({x+1+(i*100): new_table[key] for x, key in enumerate(new_table)})

    # join all the tables into one
    if len(tables_list) > 1:
        result_table = {}
        [result_table.update(table) for table in tables_list]
    else:
        result_table = tables_list[0]

    # sort the table by the sort_by_element number item in the table
    if sort_by_element:
        if sort_by_element:
            # todo could i use a loop instead of comprehension?
            if result_table[1][sort_by_element] is float:
                result_table = {k: v for k, v in sorted(result_table.items(), key=lambda item:
                                item[1][sort_by_element], reverse=True)}
            else:
                result_table = {k: v for k, v in sorted(result_table.items(), key=lambda item:
                                float(item[1][sort_by_element]), reverse=True)}
            #for key, value in result_table.items():
            #    print(str(result_table[key][sort_by_element]) + " ---- " + str(value))

    # use list comprehension to make list of dictionaries
    return [str(value)[2:-3] for key, value in result_table.items()]


# Earnings functions
def _parse_earnings_json(url):
    resp = requests.get(url, headers=default_headers)
    content = resp.content.decode(encoding='utf-8', errors='strict')
    page_data = [row for row in content.split('\n') if row.startswith('root.App.main = ')][0][:-1]
    page_data = page_data.split('root.App.main = ', 1)[1]

    return json.loads(page_data)


# todo finish rewriting, create caching system
# Returns a dictionary of stock tickers with earnings expected EPS values for each stock.
def earnings_for_date_us(date=datetime.datetime.today()):
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    offset = 0
    tables = []
    while True:
        try:
            url = f"{urlUS}/calendar/earnings?day={date}&offset={offset}&size=100"
            tables += table_to_dict(pandas.read_html(requests.get(url, headers=default_headers).text)[0])
            offset += 100
        except ValueError:
            break
    # todo combine tables and number correctly
    print(tables)
    input()
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


# todo https://uk.finance.yahoo.com/industries/autos_transportation/ and other topics
