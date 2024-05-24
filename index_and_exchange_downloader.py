import pandas
import ftplib
import io
import os
import warnings
import requests

# functions to download ticker lists and index lists

### exchange cache functions ###

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


def get_nyse():  # NYSE stocks
    fields = ["0–9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
              "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    nyse_names = []
    nyse_tickers = []
    for field in fields:
        nyse_page = requests.get(f"https://en.wikipedia.org/wiki/"
                                 f"Companies_listed_on_the_New_York_Stock_Exchange_({field})").content
        nyse_page = (str(nyse_page).split("<th>Country of origin\\n<")[1].split("</table>")[0])

        nyse_ticker_page = nyse_page.split("href=\"https://www.nyse.com/quote/XNYS:")[1:]

        for i in range(len(nyse_ticker_page[:-1])):
            nyse_ticker = nyse_ticker_page[i].split("\">")[0]
            nyse_name = nyse_ticker_page[i]
            if "p" not in nyse_ticker:
                nyse_tickers.append(nyse_ticker)
                try:
                    nyse_name = nyse_name.split("\\n<td>")[2].split("\\n")[0]
                    if "<a href" in nyse_name:
                        nyse_name = nyse_name.split("\">")[1].split("</a>")[0]
                except IndexError:
                    nyse_name = nyse_names[-1]
                nyse_names.append(nyse_name)

    return nyse_tickers, nyse_names, [None] * len(nyse_tickers)


def _nasdaq_trader_(search_param):  # Downloads list of nasdaq/nasdaq_other tickers
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = io.BytesIO()
    ftp.retrbinary(f'RETR {search_param}.txt', r.write)

    info = r.getvalue().decode()
    splits = info.split("|")

    ticker_list = [x for x in splits if len(x) > 1]
    nsd_tickers, nsd_names, nsd_type = [], [], []
    for i in range(len(ticker_list)-4):
        if ticker_list[i] == "100" and "-" in ticker_list[i+2]:
            stock_ticker = ticker_list[i+1].split('\r\n')[1]
            stock_name = ticker_list[i+2].split(" - ")[0]
            stock_type = str(ticker_list[i+2].split(" - ")[1:])[2:-2]
            if ".W" not in stock_ticker:
                nsd_tickers.append(stock_ticker)
                nsd_names.append(stock_name)
                nsd_type.append(stock_type)
        elif ticker_list[i] == "100" and "-" not in ticker_list[i+2] and "test stock" not in ticker_list[i+2].lower():
            stock_ticker = ticker_list[i+1].split('\r\n')[1]
            if ".W" not in stock_ticker:
                nsd_tickers.append(stock_ticker)
                nsd_names.append("")
                nsd_type.append(ticker_list[i+2])

    return nsd_tickers, nsd_names, nsd_type


def get_nasdaq():  # Nasdaq stocks
    return _nasdaq_trader_("nasdaqlisted")


def get_us_other():  # Nasdaq other, funds, etfs, etc.
    return _nasdaq_trader_("otherlisted")


def get_lse(lse_type, rename=False):  # LSE stocks
    if not os.path.exists(f"TickerData/lse.xlsx"):
        print("LSE tickers not found, please download the file from "
              "https://www.londonstockexchange.com/reports?tab=instruments, then save it as lse.xlsx in the "
              "TickerData folder")
        exit()
    else:
        _data = pandas.read_excel(f"TickerData/lse.xlsx", None)
        if lse_type == "eq":
            data = _data['1.0 All Equity'].values.tolist()[8:]
        else:
            data = _data['2.0 All Non-Equity'].values.tolist()[8:]

        tickers = []
        for i in range(len(data)):
            if data[i][0].endswith("."):
                tickers.append(f"{data[i][0]}L")
            else:
                tickers.append(f"{data[i][0]}.L")

        other_info = []
        current_line = ""
        for i in range(len(data)):
            for j in range(2, len(data[i])):
                current_line += f"{data[i][j]}§"
            other_info.append(current_line[:-1])
            current_line = ""

        if rename:
            os.rename("TickerData/lse.xlsx", "TickerData/lse_old.xlsx")

        return tickers, [x[1] for x in data], other_info


### index cache functions ###


def get_sp500():  # Downloads list of tickers currently listed in the S&P 500
    sp500 = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers, sp_names, sp_data = [], [], []
    for i in range(len(sp500)):
        sp_tickers.append(sp500.values[i][0])
        sp_names.append(sp500.values[i][1])
        sp_data.append(f"{sp500.values[i][2]}§{sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")
    return sp_tickers, sp_names, sp_data


def get_dow():  # Dow_Jones_Industrial_Average
    table = pandas.read_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
                             attrs={"id": "constituents"})[0]
    dow_tickers, dow_names, dow_data = [], [], []
    for i in range(len(table)):
        dow_tickers.append(table.values[i][2])
        dow_names.append(table.values[i][0])
        dow_data.append(f"{table.values[i][6]}§{table.values[i][1]}§{table.values[i][3]}")

    return dow_tickers, dow_names, dow_data


def get_nifty50():  # NIFTY 50, India
    table = pandas.read_html("https://en.wikipedia.org/wiki/NIFTY_50", attrs={"id": "constituents"})[0]
    n50_tickers, n50_names, n50_data = [], [], []
    for i in range(len(table)):
        n50_tickers.append(table.values[i][1])
        n50_names.append(table.values[i][0])
        n50_data.append(table.values[i][2])

    return n50_tickers, n50_names, n50_data


def get_ftse(ftse_num):
    table = pandas.read_html(f"https://en.wikipedia.org/wiki/FTSE_{ftse_num}_Index", attrs={"id": "constituents"})[0]
    ftse_tickers, ftse_names, ftse_data = [], [], []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            ftse_tickers.append(table.values[i][1] + "L")
        else:
            ftse_tickers.append(table.values[i][1] + ".L")
        ftse_names.append(table.values[i][0])
        ftse_data.append(table.values[i][2])
    return ftse_tickers, ftse_names, ftse_data


### wrapper functions to run ###


def get_index(index_name):  # Returns the tickers, names, and other info of the index
    if index_name == "SP500":
        return get_sp500()
    elif index_name == "DOW":
        return get_dow()
    elif index_name == "NIFTY50":
        return get_nifty50()
    elif index_name == "FTSE100":
        return get_ftse("100")
    elif index_name == "FTSE250":
        return get_ftse("250")
    else:
        return None, None, None


def get_exchange(exchange_name):  # Returns the tickers, names, and other info of the exchange
    print(f"Reloading {exchange_name} tickers")
    if exchange_name == "NASDAQ":
        return get_nasdaq()
    elif exchange_name == "NASDAQ_OTHER":
        return get_us_other()
    elif exchange_name == "NYSE":
        return get_nyse()
    elif exchange_name == "LSE":
        return get_lse("eq")
    elif exchange_name == "LSE_OTHER":
        return get_lse("non_eq", rename=True)
    else:
        return None, None, None
