import yfinance
t_object = yfinance.Ticker("MBG.DE")
nvda = t_object.info

# address
print(nvda["address1"])
#print(nvda["address2"])
print(nvda["city"])
#print(nvda["state"])
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

# beta (stock volatility relative to the S&P 500 which is 1.0) (more is more volatile)
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
#print(nvda["sharesShort"])  # number of shares shorted

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
print(nvda["returnOnAssets"])  # return on assets as a percentage, company efficiency on its spending investments
print(nvda["returnOnEquity"])  # return on equity as a percentage, company efficiency on shareholder equity

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

# todo check need for separate [price target, growth estimate, action suggest, valuation] functions.


# below code for writing a ticker to the cache
