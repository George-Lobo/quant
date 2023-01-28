import os
import pandas as pd
from tqdm import tqdm
import datetime as dt
import yfinance as yfin
from pandas_datareader import data as pdr


def download_stocks_data(tickers=None, start_time=None, end_time=None, update_all=False):

    if not tickers:
        tickers = list(pd.read_csv('high_volume_tickers.csv')['Symbol'])

    if not end_time:
        current_date = dt.datetime.now() + dt.timedelta(days=1)
        end_time = current_date

    if not start_time:
        start_time = dt.datetime(year=2015, month=1, day=1)

    # need this because apparently pandas_datareader changed a bit
    yfin.pdr_override()

    df = pdr.get_data_yahoo(tickers, start_time, end_time)

    # flattening the MultiIndex and replacing whitespaces with underscores
    columns1 = [' '.join(col).strip() for col in df.columns.values]
    df.columns = [i.replace(' ', '_') for i in columns1]
    df.index = pd.to_datetime(df.index).tz_localize(None)

    # saving all data into a single file
    if update_all:
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

    print(f'Added data from {start_time} to {end_time}.')

# build this in the future if not possible anymore to retrieve all data in a single request
def update_stocks_data():

    pass


def get_correlation_list(start_date=dt.datetime(year=2015, month=1, day=1), end_date=dt.datetime.now()):

    df1 = pd.read_csv('500_stocks_data.csv', parse_dates=['Date'])
    df = df1[(df1['Date'] >= start_date) & (df1['Date'] <= end_date)]

    columns_of_interest = [i for i in df.columns if 'Adj_Close' in i]
    data = df[columns_of_interest]
    data_corr = data.corr()
    high_corr_data = data_corr[data_corr.abs() > 0.95].dropna(thresh=2, axis=1)

    pairs_list = []
    reduced_pairs_list = []

    for each_column in high_corr_data.columns:
        current_ticker = each_column.replace('Adj_Close_', '')
        correlated_columns = high_corr_data[each_column][(high_corr_data[each_column].isnull() == False)].index
        correlated_stocks = correlated_columns.str.replace('Adj_Close_', '').drop(current_ticker)

        pairs_list += [(current_ticker, i) for i in correlated_stocks]
        reduced_pairs_list += [(current_ticker, i) for i in correlated_stocks
                               if (i, current_ticker) not in reduced_pairs_list]

    return reduced_pairs_list


if __name__ == '__main__':
    print(len(get_correlation_list()))