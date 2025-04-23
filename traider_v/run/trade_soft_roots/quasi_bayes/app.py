from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify  # Import Flask and helper modules for routing and rendering templates
import os
import re
from modules import a_fetch_data as fetch_data
from modules import b_backtest_parent as backtest_parent
from modules import c_backtest_child as backtest_child
from modules import d_compare as compare
from datetime import datetime

app = Flask(__name__)

STOP_LOSSES = [0.01, 0.02, 0.05, 0.1, 0.25, 0.50, 1, 2.50, 5, 10, 25, 50, 100]
REWARD_RATIOS = [1, 2, 3, 5, 10]
POSITIONS = ['long', 'short']
INTERVALS = [1, 5, 15, 60]

DATA_FOLDER = 'data'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        action = request.form['action']

        if action == 'run_algorithm':
            return redirect(url_for('results', ticker=ticker, run_algorithm=True))
        elif action == 'view_latest':
            return redirect(url_for('results', ticker=ticker, run_algorithm=False))

    return render_template('index.html')

@app.route('/results/<ticker>')
def results(ticker):
    data_folder = os.path.join(DATA_FOLDER, ticker)
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    run_algorithm = request.args.get('run_algorithm', 'true').lower() == 'true'

    # Paths for parent backtest and latest child backtest and compare files
    parent_backtest_path = os.path.join(data_folder, f'{ticker}_parent_backtest.csv')

    if run_algorithm:
        # Fetch data and run the algorithm if requested
        fetch_data.fetch_price_data(ticker, data_folder)

        # Run parent backtest
        backtest_parent.run_backtest(
            ticker, data_folder, parent_backtest_path,
            STOP_LOSSES, REWARD_RATIOS, POSITIONS, INTERVALS
        )

        # Create timestamped paths for child and compare backtests
        datetime_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        child_backtest_path = os.path.join(data_folder, f'{ticker}_{datetime_str}_child_backtest.csv')
        compare_path = os.path.join(data_folder, f'{ticker}_{datetime_str}_compare.csv')

        # Run child backtest and compare
        backtest_child.run_backtest(
            ticker, data_folder, child_backtest_path,
            STOP_LOSSES, REWARD_RATIOS, POSITIONS, INTERVALS
        )
        compare.compare_backtests(parent_backtest_path, child_backtest_path, compare_path)

    else:
        # Retrieve the most recent child backtest and compare files
        child_backtest_path = get_latest_file(data_folder, f'{ticker}_.*_child_backtest.csv')
        compare_path = get_latest_file(data_folder, f'{ticker}_.*_compare.csv')

        # If no recent files exist, redirect to an error page or show a message
        if not (os.path.exists(parent_backtest_path) and child_backtest_path and compare_path):
            return "No recent data found. Please run the algorithm first.", 404

    # Load results into DataFrames
    comparison_results_df = compare.read_comparison_results(compare_path)
    parent_results_df = compare.read_comparison_results(parent_backtest_path)
    child_results_df = compare.read_comparison_results(child_backtest_path)

    # Convert DataFrames to lists of dictionaries for easier rendering in HTML
    comparison_results = comparison_results_df.to_dict(orient='records')
    parent_results = parent_results_df.to_dict(orient='records')
    child_results = child_results_df.to_dict(orient='records')

    return render_template(
        'results.html', ticker=ticker,
        comparison_results=comparison_results,
        parent_results=parent_results,
        child_results=child_results
    )

def get_latest_file(directory, pattern):
    """Find the most recent file matching the pattern in a given directory."""
    matched_files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if re.match(pattern, f)
    ]
    if not matched_files:
        return None
    latest_file = max(matched_files, key=os.path.getctime)
    return latest_file


@app.route('/bar')
def bar():
    # Serve the page with the chart and file selection
    return render_template('bar.html')

@app.route('/get_tickers')
def get_tickers():
    # Get all tickers and filter for files that include "compare" in their names
    tickers = {
        subfolder: [file for file in os.listdir(os.path.join(DATA_FOLDER, subfolder))
                    if "compare" in file and file.endswith(".csv")]
        for subfolder in os.listdir(DATA_FOLDER)
        if os.path.isdir(os.path.join(DATA_FOLDER, subfolder))
    }
    return jsonify(tickers=tickers)

@app.route('/get_file/<ticker>/<filename>')
def get_file(ticker, filename):
    # Serve only files containing "compare" in their names from the specified ticker's folder
    if "compare" in filename and filename.endswith(".csv"):
        return send_from_directory(os.path.join(DATA_FOLDER, ticker), filename)
    else:
        return "File not allowed", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3131)