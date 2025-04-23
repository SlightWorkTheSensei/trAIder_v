import yfinance as yf
import pandas as pd

def get_price_change(ticker_symbol):
    try:
        # Fetch the data for the specified ticker
        ticker_data = yf.Ticker(ticker_symbol)
        
        # Get the daily price and volume data for the past 30 days
        daily_data = ticker_data.history(period='1d')
        
        # Calculate the price change
        open_price = daily_data['Open'].iloc[0]
        close_price = daily_data['Close'].iloc[-1]
        price_change = close_price - open_price
        
        # Calculate the percent change
        percent_change = (price_change / open_price) * 100
        
        # Get the volume for the most recent day
        volume = daily_data['Volume'].iloc[-1]
        
        # Calculate the average volume for the past 30 days
        average_volume = daily_data['Volume'].mean()
        
        # Calculate the current commitment
        current_commitment = volume / average_volume
        
        return {
            "Ticker": ticker_symbol,
            "Price": round(close_price, 3),
            "Price Change": round(price_change, 3),
            "Price Percent Change": round(percent_change, 3),
            "Volume": round(volume, 3),
            "avgVolume": round(average_volume, 3),
            "CurrentCommitment": round(current_commitment, 3)
        }
    except Exception as e:
        return f"Error fetching data for {ticker_symbol}: {e}"

if __name__ == "__main__":
    # Read tickers from the CSV file
    tickers_df = pd.read_csv("tickers.csv", header=None, names=["Ticker"])
    tickers = tickers_df["Ticker"].tolist()
    
    # Fetch data for each ticker
    data = [get_price_change(ticker) for ticker in tickers]
    
    # Convert data to DataFrame
    data_df = pd.DataFrame(data)
    
    # Save data to CSV
    data_df.to_csv("refreshed_data.csv", index=False)
