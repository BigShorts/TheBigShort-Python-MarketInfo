import pandas
import ftplib
import io

### exchange cache functions ###

def _nasdaq_trader_(search_param):  # Downloads list of nasdaq tickers
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


def get_us_other_():  # Nasdaq other, funds, etfs, etc.
    return _nasdaq_trader_("otherlisted")


### index cache functions ###


def get_sp500():  # Downloads list of tickers currently listed in the S&P 500
    sp500 = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers, sp_names, sp_data = [], [], []
    for i in range(len(sp500)):
        sp_tickers.append(sp500.values[i][0])
        sp_names.append(sp500.values[i][1])
        sp_data.append(f"{sp500.values[i][2]}§{sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")
    return (sp_tickers), (sp_names), (sp_data)


def get_dow():  # Dow_Jones_Industrial_Average
    table = pandas.read_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
                             attrs={"id": "constituents"})[0]
    dow_tickers, dow_names, dow_data = [], [], []
    for i in range(len(table)):
        dow_tickers.append(table.values[i][2])
        dow_names.append(table.values[i][0])
        dow_data.append(f"{table.values[i][6]}§{table.values[i][1]}§{table.values[i][3]}")

    return (dow_tickers), (dow_names), (dow_data)


def get_nifty50():  # NIFTY 50, India
    table = pandas.read_html("https://en.wikipedia.org/wiki/NIFTY_50", attrs={"id": "constituents"})[0]
    n50_tickers, n50_names, n50_data = [], [], []
    for i in range(len(table)):
        n50_tickers.append(table.values[i][1])
        n50_names.append(table.values[i][0])
        n50_data.append(table.values[i][2])

    return (n50_tickers), (n50_names), (n50_data)


# todo below can become one function change links
def get_ftse100():  # UK 100
    table = pandas.read_html("https://en.wikipedia.org/wiki/FTSE_100_Index", attrs={"id": "constituents"})[0]
    ftse100_tickers, ftse100_names, ftse100_data = [], [], []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            ftse100_tickers.append(table.values[i][1]+"L")
        else:
            ftse100_tickers.append(table.values[i][1]+".L")
        ftse100_names.append(table.values[i][0])
        ftse100_data.append(table.values[i][2])
    return (ftse100_tickers), (ftse100_names), (ftse100_data)


def get_ftse250():  # UK 250
    table = pandas.read_html("https://en.wikipedia.org/wiki/FTSE_250_Index", attrs={"id": "constituents"})[0]
    ftse250_tickers, ftse250_names, ftse250_data = [], [], []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            ftse250_tickers.append(table.values[i][1]+"L")
        else:
            ftse250_tickers.append(table.values[i][1]+".L")
        ftse250_names.append(table.values[i][0])
        ftse250_data.append(table.values[i][2])
    return (ftse250_tickers), (ftse250_names), (ftse250_data)


def get_index(index_name):  # Returns the tickers, names, and other info of the index
    if index_name == "SP500":
        return get_sp500()
    elif index_name == "DOW":
        return get_dow()
    elif index_name == "NIFTY50":
        return get_nifty50()
    elif index_name == "FTSE100":
        return get_ftse100()
    elif index_name == "FTSE250":
        return get_ftse250()
    else:
        return None, None, None


# todo continue work
def get_exchange(exchange_name):  # Returns the tickers, names, and other info of the exchange
    if exchange_name == "NASDAQ":
        return get_nasdaq()
    elif exchange_name == "NASDAQ_OTHER":
        return get_us_other_()
    elif exchange_name == "NYSE":
        return ""
    elif exchange_name == "LSE":
        return ""
    else:
        return None, None, None