import requests_html
import pandas

# This file contains functions that scrape data from Yahoo Finance
# This file powers the day events (screeners) API calls

site_dict = {"us": "https://finance.yahoo.com", "uk": "https://uk.finance.yahoo.com",
             "de": "https://de.finance.yahoo.com"}
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


def raw_daily_info(market, site, multiple_pages=False, sort_by_element=None, page_limit=50, skip=0,
                   modify="?", convert_to_dict=True):
    site = f"{site_dict[market]}/{site}"
    print(f"{site}?count=100")
    tables_list = []
    session = requests_html.HTMLSession()
    resp = session.get(f"{site}{modify}count=100")

    # splits the html page where it says, for example, "1-100 of 256 results" and gets the number of pages from this
    try:
        if multiple_pages:
            pages = (int(str(resp.html.raw_html).split("<span>1-")[1].split(" results</span>")[0].split(" of ")[1])//100)+1
        else:
            pages = 1
        if pages > page_limit:
            pages = page_limit
    except IndexError:
        return []

    for i in range(pages):
        if i != 0:
            resp = session.get(f"{site}{modify}count=100&offset={i*100}")
        try:
            tables = pandas.read_html(resp.html.raw_html)
        except ValueError:
            break
        df = tables[0].copy()
        df.columns = tables[0].columns

        # todo add german de market
        try:
            if market == "uk":
                del df["52-week range"]
                df["% change"] = df["% change"].map(lambda x: float(x.strip("%").replace(",", "")))
            if market == "us":
                del df["52 Week Range"]
                df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%").replace(",", "")))
            del df["Day Chart"]
        except KeyError:
            pass

        # convert the fields to numeric from string
        for field in df.columns.tolist()[5:]:
            df[field] = df[field].map(_convert_to_numeric_)

        session.close()

        # convert table to dict then replace nan's with 0.0
        new_table = table_to_dict(df, skip=skip)
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
        if sort_by_element == "percent_change":
            sort_by_element = 4
        else:
            sort_by_element = 7

        if result_table[1][sort_by_element] is float:
            result_table = {k: v for k, v in sorted(result_table.items(), key=lambda item:
                            item[1][sort_by_element], reverse=True)}
        else:
            result_table = {k: v for k, v in sorted(result_table.items(), key=lambda item:
                            float(item[1][sort_by_element]), reverse=True)}

    # use list comprehension to make list of dictionaries
    if convert_to_dict:
        return [str(value)[2:-2] for key, value in result_table.items()]
    else:
        return result_table
