# list of supported indexes
# the values are the index refresh times in days (checks for updates to indexes)
supported_index_dict = {"SP500": ["NASDAQ", 1], "DOW": ["NASDAQ", 5], "NIFTY50": ["NSE", 7], "FTSE100": ["LSE", 1],
                        "FTSE250": ["LSE", 1]}


# list of supported exchanges # LSE_OTHER is commented out as 20k irrelevant tickers
supported_exchange_list = ["NASDAQ", "NASDAQ_OTHER", "LSE"]#, "LSE_OTHER"]

# exchange refresh time in days (checks for newly added stocks)
exchange_refresh_time = 31
# (is random +0-5 days to avoid all exchanges refreshing at the same time)
exchange_profiles_refresh_time = 26


# watchlist refresh time in days
# stocks in watchlist are force refreshed if older than this
all_index_watchlist_refresh_time = 14

# watchlist min market cap in USD
all_index_watchlist_min_market_cap = 10_000_000  # todo currency conversion?

# watchlist min trade volume
all_index_watchlist_min_trade_volume = 100_000
