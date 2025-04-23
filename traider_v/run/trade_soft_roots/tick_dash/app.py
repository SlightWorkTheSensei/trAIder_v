from flask import Flask, render_template, jsonify
import pandas as pd
import subprocess
import os

app = Flask(__name__)

def load_market_data(market):
    csv_file = f'data/{market}_data.csv'
    # Check if the CSV file exists and is not empty
    if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
        print(f"{csv_file} does not exist or is empty. Fetching data...")
        # Fetch data by running update_data.py
        subprocess.run(['python', 'update_data.py'], check=True)
    try:
        df = pd.read_csv(csv_file)
        data = df.to_dict(orient='records')
    except pd.errors.EmptyDataError:
        print(f"{csv_file} is empty after attempting to fetch data.")
        data = []
    return data

@app.route('/')
def index():
    markets = ['stocks', 'futures', 'crypto', 'forex']
    market_data = {}
    for market in markets:
        market_data[market] = load_market_data(market)
    return render_template('index.html', market_data=market_data)

@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    subprocess.run(['python', 'update_data.py'], check=True)
    markets = ['stocks', 'futures', 'crypto', 'forex']
    market_data = {}
    for market in markets:
        market_data[market] = load_market_data(market)
    return jsonify(market_data=market_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 4545)
