from .dataset import EndOfTime

class NotAllowed(BaseException): pass

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
