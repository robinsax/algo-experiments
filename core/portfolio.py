class NotAllowed(BaseException): pass

class Equity:
    
    def __init__(self, ticker, amount, price):
        self.ticker = ticker
        self.amount = amount
        self.average_price = price

    def update(self, action, amount, price=None):
        if action == "buy":
            self.compute_average_price(amount, price)
            self.amount += amount

        elif action == "sell":
            if amount > self.amount:
                raise NotAllowed()
            self.amount -= amount

        else:
            raise NotAllowed()

    def compute_average_price(self, amount, price):
        self.average_price = ((self.average_price * self.amount)+(price * amount))/(self.amount+amount)

class Portfolio:

    def __init__(self, equities=[]):
        self.equities = equities

    def get_equity(self, ticker):
        for equity in self.equities:
            if equity.ticker == ticker:
                return equity
        
        return None

    def get_holdings(self):
        return [equity.ticker for equity in self.equities]

    def update(self, action, ticker, amount, price=None):
        equity = self.get_equity(ticker)

        if not equity and action == "buy":
            self.equities.append(Equity(ticker, amount, price))
        elif equity:
            equity.update(action, amount, price)
            if equity.amount == 0:
                self.equities = [eq for eq in self.equities if eq.ticker != equity.ticker]
        else: 
            raise NotAllowed()

    def value(self, timepoint, dataset):
        value = 0
        for equity in self.equities:
            equity_value = equity.amount * dataset.sample(equity.ticker, timepoint).price
            value += equity_value
            print('holding %d %s, value: %.2f'%(equity.amount, equity.ticker, equity_value))

        return value

    def __str__(self):
        if len(self.equities) == 0:
            return ''

        portfolio = 'portfolio:\n'
        for equity in self.equities:
            portfolio += f'\t{equity.ticker}: {equity.amount} at {equity.average_price} per share\n'
        
        return portfolio