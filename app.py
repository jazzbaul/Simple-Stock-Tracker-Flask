from flask import Flask, render_template, request, redirect, url_for
from yfinance import Ticker, download
import pandas as pd
import matplotlib.pyplot as plt
import csv
from io import BytesIO
import base64

app = Flask(__name__)

def load_stocks():
    try:
        with open('stocks.csv', 'r') as file:
            reader = csv.reader(file)
            stocks = [Ticker(row[0]) for row in reader]
            return stocks
    except FileNotFoundError:
        return []

def save_stocks(stocks):
    with open('stocks.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([[stock.info['symbol']] for stock in stocks])

# Home page
@app.route('/')
def home():
    stocks = load_stocks()
    return render_template('home.html', stocks=stocks)

# Add stocks page
@app.route('/add_stocks', methods=['POST'])
def add_stocks():
    symbols = request.form['symbols']
    new_stocks = [Ticker(symbol) for symbol in symbols.replace(' ', '').split(',')]
    stocks = load_stocks()
    stocks.extend(new_stocks)
    save_stocks(stocks)
    return redirect(url_for('home'))

# Delete stocks page
@app.route('/delete_stocks', methods=['POST'])
def delete_stocks():
    symbols = request.form['symbols']
    delete_stocks = [symbol for symbol in symbols.replace(' ', '').split(',')]
    stocks = load_stocks()
    stocks = [stock for stock in stocks if stock.info['symbol'] not in delete_stocks]
    save_stocks(stocks)
    return redirect(url_for('home'))

# Display stock info page
@app.route('/stock_info/<symbol>')
def stock_info(symbol):
    stock = Ticker(symbol)
    info = stock.info
    return render_template('stock_info.html', info=info)

# Display chart page
@app.route('/chart', methods=['POST'])
def chart():
    symbol = request.form['symbol']
    duration = request.form['duration']
    data = download(symbol, period=duration)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data['Close'])
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('chart.html', plot_url=plot_url)

# Rank stocks page
@app.route('/rank_stocks')
def rank_stocks():
    stocks = load_stocks()
    data = [(stock.info['symbol'], download(stock.info['symbol'], period='5d')['Close'].pct_change().sum()) for stock in stocks]
    data.sort(key=lambda x: x[1], reverse=True)
    return render_template('rank_stocks.html', data=data)

# Top performing stock page
@app.route('/top_performing_stock')
def top_performing_stock():
    stocks = load_stocks()
    data = [(stock.info['symbol'], download(stock.info['symbol'], period='5d')['Close'].pct_change().sum()) for stock in stocks]
    top_stock = max(data, key=lambda x: x[1])
    return render_template('top_performing_stock.html', top_stock=top_stock)

if __name__ == "__main__":
    app.run(debug=True)
