import yfinance as yf
import pandas as pd
import os

def fetch_ticker_data():
    # Create the data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Load tickers from the original CSV file
    tickers_df = pd.read_csv('data/tickers.csv')

    market_types = tickers_df.columns.tolist()
    for market in market_types:
        market_tickers = tickers_df[market].dropna().tolist()
        data_list = []
        for ticker in market_tickers:
            try:
                # Fetch data from Yahoo Finance
                ticker_data = yf.Ticker(ticker)
                hist_data = ticker_data.history(period="1d")

                # Initialize default values
                price = 'N/A'
                volume = 'N/A'
                avg_volume = 'N/A'
                commitment = 'N/A'

                # Fetch price
                if not hist_data.empty:
                    price = round(hist_data['Close'][-1], 2)

                # For markets other than forex, fetch volume and calculate commitment
                if market != 'forex':
                    # Fetch volume
                    if not hist_data.empty and 'Volume' in hist_data.columns:
                        volume = round(hist_data['Volume'][-1], 2)
                    else:
                        volume = 'N/A'

                    # Fetch average volume
                    avg_volume_info = ticker_data.info.get('averageVolume', 'N/A')
                    avg_volume = round(avg_volume_info, 2) if avg_volume_info != 'N/A' else 'N/A'

                    # Calculate commitment if volume and avg_volume are available
                    if volume != 'N/A' and avg_volume != 'N/A' and avg_volume != 0:
                        commitment = round((volume / avg_volume), 2)
                    else:
                        commitment = 'N/A'

                # Append data to list
                data_list.append({
                    'ticker': ticker,
                    'price': price,
                    'volume': volume,
                    'avg_volume': avg_volume,
                    'commitment': commitment
                })
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                data_list.append({
                    'ticker': ticker,
                    'price': 'N/A',
                    'volume': 'N/A',
                    'avg_volume': 'N/A',
                    'commitment': 'N/A'
                })
        # Save data to CSV
        df = pd.DataFrame(data_list)
        df.to_csv(f'data/{market}_data.csv', index=False)

if __name__ == '__main__':
    fetch_ticker_data()
