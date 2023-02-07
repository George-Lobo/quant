import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import datetime as dt
import yfinance as yfin
from pandas_datareader import data as pdr
from statsmodels.tsa.stattools import adfuller

pd.options.mode.chained_assignment = None

def get_todays_datetime():
    return dt.datetime(year=dt.datetime.now().year, month=dt.datetime.now().month, day=dt.datetime.now().day)


def download_stocks_data(tickers=None,
                         start_time=dt.datetime(year=2015, month=1, day=1),
                         end_time=dt.datetime.now() + dt.timedelta(days=1),
                         update_all=False):

    if not tickers:
        tickers = list(pd.read_csv('high_volume_tickers.csv')['Symbol'])

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


# this function uses the adjusted close price; positive_corr=True returns positively correlated stock pairs, False
# returns negatively correlated stock pairs
def get_correlation_list(start_date=dt.datetime(year=2015, month=1, day=1), end_date=dt.datetime.now(),
                         abs_corr_coef=0.95, positive_corr=True):

    df1 = pd.read_csv('500_stocks_data.csv', parse_dates=['Date'])
    df = df1[(df1['Date'] >= start_date) & (df1['Date'] <= end_date)]

    columns_of_interest = [i for i in df.columns if 'Adj_Close' in i]
    data = df[columns_of_interest]
    data_corr = data.corr()

    if positive_corr:
        high_corr_data = data_corr[data_corr >= abs_corr_coef].dropna(thresh=2, axis=1)

    else:
        high_corr_data = data_corr[data_corr <= -abs_corr_coef].dropna(thresh=1, axis=1)

    pairs_list = []
    reduced_pairs_list = []

    for each_column in high_corr_data.columns:

        current_ticker = each_column.replace('Adj_Close_', '')
        correlated_columns = high_corr_data[each_column][(high_corr_data[each_column].isnull() == False)].index

        if positive_corr:
            correlated_stocks = correlated_columns.str.replace('Adj_Close_', '').drop(current_ticker)

        else:
            correlated_stocks = correlated_columns.str.replace('Adj_Close_', '')

        pairs_list += [(current_ticker, i) for i in correlated_stocks]
        reduced_pairs_list += [(current_ticker, i) for i in correlated_stocks
                               if (i, current_ticker) not in reduced_pairs_list]

    return reduced_pairs_list


# only uses the Augmented Dickey-Fuller test
def check_stationarity(time_series, alpha=0.05):

    adf_results = adfuller(time_series)

    if adf_results[1] > alpha:
        return False

    else:
        return True


# returns the z_scores, not the actual values
def construct_pair_df(ticker1, ticker2, start_date=dt.datetime(year=2015, month=1, day=1),
                      date_to_consider=get_todays_datetime(), path='tickers_data', positive_corr=True, alpha=0.05):

    df1 = get_returns(ticker1, path)
    df2 = get_returns(ticker2, path)
    df = df1[(df1['Date'] >= start_date) &
             (df1['Date'] <= date_to_consider)].merge(df2[(df2['Date'] >= start_date) &
                                                          (df2['Date'] <= date_to_consider)], how='inner', on='Date')

    stationary_columns = []
    if positive_corr:

        df['diff_returns'] = df[f'return_{ticker1}'] - df[f'return_{ticker2}']
        df['diff_prices'] = df[f'Adj_Close_{ticker1}'] - df[f'Adj_Close_{ticker2}']

        df.dropna(axis=0, inplace=True)

        if not check_stationarity(time_series=df['diff_returns'], alpha=alpha):
            df.drop('diff_returns', axis=1, inplace=True)

        else:
            p_value = adfuller(df["diff_returns"])[1]
            df['diff_returns_z_score'] = (df['diff_returns'] - df['diff_returns'].mean()) / df['diff_returns'].std()
            stationary_columns.append('diff_returns_z_score')

        if not check_stationarity(time_series=df['diff_prices'], alpha=alpha):
            df.drop('diff_prices', axis=1, inplace=True)

        else:
            p_value = adfuller(df["diff_prices"])[1]
            df['diff_prices_z_score'] = (df['diff_prices'] - df['diff_prices'].mean()) / df['diff_prices'].std()
            stationary_columns.append('diff_prices_z_score')

    else:

        df['sum_returns'] = df[f'return_{ticker1}'] + df[f'return_{ticker2}']
        df['sum_prices'] = df[f'Adj_Close_{ticker1}'] + df[f'Adj_Close_{ticker2}']

        df.dropna(axis=0, inplace=True)

        if not check_stationarity(time_series=df['sum_returns'], alpha=alpha):
            df.drop('sum_returns', axis=1, inplace=True)

        else:
            p_value = adfuller(df["sum_returns"])[1]
            df['sum_returns_z_score'] = (df['sum_returns'] - df['sum_returns'].mean()) / df['sum_returns'].std()
            stationary_columns.append('sum_returns_z_score')

        if not check_stationarity(time_series=df['sum_prices'], alpha=alpha):
            df.drop('sum_prices', axis=1, inplace=True)

        else:
            p_value = adfuller(df["sum_prices"])[1]
            df['sum_prices_z_score'] = (df['sum_prices'] - df['sum_prices'].mean()) / df['sum_prices'].std()
            stationary_columns.append('sum_prices_z_score')

    return df[['Date'] + stationary_columns].sort_values('Date', ascending=False)


# should not work as the price itself is not stationary
def get_returns(ticker, path='tickers_data'):

    df = pd.read_csv(f'{path}/{ticker}_data.csv', parse_dates=['Date'])
    df[f'return_{ticker}'] = df[f'Adj_Close_{ticker}'].diff()/df[f'Adj_Close_{ticker}'].shift(1)

    return df.loc[1:,['Date',f'Adj_Close_{ticker}', f'return_{ticker}']]


def check_arbitrage_opps(initial_date=dt.datetime(year=2015, month=1, day=1), date_to_consider=get_todays_datetime(),
                         z_score_threshold=2.5):

    positively_corr_list = get_correlation_list(start_date=initial_date, end_date=date_to_consider, positive_corr=True)
    positively_corr_opps = {str(initial_date) + '---' + str(date_to_consider): []}
    negatively_corr_list = get_correlation_list(start_date=initial_date, end_date=date_to_consider, positive_corr=False)
    negatively_corr_opps = {str(initial_date) + '---' + str(date_to_consider): []}

    for each_pair in tqdm(positively_corr_list):

        current_pair_df = construct_pair_df(ticker1=each_pair[0], ticker2=each_pair[1], start_date=initial_date,
                                            date_to_consider=date_to_consider, positive_corr=True)

        if current_pair_df.shape[1] > 1:

            columns_of_interest = [i for i in current_pair_df.columns if 'z_score' in i]
            for each_column in columns_of_interest:

                position = current_pair_df.index[current_pair_df['Date'] == date_to_consider]
                if abs(current_pair_df.loc[position, each_column].item()) >= z_score_threshold:

                    positively_corr_opps[str(initial_date) + '---' + str(date_to_consider)].append((each_pair, each_column))


    for each_pair in tqdm(negatively_corr_list):

        current_pair_df = construct_pair_df(ticker1=each_pair[0], ticker2=each_pair[1], start_date=initial_date,
                                            date_to_consider=date_to_consider, positive_corr=False)

        if current_pair_df.shape[1] > 1:

            columns_of_interest = [i for i in current_pair_df.columns if 'z_score' in i]
            for each_column in columns_of_interest:

                position = current_pair_df.index[current_pair_df['Date'] == date_to_consider]
                if abs(current_pair_df.loc[position, each_column].item()) >= z_score_threshold:

                    negatively_corr_opps[str(initial_date) + '---' + str(date_to_consider)].append((each_pair, each_column))

    with open('positively_corr_opps.txt', 'a') as data1:
        data1.write(str(positively_corr_opps))

    with open('negatively_corr_opps.txt', 'a') as data2:
        data2.write(str(negatively_corr_opps))

    return positively_corr_opps, negatively_corr_opps


if __name__ == '__main__':
    #corr_tuple = get_correlation_list()[0]
    #print(construct_pair_df(corr_tuple[0], corr_tuple[1]).head())

    test1, test2 = check_arbitrage_opps(initial_date=dt.datetime(year=2022, month=7, day=1),
                                        date_to_consider=get_todays_datetime() - dt.timedelta(days=1))
    print(test1)
    print(test2)


