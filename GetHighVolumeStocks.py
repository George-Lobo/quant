import pandas as pd

# the aim of this script is simply to generate a list with the 500 most traded tickers in a random day (Jan 22 2023)
# this is a placeholder method until we're able to get data that updates this at least once per month.

# source: https://www.nasdaq.com/market-activity/stocks/screener; Jan 22 2023
# filters: medium, large and mega caps in the United States

data = pd.read_csv('nasdaq_screener_1674425615978.csv')

# choosing only the 500 stocks with the most traded volume
volume_df = data.sort_values('Volume', ascending=False)[:500]
tickers = volume_df['Symbol']

tickers.to_csv('high_volume_tickers.csv')