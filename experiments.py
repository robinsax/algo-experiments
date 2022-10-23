import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from algoexperiments import Dataset, Trader, NotAllowed, InvalidSample, Simulation

dataset = Dataset()

class Chaos(Trader):

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

simulation = Simulation(dataset, Chaos(), 1)
simulation.run(1000)
