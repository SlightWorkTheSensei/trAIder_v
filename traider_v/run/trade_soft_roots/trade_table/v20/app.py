import os
import warnings
import contextlib
import time
from flask import Flask, render_template, request
import pandas as pd
from py.visualize_backtest import generate_visualizations
from py.compile_run import compile_and_run
from py.data_collector import fetch_data

# Ignore all warnings globally
warnings.filterwarnings("ignore")

# Get the root directory of the current script (this ensures correct absolute paths)
root_dir = os.path.abspath(os.path.dirname(__file__))

# Define the absolute paths for the 'data' and 'static' folders
data_folder = os.path.join(root_dir, 'data')
static_folder = os.path.join(root_dir, 'static')

# Ensure necessary folders exist
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

if not os.path.exists(static_folder):
    os.makedirs(static_folder)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    visualizations = None
    selected_ticker = ""

    if request.method == "POST":
        # Get ticker input from user
        ticker = request.form["ticker"].upper()

        if not ticker:
            results = "Error: Invalid ticker selection."
        else:
            selected_ticker = ticker

            # Paths to files and folders (now using absolute paths)
            price_data_file = os.path.join(data_folder, f"{ticker}_1min.csv")
            results_file = os.path.join(data_folder, f"backtest_results_{ticker}.csv")
            visualizations_folder = os.path.join(static_folder, f"{ticker}_correlations")

            # If price data doesn't exist, fetch it
            if not os.path.exists(price_data_file):
                with contextlib.redirect_stderr(open(os.devnull, 'w')):
                    fetch_data(ticker)
                # If fetching fails, return an error message
                if not os.path.exists(price_data_file):
                    results = f"Error: Could not fetch data for ticker '{ticker}'. Ticker might not exist."
                    return render_template("index.html", results=results, selected_ticker=selected_ticker)

            # If backtest results don't exist, compile and run the C++ backtest logic
            if not os.path.exists(results_file):
                with contextlib.redirect_stderr(open(os.devnull, 'w')):
                    compile_result = compile_and_run(ticker)
                if "Compilation failed" in compile_result:
                    results = "Error: Unable to run backtest. Compilation failed."
                    return render_template("index.html", results=results, selected_ticker=selected_ticker)
                elif "Error running backtest" in compile_result:
                    results = compile_result
                    return render_template("index.html", results=results, selected_ticker=selected_ticker)

            # Read the backtest results
            if os.path.exists(results_file):
                with contextlib.redirect_stderr(open(os.devnull, 'w')):
                    results_df = pd.read_csv(results_file)

                if not results_df.empty:
                    results = results_df.to_dict(orient='records')

                    # Check if visualizations exist in the folder
                    if not os.path.exists(visualizations_folder) or not os.listdir(visualizations_folder):
                        # Generate visualizations if they do not exist
                        with contextlib.redirect_stderr(open(os.devnull, 'w')):
                            visualizations = generate_visualizations(ticker)
                        time.sleep(1)  # Adding a short delay to ensure plots are saved before rendering
                    else:
                        # Load existing visualizations
                        visualizations = {
                            "scatter_plots": [os.path.join(f"{ticker}_correlations", f).replace("\\", "/") for f in os.listdir(visualizations_folder) if f.endswith('.html')]
                        }
            else:
                results = "Error: Backtest results not found."

    return render_template("index.html", results=results, visualizations=visualizations, selected_ticker=selected_ticker)

if __name__ == "__main__":
    # Running the app while still printing the port information
    app.run(host='0.0.0.0', port=6066)
