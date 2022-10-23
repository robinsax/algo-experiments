import pandas as pd
import json

dataset = pd.read_csv('sp500_stocks.csv')

per_co = dict()

print(dataset.head())

for _, datum in dataset.iterrows():
    sym = datum[1]
    if sym not in per_co:
        per_co[sym] = list()

    per_co[sym].append({
        'd': datum[0],
        'adj_c': datum[2],
        'c': datum[3],
        'h': datum[4],
        'l': datum[5],
        'o': datum[6],
        'v': datum[7]
    })

for key in per_co:
    fh = open('ds/%s.json'%key, 'w')
    json.dump(per_co[key], fh)
    fh.close()
