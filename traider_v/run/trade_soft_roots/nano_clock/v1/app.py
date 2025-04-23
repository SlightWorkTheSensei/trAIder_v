from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# List of ticker symbols and corresponding countries for various indexes
tickers = [
    {'symbol': '^FTSE', 'country': 'United Kingdom'},
    {'symbol': '^GDAXI', 'country': 'Germany'},
    {'symbol': '^FCHI', 'country': 'France'},
    {'symbol': '^N225', 'country': 'Japan'},
    {'symbol': '^HSI', 'country': 'Hong Kong'},
    {'symbol': '000001.SS', 'country': 'China'},
    {'symbol': '^GSPTSE', 'country': 'Canada'},
    {'symbol': '^BVSP', 'country': 'Brazil'},
    {'symbol': '^BSESN', 'country': 'India'},
    {'symbol': '^AXJO', 'country': 'Australia'},
    {'symbol': '^STOXX50E', 'country': 'Eurozone'},
    {'symbol': 'SPY', 'country': 'United States (New York)'},  # SPY for New York
    {'symbol': 'MNQ=F', 'country': 'United States (Chicago)'}  # MNQ for Chicago (Nasdaq futures)
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Create an empty list to store the data
    data_list = []

    # Loop over each ticker to fetch today's data
    for ticker_info in tickers:
        ticker = yf.Ticker(ticker_info['symbol'])
        today_data = ticker.history(period="1d")

        if not today_data.empty:
            current_price = today_data['Close'][0]
            open_price = today_data['Open'][0]
            price_change = current_price - open_price

            # Check if the open price is not zero before calculating percentage change
            if open_price != 0:
                price_change_percent = (price_change / open_price) * 100
            else:
                price_change_percent = 0  # Set to 0 if open_price is 0 to avoid division by zero

            volume = today_data['Volume'][0]

            # Collect data in the list
            data_list.append({
                'Ticker': ticker_info['symbol'],
                'Country': ticker_info['country'],
                'Current Price': current_price,
                'Price Change': price_change,
                'Percentage Change': price_change_percent,
                'Volume': volume
            })

    # Convert the list to a DataFrame
    price_data = pd.DataFrame(data_list)

    # Return the data as JSON
    return jsonify(price_data.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 3636)
