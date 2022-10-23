import json
import os
import math

from datetime import datetime, timedelta

class EndOfTime(BaseException): pass
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
