from flask import Flask, render_template, request
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import pandas as pd

app = Flask(__name__)

def generate_candlestick_chart(ticker_data):
    # Ensure data integrity
    ticker_data = ticker_data.copy()
    ticker_data.dropna(subset=['Open', 'Close', 'Volume'], inplace=True)

    # Convert required columns to numeric
    numeric_columns = ['Open', 'Close', 'Volume']
    ticker_data[numeric_columns] = ticker_data[numeric_columns].apply(pd.to_numeric, errors='coerce')
    ticker_data.dropna(subset=numeric_columns, inplace=True)

    # Convert index to datetime
    ticker_data.index = pd.to_datetime(ticker_data.index)

    # Proceed only if there is data
    if ticker_data.empty:
        return None

    fig, ax = plt.subplots(3, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    plt.subplots_adjust(hspace=0.05)
    ax_price = ax[0]
    ax_volume = ax[1]
    ax_trend = ax[2]
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax_trend.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Plot candlesticks
    ax_price.plot(ticker_data.index, ticker_data['Close'], color='black', label='Close Price')
    ax_price.fill_between(
        ticker_data.index,
        ticker_data['Open'],
        ticker_data['Close'],
        where=(ticker_data['Close'] >= ticker_data['Open']),
        color='green',
        alpha=0.5
    )
    ax_price.fill_between(
        ticker_data.index,
        ticker_data['Open'],
        ticker_data['Close'],
        where=(ticker_data['Close'] < ticker_data['Open']),
        color='red',
        alpha=0.5
    )
    ax_price.legend()

    # Plot volume bars
    volume_color = ['red' if ticker_data['Close'].iloc[i] < ticker_data['Open'].iloc[i] else 'green' for i in range(len(ticker_data))]
    ax_volume.bar(ticker_data.index, ticker_data['Volume'], color=volume_color, alpha=0.5)

    # Plot trend intervals
    trend_intervals = []
    trend_start = None
    for i in range(1, len(ticker_data)):
        current_up = ticker_data['Close'].iloc[i] >= ticker_data['Open'].iloc[i]
        previous_up = ticker_data['Close'].iloc[i-1] >= ticker_data['Open'].iloc[i-1]
        if current_up == previous_up:
            if trend_start is None:
                trend_start = ticker_data.index[i-1]
        else:
            if trend_start is not None:
                trend_end = ticker_data.index[i-1]
                color = 'green' if previous_up else 'red'
                trend_intervals.append((trend_start, trend_end, color))
                trend_start = None
    if trend_start is not None:
        trend_end = ticker_data.index[-1]
        color = 'green' if ticker_data['Close'].iloc[-1] >= ticker_data['Open'].iloc[-1] else 'red'
        trend_intervals.append((trend_start, trend_end, color))

    for interval in trend_intervals:
        xmin = mdates.date2num(interval[0])
        xmax = mdates.date2num(interval[1])
        ax_trend.axvspan(xmin=xmin, xmax=xmax, color=interval[2], alpha=0.3)

    # Remove x-axis labels from price and volume charts
    ax_price.set_xticklabels([])
    ax_volume.set_xticklabels([])

    # Save candlestick chart to bytes
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return plot_data

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    plot_data = None
    ticker_symbol = "TSLA"  # Default ticker symbol

    if request.method == 'POST':
        ticker_symbol = request.form['ticker'].upper()

    # Fetch data for the provided ticker symbol
    ticker = yf.Ticker(ticker_symbol)
    ticker_data = ticker.history(period="1mo")

    if ticker_data.empty:
        error = f"No data available for ticker symbol '{ticker_symbol}'. Please try a different symbol."
    else:
        plot_data = generate_candlestick_chart(ticker_data)
        if plot_data is None:
            error = "An error occurred while generating the chart. Please try again."

    return render_template('index.html', plot_data=plot_data, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6067)
