import os
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_data(ticker, data_folder):
    # Define intervals and corresponding valid periods
    intervals = {
        '1m': None,     # Special handling with start/end dates
        '5m': '1mo',    # Valid period for 5m data
        '15m': '1mo',   # Adjusted period for 15m data
        '60m': '6mo'    # Valid period for 60m data
    }

    # Ensure the data folder exists
    os.makedirs(data_folder, exist_ok=True)

    for interval, period in intervals.items():
        save_path = os.path.join(data_folder, f'{ticker}_{interval}_price_data.csv')

        try:
            if interval == '1m':
                # Use start/end dates for 1m interval
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)
                new_data = yf.download(
                    tickers=ticker,
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    interval=interval,
                    progress=False,
                    threads=False
                )
            else:
                # Use period for other intervals
                new_data = yf.download(
                    tickers=ticker,
                    period=period,
                    interval=interval,
                    progress=False,
                    threads=False
                )

            # Check if data was fetched successfully
            if new_data.empty:
                print(f"No data fetched for {ticker} at interval {interval}. Skipping...")
                continue

            # Reset index to make 'Datetime' a column and rename columns
            new_data.reset_index(inplace=True)
            new_data.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Adj Close': 'Adj Close',
                'Volume': 'Volume'
            }, inplace=True)

            # Ensure the column order matches the required format
            required_columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            new_data = new_data[required_columns]

            # Save the data to CSV
            new_data.to_csv(save_path, index=False)
            print(f"Saved {ticker} {interval} data to {save_path}")

        except Exception as e:
            print(f"Failed to fetch {interval} data for {ticker}: {e}")

        # Pause between API requests
        time.sleep(0.6)
