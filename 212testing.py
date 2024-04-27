import requests

#url = "https://demo.trading212.com/api/v0/equity/metadata/exchanges"
#url = "https://demo.trading212.com/api/v0/equity/metadata/instruments"
#url = "https://demo.trading212.com/api/v0/equity/pies"
#url = "https://demo.trading212.com/api/v0/equity/orders"
#url = "https://demo.trading212.com/api/v0/equity/orders/limit"
#url = "https://demo.trading212.com/api/v0/equity/orders/market"
#url = "https://demo.trading212.com/api/v0/equity/orders/stop"
#url = "https://demo.trading212.com/api/v0/equity/orders/stop_limit"
#url = "https://demo.trading212.com/api/v0/equity/orders/" + id
#url = "https://demo.trading212.com/api/v0/equity/account/cash"
#url = "https://demo.trading212.com/api/v0/equity/account/info"
#url = "https://demo.trading212.com/api/v0/equity/portfolio"
#url = "https://demo.trading212.com/api/v0/equity/portfolio/" + ticker
#url = "https://demo.trading212.com/api/v0/equity/history/orders"
#url = "https://demo.trading212.com/api/v0/history/dividends"
#url = "https://demo.trading212.com/api/v0/history/exports"
#url = "https://demo.trading212.com/api/v0/history/transactions"

with open("api_key.txt", "r") as f:
    api_key = f.read()

headers = {"Authorization": api_key}

#response = requests.get(url, headers=headers)

#data = response.json()
#for ticker in data:
#    print(ticker)


url = "https://live.trading212.com/api/v0/equity/metadata/exchanges"


response = requests.get(url, headers=headers)

data = response.json()
print(data)

# todo assign job of taking market timings apart to someone else
