import yfinance as yf
import pandas as pd
from flask import render_template
import os
from datetime import datetime
import logging
from .visualization import create_charts

def fetch_data_handler(request, data_folder):
    ticker = request.form['ticker']
    intervals = request.form.getlist('intervals')  # Get all selected intervals as a list
    duration = int(request.form['duration'])
    unit = request.form['unit']

    logging.debug(f"Selected intervals: {intervals}")

    reward_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    risk_array = [1]
    stop_loss_array = [0.01, 0.10, 0.25, 0.50, 0.75, 1, 2.5, 5, 10, 25, 50, 100]

    if unit == 'minutes':
        period = f'{duration}m'
    elif unit == 'hours':
        period = f'{duration}h'
    else:
        period = f'{duration}d'

    logging.debug(f"Ticker: {ticker}, Duration: {duration}, Unit: {unit}, Period: {period}")

    all_results = []
    all_charts = []

    for interval in intervals:
        try:
            data = yf.download(tickers=ticker, period=period, interval=interval)
            if data.empty:
                logging.error(f"No data found for ticker: {ticker}, period: {period}, interval: {interval}")
                continue  # Skip to the next interval if no data is found
            logging.debug(f"Data for interval {interval}: {data.head()}")
        except Exception as e:
            logging.exception("Error downloading data")
            continue  # Skip to the next interval if an error occurs

        avg_volume = data['Volume'].mean()
        data['Average Volume'] = avg_volume

        results = []

        for reward in reward_array:
            for risk in risk_array:
                for stop_loss in stop_loss_array:
                    for trade_direction in ['long', 'short']:
                        trades = []
                        account_values = [10000]  # Starting account value
                        account_value = 10000
                        initial_account_value = account_value
                        gross_profit = 0
                        gross_loss = 0
                        unrealized_gain = 0
                        unrealized_loss = 0
                        for i in range(len(data) - 1):
                            entry_price = data['Close'][i]
                            if trade_direction == 'long':
                                target = entry_price + reward * stop_loss
                                stop = entry_price - stop_loss
                            else:
                                target = entry_price - reward * stop_loss
                                stop = entry_price + stop_loss

                            trade = {'entry': entry_price, 'target': target, 'stop': stop, 'type': trade_direction}
                            trade_closed = False
                            # Check if the trade hits target or stop loss
                            for j in range(i + 1, len(data)):
                                if trade_direction == 'long' and data['Low'][j] <= stop:
                                    trade['result'] = 'loss'
                                    account_value -= stop_loss
                                    gross_loss += stop_loss
                                    trade_closed = True
                                    break
                                if trade_direction == 'long' and data['High'][j] >= target:
                                    trade['result'] = 'win'
                                    account_value += reward * stop_loss
                                    gross_profit += reward * stop_loss
                                    trade_closed = True
                                    break
                                if trade_direction == 'short' and data['High'][j] >= stop:
                                    trade['result'] = 'loss'
                                    account_value -= stop_loss
                                    gross_loss += stop_loss
                                    trade_closed = True
                                    break
                                if trade_direction == 'short' and data['Low'][j] <= target:
                                    trade['result'] = 'win'
                                    account_value += reward * stop_loss
                                    gross_profit += reward * stop_loss
                                    trade_closed = True
                                    break

                            if not trade_closed:
                                trade['result'] = 'neutral'
                                # Calculate unrealized gain/loss
                                if trade_direction == 'long':
                                    unrealized_gain += max(0, data['Close'][j] - entry_price)
                                    unrealized_loss += max(0, entry_price - data['Close'][j])
                                else:
                                    unrealized_gain += max(0, entry_price - data['Close'][j])
                                    unrealized_loss += max(0, data['Close'][j] - entry_price)

                            trades.append(trade)
                            account_values.append(account_value)

                        win_trades = [trade for trade in trades if trade['result'] == 'win']
                        loss_trades = [trade for trade in trades if trade['result'] == 'loss']
                        neutral_trades = [trade for trade in trades if trade['result'] == 'neutral']

                        batting_average = len(win_trades) / len(trades) if trades else 0
                        net_profit_loss = account_value - initial_account_value
                        net_profit_loss_percentage = (net_profit_loss / initial_account_value) * 100

                        result = {
                            'interval': interval,
                            'reward': reward,
                            'risk': risk,
                            'stop_loss': stop_loss,
                            'trade_type': trade_direction,
                            'total_trades': len(trades),
                            'win_trades': len(win_trades),
                            'loss_trades': len(loss_trades),
                            'neutral_trades': len(neutral_trades),
                            'batting_average': f"{round(batting_average * 100, 3)}%",
                            'gross_profit': round(gross_profit, 3),
                            'gross_loss': round(gross_loss, 3),
                            'net_profit_loss_percentage': f"{round(net_profit_loss_percentage, 3)}%",
                            'unrealized_gain': round(unrealized_gain, 3),
                            'unrealized_loss': round(unrealized_loss, 3),
                            'account_values': account_values
                        }

                        results.append(result)

        logging.debug(f"Results for interval {interval}: {results}")

        if results:
            all_results.extend(results)

            # Generate charts for each interval
            graph_candlestick, graph_volume = create_charts(data, ticker)
            all_charts.append((interval, graph_candlestick, graph_volume))

            # Save the data for each interval
            file_name = f"{ticker}_{interval}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            file_path = os.path.join(data_folder, file_name)
            data.to_csv(file_path)

    if not all_results:
        logging.error("No valid results generated for any interval.")
        return "No valid data found for any selected interval.", 400

    return render_template('display.html', results=all_results, charts=all_charts, ticker=ticker, duration=duration, intervals=intervals)
