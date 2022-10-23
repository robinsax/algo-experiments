import json
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime, timedelta

class EndOfTime(BaseException): pass
class NotAllowed(BaseException): pass
class InvalidSample(BaseException): pass

class Timepoint:

    def __init__(self, dataset, date_str, start):
        parts = date_str.split('-')

        self.dataset = dataset
        self.start = start
        self.when = datetime(
            int(parts[0]),
            int(parts[1]),
            int(parts[2])
        )

    def __add__(self, steps):
        day_step = 1 if steps > 0 else -1
        when = self.when
        start = self.start
        for i in range(abs(steps)):
            if start:
                start = False
            else:
                start = True
                when += timedelta(days=day_step)
                if str(when.date()) == self.dataset.last_day:
                    raise EndOfTime()
                while str(when.date()) not in self.dataset.open_days:
                    when += timedelta(days=day_step)

        return Timepoint(self.dataset, str(when.date()), start)

    def date(self):
        return self.when.strftime('%Y-%m-%d')

    def __str__(self):
        return '%s %s'%(self.date(), 'open' if self.start else 'close')

class Datapoint:

    def __init__(self, ticker, datum, timepoint):
        self.ticker = ticker
        self.timepoint = timepoint
        self._datum = datum
        
    @property
    def price(self):
        return self._datum['o' if self.timepoint.start else 'c']

    @property
    def volume(self):
        return 0 if self.timepoint.start else self._datum['v']

    def __str__(self):
        return '%s, price: %s, volume: %s'%(
            self.timepoint, self.price, self.volume
        )

class Datapoints(list):

    @property
    def prices(self):
        return list(sample.price for sample in self)

    def __str__(self):
        return '\n'.join(list(str(item) for item in self))

class Dataset:

    def __init__(self):
        self.loaded = dict()
        self.open_days = None

        self.tickers = list()
        for fn in os.listdir('ds'):
            self.tickers.append(fn.replace('.json', ''))

        data = self._get_ticker(self.tickers[0])
        self.open_days = dict()
        self.last_day = data[-1]['d']
        self.first_day = None
        for datum in data:
            if not self.first_day:
                self.first_day = datum['d']
            self.open_days[datum['d']] = True

    def _get_ticker(self, ticker):
        if not ticker in self.loaded:
            with open('ds/%s.json'%ticker) as fh:
                self.loaded[ticker] = json.load(fh)        

        return self.loaded[ticker]

    def timepoint(self, date_str, start):
        return Timepoint(self, date_str, start)

    def first_timepoint(self):
        return Timepoint(self, self.first_day, True)

    def sample(self, ticker, timepoint):
        data = self._get_ticker(ticker)

        when = timepoint.date()
        for datum in data:
            if datum['d'] == when:
                if math.isnan(datum['c']):
                    raise InvalidSample()
                return Datapoint(ticker, datum, timepoint)

        return None

class Trader:
    
    def __init__(self):
        self.portfolio = dict()
        self.cash = 0
        self.market = None

        self._buys = 0
        self._sells = 0

    def step(self, timepoint):
        pass

class Simulation:

    def __init__(self, dataset, trader, trade_fee):
        self.dataset = dataset
        self.trader = trader
        self.trade_fee = trade_fee

        self._current_time = None

    def buy(self, ticker, amount):
        cost = (
            (self.dataset.sample(ticker, self._current_time).price * amount) +
            self.trade_fee
        )
        if cost > self.trader.cash:
            raise NotAllowed()

        self.trader._buys += 1
        self.trader.cash -= cost
        self.trader.portfolio[ticker] = amount + self.trader.portfolio.get(ticker, 0)

    def sell(self, ticker, amount):
        if amount > self.trader.portfolio[ticker]:
            raise NotAllowed()
        value = (
            (self.dataset.sample(ticker, self._current_time).price * amount) -
            self.trade_fee
        )

        self.trader._sells += 1
        self.trader.cash += value
        self.trader.portfolio[ticker] -= amount

    def run(self, trader_cash):
        self.trader.cash = trader_cash
        self.trader.market = self

        self._current_time = self.dataset.first_timepoint()

        print('running simulation, initial cash: %.2f'%(trader_cash))
        print('first day: %s'%self._current_time)

        while True:
            try:
                self._current_time += 1
            except EndOfTime:
                break

            self.trader.step(self._current_time)

        print('last day: %s'%self._current_time)

        final_value = self.trader.cash
        for ticker in self.trader.portfolio:
            amount = self.trader.portfolio[ticker]
            if amount > 0:
                value = amount * self.dataset.sample(ticker, self._current_time).price
                final_value += value
                print('holding %d %s, value: %.2f'%(amount, ticker, value))

        print('final value: %.2f'%final_value)
        print('%d buys and %d sells'%(self.trader._buys, self.trader._sells))

dataset = Dataset()

class MyFirstAwesomeTrader(Trader):

    def step(self, timepoint):
        import random

        buy = len(self.portfolio) == 0 or random.choice((True, False))
        ticker_choices = dataset.tickers
        if not buy:
            ticker_choices = list(self.portfolio.keys())

        ticker = ticker_choices[random.randint(0, len(ticker_choices) - 1)]

        try:
            if buy:
                self.market.buy(ticker, 1)
            else:
                self.market.sell(ticker, 1)
        except NotAllowed:
            pass
        except InvalidSample:
            pass

simulation = Simulation(dataset, MyFirstAwesomeTrader(), 1)
simulation.run(1000)

def offset_prices_pairwise_timeseries_df(ticker_a, ticker_b, t_0, t_length, t_offset):
    data = list()
    for i in range(t_length):
        data.append((
            dataset.sample(ticker_a, t_0 + i).price,
            dataset.sample(ticker_b, t_0 + t_offset + i).price
        ))

    return pd.DataFrame(data, columns=(ticker_a, ticker_b))

def offset_prices_timeseries_df(against_ticker, other_tickers, t_0, t_length, t_offset):
    all_tickers = (against_ticker, *other_tickers)
    
    data = list()
    for i in range(t_length):
        row = list()
        for ticker in all_tickers:
            t_sample = t_0 + i
            if ticker != against_ticker:
                t_sample += t_offset

            row.append(dataset.sample(ticker, t_sample).price)
        data.append(row)

    return pd.DataFrame(data, columns=all_tickers)

def stupid_test():
    t_0 = dataset.timepoint('2020-03-02', True)
    t_length = 10

    ticker_a = 'AAPL'
    max_corr = None
    for t_offset in range(5, 10):
        for ticker_b in dataset.tickers:
            if ticker_a == ticker_b:
                continue
            data = offset_prices_pairwise_timeseries_df(ticker_a, ticker_b, t_0, t_length, t_offset)
            corr_df = data.corr(method='pearson')

            corr = corr_df[ticker_a][1]
            if not max_corr or corr > max_corr[1]:
                max_corr = (ticker_b, corr, t_offset)

    print(max_corr)

exit()
data = offset_prices_timeseries_df('MSFT', dataset.tickers[:30], t_0, t_length, t_offset)
corr_df = data.corr(method='pearson')

#take the bottom triangle since it repeats itself
mask = np.zeros_like(corr_df)
mask[np.triu_indices_from(mask)] = True
#generate plot
import seaborn
seaborn.heatmap(
    corr_df, cmap='RdYlGn',
    vmax=1.0, vmin=-1.0,
    mask=mask,
    linewidths=2.5
)
plt.yticks(rotation=0) 
plt.xticks(rotation=90) 
plt.show()
