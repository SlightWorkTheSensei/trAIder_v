from flask import Flask, render_template, request
import json
import yfinance as yf
import pandas as pd  # Import pandas

app = Flask(__name__)

# Valid Yahoo Finance intervals and periods
VALID_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

# Fetch historical price data
def fetch_data(ticker, interval, period):
    try:
        # Fetch historical data
        data = yf.download(ticker, interval=interval, period=period)

        # Debugging: Inspect the returned data
        print("Data fetched from Yahoo Finance:")
        print(data.head())  # Show the first few rows
        print("Data type:", type(data))
        print("Data columns:", data.columns)

        # Ensure data is not empty
        if data.empty:
            raise RuntimeError(f"No data returned for ticker: {ticker}")

        # Flatten MultiIndex columns if necessary
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            print("Flattened columns:", data.columns)

        # Process the data
        trade_data = [
            {
                "datetime": i.strftime("%Y-%m-%d %H:%M:%S"),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Adj Close"] if "Adj Close" in row else row["Close"],
            }
            for i, row in data.iterrows()
        ]
        return trade_data
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data for {ticker}: {str(e)}")


# Backtest trades to calculate outcomes
def process_trades(trade_data, stop_loss, reward_to_risk):
    results = []
    for i, trade in enumerate(trade_data):
        entry = trade["close"]
        stop = entry - stop_loss
        target = entry + (stop_loss * reward_to_risk)

        outcome = "Open"
        for j in range(i + 1, len(trade_data)):
            if trade_data[j]["low"] <= stop:
                outcome = "Stop"
                break
            elif trade_data[j]["high"] >= target:
                outcome = "Target"
                break

        results.append({
            "datetime": trade["datetime"],
            "open": trade["open"],
            "high": trade["high"],
            "low": trade["low"],
            "close": trade["close"],
            "entry": entry,
            "stop": stop,
            "target": target,
            "outcome": outcome,
        })

    return results


# Detect streaks and assign grouping intensity
def detect_groupings(trade_results):
    grouping_data = []
    current_streak_color = None
    streak_length = 0

    for trade in trade_results:
        if trade["outcome"] == "Target":
            current_color = "green"
        elif trade["outcome"] == "Stop":
            current_color = "red"
        else:
            current_color = None
            streak_length = 0

        if current_color == current_streak_color:
            streak_length += 1
        else:
            current_streak_color = current_color
            streak_length = 1

        grouping_intensity = (
            4 if streak_length >= 10 else
            3 if streak_length >= 8 else
            2 if streak_length >= 6 else
            1 if streak_length >= 4 else
            0
        )

        grouping_data.append({
            "datetime": trade["datetime"],
            "grouping_intensity": grouping_intensity,
        })

    return grouping_data


@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    trade_results = []
    grouping_data = []

    # Default values
    ticker = "SPY"
    selected_interval = "1d"
    selected_period = "1mo"
    stop_loss = 1.0
    reward_to_risk = 1.0

    if request.method == "POST":
        try:
            # Fetch form data
            ticker = request.form.get("ticker", "SPY").upper()
            selected_interval = request.form.get("interval", "1d")
            selected_period = request.form.get("period", "1mo")
            stop_loss = float(request.form.get("stop_loss", 1.0))
            reward_to_risk = float(request.form.get("reward_to_risk", 1.0))

            # Validate interval and period
            if selected_interval not in VALID_INTERVALS or selected_period not in VALID_PERIODS:
                raise ValueError("Invalid interval or period selected.")

            # Fetch, process, and analyze trade data
            trade_data = fetch_data(ticker, selected_interval, selected_period)
            trade_results = process_trades(trade_data, stop_loss, reward_to_risk)
            grouping_data = detect_groupings(trade_results)
        except ValueError as ve:
            error_message = str(ve)
        except RuntimeError as re:
            error_message = str(re)
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"

    return render_template(
        "index.html",
        trade_results=json.dumps(trade_results),
        grouping_data=json.dumps(grouping_data),
        ticker=ticker,
        selected_interval=selected_interval,
        selected_period=selected_period,
        stop_loss=stop_loss,
        reward_to_risk=reward_to_risk,
        error_message=error_message,
    )


if __name__ == "__main__":
    app.run(debug=True, port=2332)
