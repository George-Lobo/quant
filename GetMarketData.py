import os
import pandas as pd
from tqdm import tqdm
import datetime as dt
import yfinance as yfin
from pandas_datareader import data as pdr

# need this because apparently pandas_datareader changed a bit
yfin.pdr_override()

current_date = dt.datetime.now() + dt.timedelta(days=1)

end_time = current_date
start_time = dt.datetime(year=2015, month=1, day=1)

tickers = list(pd.read_csv('high_volume_tickers.csv')['Symbol'])

df = pdr.get_data_yahoo(tickers, start_time, end_time)

# flattening the MultiIndex and replacing whitespaces with underscores
columns1 = [' '.join(col).strip() for col in df.columns.values]
df.columns = [i.replace(' ', '_') for i in columns1]

# saving all data into a single file
df.to_csv('500_stocks_data.csv')

# saving each stock separately to a new directory
path = 'tickers_data'

path_exists = os.path.exists('tickers_data')

column_titles = ['Open_', 'High_', 'Low_', 'Close_', 'Adj_Close_', 'Volume_']

if not path_exists:

    os.makedirs(path)

for each_ticker in tqdm(tickers):

    column_names = [i + each_ticker for i in column_titles]

    temp_df = df[column_names]

    current_ticker = each_ticker.replace('/', '-')

    temp_df.to_csv(f'{path}/{current_ticker}_data.csv')