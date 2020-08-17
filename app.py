from flask import Flask, render_template ,request
from patterns import candlestick_patterns
import yfinance as yf 
from datetime import date
import pandas as pd
import os
import glob
import talib
import csv
import numpy as np

app = Flask(__name__)
intervals = ["1m","2m","5m","15m","30m","60m","90m","1h","1d","5d","1wk","1mo","3mo"]
@app.route('/')
def index():
    pattern = request.args.get('pattern',None)
    stocks = {}

    with open('datasets/companies.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}
    if(pattern):
        datafiles = os.listdir("datasets/daily")
        for fname in datafiles:
            df = pd.read_csv("datasets/daily/{}".format(fname))
            # df= pd.DataFrame(data = df, dtype=np.float64)
            # print(df)
            # for pattern in candlestick_patterns:
            print("----------- {} ----------".format(pattern))
            pattern_function = getattr(talib, pattern)
            symbol = fname.split('.')[0]

            
            open_ = df['Open'].astype('float64').to_numpy()
            high = df['High'].astype('float64').to_numpy()
            low = df['Low'].astype('float64').to_numpy()
            close = df['Close'].astype('float64').to_numpy()          

            try:
                results = pattern_function(open_,high,low,close)
                # results = pattern_function(df['Open'],df['High'],df['Low'],df['Close'])
                print("res",results)
                # last = results.tail(1).values[0]
                last = results[0]
                print("last",last)

                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                    break
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                    break
                else:
                    stocks[symbol][pattern] = None
            except Exception as e:
                print('failed on filename: ', fname, "Error: ",e)
                 

    return render_template("index.html",candlestick_patterns=candlestick_patterns,stocks=stocks, pattern=pattern,interval_dict=intervals)


@app.route('/snapshot')
def snapshot():
    files = glob.glob('datasets/daily/*')
    interval = request.args.get('interval',None)    
    if(not interval): interval = "1h"
    print("Interval ", interval)

    for f in files:
        os.remove(f)
        print("Removed",f)
    with open("datasets/companies.csv") as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]

            filePath = 'datasets/daily/{}.csv'.format(symbol)
            # if(not os.path.isfile(filePath)):
            
            df = yf.download(symbol,start="2020-01-01",end=date.today().strftime("%Y-%m-%d"),interval=interval)
             
            # df = yf.download(symbol,start="2020-01-01",end="2020-08-01")
            df.to_csv(filePath)
            
    return render_template("index.html",candlestick_patterns=candlestick_patterns, interval_dict=intervals)
    # return {
    #     "code" : "success"
    # }