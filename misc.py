### Snippets.

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
