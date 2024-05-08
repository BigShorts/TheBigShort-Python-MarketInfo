import tickers_and_cache as tnc

earnings_for_day = tnc.earnings_for_date_us("2024-05-03")
print(earnings_for_day)
print(len(earnings_for_day))

tickers = tnc.TNS(["tesla"]).get_objects()
print(tickers)
print(tickers['TSLA'])
