# CSV format: Date,Open,High,Low,Close,Adj Close,Volume
# All np array are listed from earlist to latest.
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import time
import datetime
import requests
import operator
import os
import os.path
from pandas.tseries.offsets import BDay
matplotlib.use('TkAgg')

api_key = 'XXX'

# CSV_URL = 'https://query1.finance.yahoo.com/v7/finance/download/PDD?period1=1532563200&period2=1593561600&interval=1d&events=history'
whales = ['BABA', 'INTC', 'TM', 'WMT', 'FB', 'BA', 'AAPL', 'AMD', 'AMZN', 'GOOG', 'HD', 'MSFT', 'NVDA', 'QCOM', 'TSLA', 'BAC', 'BRK-B', 'MCD', 'TWTR', 
    'MKSI', 'TSM', 'NFLX', 'BIG', 'XOM', 'LAZR', ]
sharks = ['PDD', 'LI', 'NIO', 'JD',]
others = ['XLE', 'XLF', 'QQQ', 'VIG', 'T', 'RDFN', 'SMH', 'USD']
weekday = sharks + whales 
weekend = others

def data_update(stock_name):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&outputsize=full&apikey={}&datatype=csv'.format(
        stock_name, api_key)
    r = requests.get(url, allow_redirects=True)
    if not os.path.exists('intraday_1min_{}.csv'.format(stock_name)):
        open('intraday_1min_{}.csv'.format(stock_name), 'wb').write(r.content)
    else:
        open('tmp.csv', 'wb').write(r.content)
        existingquotes = pd.read_csv('intraday_1min_{}.csv'.format(stock_name))
        newquotes = pd.read_csv('tmp.csv')
        full_quotes = pd.concat([newquotes, existingquotes])
        full_quotes = full_quotes.drop_duplicates(
            subset=['timestamp'], keep='first')
        full_quotes = full_quotes.sort_values(by=['timestamp'], ascending=False)

        full_quotes.to_csv('intraday_1min_{}.csv'.format(stock_name), index=False)
        os.remove('tmp.csv')
    # alphavantage allows up to 5 API requests per minute and 500 requests per day
    time.sleep(12)

def dome_follower(stock_name, day_num, display = True):
    df = pd.read_csv('intraday_1min_{}.csv'.format(stock_name), index_col=0, parse_dates=True)
    end_time = df.index[0].date() + BDay(1)
    start_time = end_time - BDay(day_num)
    recent_days = pd.bdate_range(start=start_time, end=end_time, freq='T')
    recent_df = df[df.index.isin(recent_days)]
    index = np.flip(range(recent_df['close'].size))
    model = np.poly1d(np.polyfit(index, recent_df['close'], 2, w=recent_df['volume']))

    center = -model[1] / (2 * model[2])  # y = a*x*x + b*x + c, center = -b/2a

    if (center > 0.8 * recent_df['close'].size and center < 1.2 * recent_df['close'].size):
        print(stock_name, model[2] * recent_df['close'].size * recent_df['close'].size, int(center))

        if display:
            plt.close()
            plt.title(stock_name)
            plt.scatter(index, recent_df['close'])
            polyline = np.linspace(recent_df['close'].size, 0, recent_df['close'].size)
            plt.plot(polyline, model(polyline))
            plt.axvline(x=center, color='r')
            plt.show()

if __name__ == '__main__':
    for stock_name in weekday:
        data_update(stock_name)

    for stock_name in weekday:
        dome_follower(stock_name, 20, False)
