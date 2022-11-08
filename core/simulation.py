from .dataset import EndOfTime
from .portfolio import Portfolio

class NotAllowed(BaseException): pass

class Trader:
    
    def __init__(self):
        self.portfolio = Portfolio()
        self.cash = 0
        self.market = None

        self.fee = 0
        self.dataset = None

        self._buys = 0
        self._sells = 0

    def step(self, timepoint):
        pass

class Simulation:

    def __init__(self, dataset, trader, trade_fee):
        self.dataset = dataset
        self.trader = trader
        self.trade_fee = trade_fee

        self.trader.fee = trade_fee
        self.trader.dataset = dataset

        self._current_time = None

    def buy(self, ticker, amount):
        price = self.dataset.sample(ticker, self._current_time).price
        cost = (price * amount) + self.trade_fee
        if cost > self.trader.cash:
            raise NotAllowed()

        self.trader._buys += 1
        self.trader.cash -= cost        
        self.trader.portfolio.update("buy", ticker, amount, price)

    def sell(self, ticker, amount):
        self.trader.portfolio.update("sell", ticker, amount)

        value = (
            (self.dataset.sample(ticker, self._current_time).price * amount) -
            self.trade_fee
        )

        self.trader._sells += 1
        self.trader.cash += value

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

        final_value = self.trader.cash + self.trader.portfolio.value(self._current_time, self.dataset)

        print('final value: %.2f'%final_value)
        print('%d buys and %d sells'%(self.trader._buys, self.trader._sells))
