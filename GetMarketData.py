import pandas as pd
import datetime as dt
import yfinance as yfin
from pandas_datareader import data as pdr

yfin.pdr_override()

current_date = dt.datetime.now() + dt.timedelta(days=1)

end_time = current_date
start_time = dt.datetime(year=2015, month=1, day=1)

tickers = list(pd.read_csv('high_volume_tickers.csv')['Symbol'])

df = pdr.get_data_yahoo(tickers, start_time, end_time)

columns1 = [' '.join(col).strip() for col in df.columns.values]
df.columns = [i.replace(' ', '_') for i in columns1]

df.to_csv('500_stocks_data.csv')