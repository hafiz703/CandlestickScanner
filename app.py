from flask import Flask, render_template ,request
from patterns import candlestick_patterns
import yfinance as yf 
from datetime import date
import pandas as pd
import os
import talib
import csv

app = Flask(__name__)

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
            # print(df)
            pattern_function = getattr(talib, pattern)
            symbol = fname.split('.')[0]

            
            open_ = df['Open'].astype('float64').to_numpy()
            high = df['High'].astype('float64').to_numpy()
            low = df['Low'].astype('float64').to_numpy()
            close = df['Close'].astype('float64').to_numpy()          

            try:
                results = pattern_function(open_,high,low,close)
                # results = pattern_function(df['Open'],df['High'],df['Low'],df['Close'])
                print("res ",results)
                last = results[0]

                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
            except Exception as e:
                print('failed on filename: ', fname, "Error: ",e)
                 

    return render_template("index.html",candlestick_patterns=candlestick_patterns,stocks=stocks, pattern=pattern)


@app.route('/snapshot')
def snapshot():
    with open("datasets/companies.csv") as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]

            filePath = 'datasets/daily/{}.csv'.format(symbol)
            # if(not os.path.isfile(filePath)):
            df = yf.download(symbol,start="2020-01-01",end=date.today().strftime("%Y-%m-%d"))
            df.to_csv(filePath)

    return {
        "code" : "success"
    }