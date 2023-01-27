# TO DOs: get last prices for every asset (need to wait until I get the data); find a way to consider current date as to
# avoid lookahead bias and also control which day the portfolio is in
import os
import pandas as pd
from GetMarketData import download_stocks_data


# parent class of all assets
class Asset:

    def __init__(self, name):
        self.name = name
        # self.current_price =

    def volatility(self):
        pass


class Stock(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.paper_type = 'stock'
        self.path = 'tickers_data'
        self.data = self.load_data()

    def load_data(self):

        path_exists = os.path.exists(f'{self.path}/{self.name}_data.csv')

        # checks if it is necessary to update all data
        if not path_exists:
            download_stocks_data()

        return pd.read_csv(f'{self.path}/{self.name}_data.csv').sort_values('Date', ascending=False)


class Commodity(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.paper_type = 'commodity'


# parent class of all derivatives
# TO DOs: get last prices for every derivative; needs to take into consideration the underlying asset

class Derivative(Asset):

    def __init__(self, name, asset_name):
        super().__init__(asset_name)
        self.name = name
        self.asset_name = asset_name
        # self.current_asset_price = self.current_price
        # self.current_price =


class Option(Derivative):
    def __init__(self, name, asset_name):
        super().__init__(name, asset_name)
        self.paper_type = 'option'


class Future(Derivative):
    def __init__(self, name, asset_name):
        super().__init__(name, asset_name)
        self.paper_type = 'future'


def create_paper(paper_type, name, asset_name=None):

    if paper_type == 'stock':
        return Stock(name)
    elif paper_type == 'commodity':
        return Commodity(name)
    elif paper_type == 'option':
        return Option(name, asset_name)
    elif paper_type == 'future':
        return Future(name, asset_name)
    else:
        print('Paper type not supported')


# portfolio
# TO DOs: risk management methods should be coded here
class Portfolio:

    def __init__(self, initial_date, initial_history=None, initial_cash=1e7):
        self.initial_date = initial_date

        if initial_history is not None:
            self.history = initial_history
            self.initial_history = self.history


        else:
            self.history = pd.DataFrame(data=['cash', 'cash', initial_cash, 1, initial_cash, initial_date, 'starting_portfolio'],
                                        columns=['paper_name', 'paper_type', 'amount', 'price', 'quantity', 'date', 'operation'])
            self.initial_history = self.history

    # needs to store net exposure somewhere
    def buy_paper(self, paper_name, paper_type, quantity, date, underlying_asset_name=None):

        paper = create_paper(paper_type, paper_name, underlying_asset_name)
        paper_row = pd.DataFrame(data=[paper_name, paper_type, paper.current_price * quantity, paper.current_price,
                                       quantity, date, 'buy_order'],
                                 columns=['paper_name', 'paper_type', 'amount', 'price', 'quantity', 'date', 'operation'])
        minus_cash_row = pd.DataFrame(data=['cash', 'cash', -paper.current_price * quantity, 1,
                                            -quantity*(paper.current_price), date, 'buy_order_cash_decrease'],
                                      columns=['paper_name', 'paper_type', 'amount', 'price', 'quantity', 'date', 'operation'])
        self.history = pd.concat([self.history, paper_row, minus_cash_row])

        print(f'Bought {quantity} units of {paper_name}')

    # needs to consider short-selling (margin call) and store net exposure somewhere
    def sell_paper(self, paper_name, paper_type, quantity, date, underlying_asset_name=None):

        paper = create_paper(paper_type, paper_name, underlying_asset_name)
        paper_row = pd.DataFrame(data=[paper_name, paper_type, -paper.current_price * quantity, paper.current_price, -quantity,
                                       date, 'sell_order'],
                                 columns=['paper_name', 'paper_type',  'amount', 'price', 'quantity', 'date', 'operation'])
        plus_cash_row = pd.DataFrame(data=['cash', 'cash', paper.current_price * quantity, 1, paper.current_price * quantity,
                                           date, 'sell_order_cash_increase'],
                                      columns=['paper_name', 'paper_type', 'amount', 'price', 'quantity', 'date', 'operation'])
        self.history = pd.concat([self.history, paper_row, plus_cash_row])

        print(f'Sold {quantity} units of {paper_name}')

    # find a way to calculate correlation of portfolio as a whole
    def get_portfolio_correlation(self):
        pass

    # need to set current date to be used in the portfolio; must remember to update this everyday in the data; maybe
    # also set a time of the day
    def set_current_date(self):
        pass

    # should close positions, based on if the portfolio is long or short on it
    def liquidate_asset(self, paper_name, paper_type, date=None, underlying_asset_name=None):

        if date is None:
            date = self.set_current_date()

        asset_history = self.history[self.history['paper_name'] == paper_name]
        remaining_quantity = asset_history['quantity'].sum()

        if remaining_quantity != 0:

            if remaining_quantity > 0:
                self.sell_paper(paper_name, paper_type, remaining_quantity, date, underlying_asset_name)

            else:
                self.buy_paper(paper_name, paper_type, remaining_quantity, date, underlying_asset_name)

        print(f'Position on asset {paper_name} was closed on {date}.')

    # should return a dictionary in the form {'paper_name': current_price}, so we can use it below for mapping
    def get_current_prices(self, date=None):

        if date is None:
            date = self.set_current_date()

        current_prices_dict = {'cash': 1}
        pass

    # should return net exposure from both buy_paper and sell_paper
    def get_exposure(self):

        aggregate_df = self.history.groupby('paper_name').sum().reset_index(inplace=True)
        open_positions = aggregate_df[aggregate_df['quantity'] != 0]
        open_positions['current_price'] = open_positions['paper_name'].map(self.get_current_prices())
        open_positions['current_amount'] = open_positions['current_price'] * open_positions['quantity']

        return open_positions[['paper_name', 'current_amount']]

    # returns the current value of all assets under management (sum of the column from history)
    def current_aum(self):
        return get_exposure['current_amount'].sum()

    # returns the performance of the portfolio
    def return_to_date(self):
        return self.current_aum() / self.initial_history['amount'].sum()

    # plots the evolution of the AUM
    def plot_evolution(self):
        pass


# strategies; need to consider the start and end dates
# TO DOs: needs to manage risk in decisions (can't just buy everything possible); need to think of long bias strategies
# as we maybe wouldn't need that much cash to run stat arb only; should strategies be functions?
class Strategy:

    def __init__(self, start_date, end_date, all_data):
        self.start_date = start_date
        self.end_date = end_date
        self.all_data = all_data

    def pair_correlation(self, paper1, paper2, period):
        pass

    def pair_statistical_arbitrage(self):
        pass


if __name__ == '__main__':

    t1 = create_paper('stock', 'AAPL')
    print(t1.data.head())