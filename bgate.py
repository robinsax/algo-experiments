import math

from core import Dataset, Trader, NotAllowed, InvalidSample, BeginningOfTime, Simulation

dataset = Dataset()

TICKER = 'MSFT'

class BGate(Trader):

    def step(self, timepoint):
        if len(self.portfolio.equities) == 0:
            self.market.buy(TICKER, 10)
            return
        
        equity = self.portfolio.get_equity(TICKER)

        try:
            past_week_avg = 0
            for i in range(1,8):
                past_week_avg += self.dataset.sample(TICKER, timepoint-i).price
            past_week_avg = past_week_avg / 7
        except BeginningOfTime:
            return

        curr_bgate_price = self.dataset.sample(TICKER, timepoint).price

        sell_condition = ((curr_bgate_price - self.fee - equity.average_price)/equity.average_price)*100
        buy_condition = ((past_week_avg - self.fee - curr_bgate_price)/curr_bgate_price)*100
        buy_amount = math.floor(self.cash / curr_bgate_price)

        try:
            if sell_condition > 3:
                self.market.sell(TICKER, equity.amount)
            elif buy_condition > 1:
                self.market.buy(TICKER, buy_amount)
            elif buy_condition > 0.5:
                self.market.buy(TICKER, buy_amount/2)
        except NotAllowed:
            pass
        except InvalidSample:
            pass

simulation = Simulation(dataset, BGate(), 0)
simulation.run(10000)