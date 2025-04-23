from flask import Flask, render_template, jsonify
import csv
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    data = read_csv()
    return render_template('movers.html', data=data)

def read_csv():
    data = []
    with open('refreshed_data.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ticker = row['Ticker']
            price = row['Price']
            price_change = row['Price Change']
            percent_change = round(float(row['Price Percent Change']), 3) if 'Price Percent Change' in row else None
            volume = row['Volume']
            avg_volume = round(float(row['avgVolume'].replace(',', '')), 3) if 'avgVolume' in row else None
            current_commitment = round(float(row['CurrentCommitment'].replace(',', '')), 3) if 'CurrentCommitment' in row else None
            if volume is not None:
                volume = volume.replace(',', '')  # Remove commas from volume
            data.append({'ticker': ticker, 'price': price, 'price_change': price_change, 'percent_change': percent_change, 'volume': volume, 'avgVolume': avg_volume, 'currentCommitment': current_commitment})

    return data



@app.route('/refresh-data')
def refresh_data():
    try:
        # Run the fetch_data.py script using subprocess
        subprocess.run(["python", "fetch_data.py"], check=True)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
