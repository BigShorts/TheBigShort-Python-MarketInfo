import DataMining.tickers_and_cache as tnc


tickers = tnc.TNS(["tesla", "microsoft", "alphabet"]).get_objects()
print(tickers)
tickers[0]
