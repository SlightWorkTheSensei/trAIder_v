from flask import Flask, render_template, request
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import base64
from io import BytesIO

app = Flask(__name__)

def calculate_support_resistance(prices):
    # Calculate 10-day moving averages for Low and High prices
    ma_low = prices['Low'].rolling(window=10).mean()
    ma_high = prices['High'].rolling(window=10).mean()

    # Identify support and resistance levels
    support_levels = ma_low.dropna()
    resistance_levels = ma_high.dropna()

    return support_levels, resistance_levels

def plot_support_resistance(prices, support_levels, resistance_levels, ticker_symbol, timeframe):
    # Plot candlestick chart
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(prices.index, prices['Close'], color='black')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f' {ticker_symbol} ({timeframe})')

    # Plot support levels
    plt.plot(support_levels.index, support_levels, color='green', linestyle='--', label='Support')

    # Plot resistance levels
    plt.plot(resistance_levels.index, resistance_levels, color='red', linestyle='--', label='Resistance')

    # Mark crossover points
    support_crosses = {}
    resistance_crosses = {}
    for date, price in prices.iterrows():
        if date in support_levels.index and price['Close'] > support_levels.loc[date]:
            plt.scatter(date, price['Close'], color='green', marker='^', s=100)
            support_crosses[date] = True
        else:
            support_crosses[date] = False

        if date in resistance_levels.index and price['Close'] < resistance_levels.loc[date]:
            plt.scatter(date, price['Close'], color='red', marker='v', s=100)
            resistance_crosses[date] = True
        else:
            resistance_crosses[date] = False

    # Only include necessary items in the legend
    plt.legend(['Close', 'Support', 'Resistance', 'Support Cross', 'Resistance Cross'])

    # Calculate probability of reversal based on consecutive crosses
    def calculate_probability(crosses):
        lengths = []
        current_length = 0
        for date in crosses:
            if crosses[date]:
                current_length += 1
            else:
                if current_length > 0:
                    lengths.append(current_length)
                    current_length = 0
        if current_length > 0:
            lengths.append(current_length)

        probabilities = {}
        for length in lengths:
            probabilities[length] = lengths.count(length) / len(lengths)
        return probabilities

    # Plot probability of reversal based on consecutive crosses
    plt.subplot(2, 1, 2)
    support_probabilities = calculate_probability(support_crosses)
    resistance_probabilities = calculate_probability(resistance_crosses)
    
    plt.bar(support_probabilities.keys(), support_probabilities.values(), color='green', alpha=0.7, label='Support Probability')
    plt.bar(resistance_probabilities.keys(), resistance_probabilities.values(), color='red', alpha=0.7, label='Resistance Probability')
    
    plt.xlabel('Consecutive Crosses')
    plt.ylabel('Probability of Reversal')
    plt.title('Probability of Reversal based on Consecutive Crosses')
    plt.legend()
    
    plt.tight_layout()

    # Convert plot to base64 encoding
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return plot_image

def get_support_resistance(ticker_symbol, timeframe):
    try:
        # Calculate start and end dates based on the selected timeframe
        # Calculate start and end dates based on the selected timeframe
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        if timeframe == '1m':
            start_date = (datetime.now() - timedelta(minutes=120)).strftime('%Y-%m-%d')
        elif timeframe == '15m':
            start_date = (datetime.now() - timedelta(minutes=30*120)).strftime('%Y-%m-%d')
        elif timeframe == '60m':
            start_date = (datetime.now() - timedelta(hours=120)).strftime('%Y-%m-%d')
        elif timeframe == '1d':
            start_date = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')
        elif timeframe == '1mo':
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif timeframe == '3mo':
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        elif timeframe == '6mo':
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        elif timeframe == '1y':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif timeframe == '2y':
            start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
        elif timeframe == '5y':
            start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        else:
            start_date = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')


        # Fetch historical data
        prices = yf.download(ticker_symbol, start=start_date, end=end_date)

        # Calculate support and resistance levels
        support_levels, resistance_levels = calculate_support_resistance(prices)

        # Plot support and resistance levels
        plot_image = plot_support_resistance(prices, support_levels, resistance_levels, ticker_symbol, timeframe)

        return plot_image

    except Exception as e:
        print("Error:", e)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker_symbol = request.form['ticker_symbol']
        timeframe = request.form['timeframe']
        plot_image = get_support_resistance(ticker_symbol, timeframe)
        return render_template('index.html', plot_image=plot_image)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8889)
