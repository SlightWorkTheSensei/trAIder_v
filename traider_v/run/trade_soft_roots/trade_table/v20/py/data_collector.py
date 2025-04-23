# data_collector.py
import yfinance as yf
import pandas as pd
import sys
import os

# Define the path to the data folder relative to the current file (i.e., in the root directory)
data_folder = os.path.join(os.path.dirname(__file__), '../data')

# Ensure the data folder exists
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

def fetch_data(ticker):
    """
    Fetch 5 days worth of 1-minute data from Yahoo Finance for the specified ticker.
    Save the data as a CSV file.
    """
    try:
        # Get 5 days of 1-minute data
        data = yf.download(ticker, period="5d", interval="1m")
        # Save data as CSV in the data folder
        csv_path = os.path.join(data_folder, f"{ticker}_1min.csv")
        data.to_csv(csv_path)
        print(f"Data for {ticker} saved as {csv_path}")
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")

if __name__ == "__main__":
    # Set a default ticker if none is provided via command-line arguments
    default_ticker = "MNQ=F"
    
    if len(sys.argv) < 2:
        print(f"No ticker provided. Using default ticker: {default_ticker}")
        ticker = default_ticker
    else:
        ticker = sys.argv[1]
    
    fetch_data(ticker)
