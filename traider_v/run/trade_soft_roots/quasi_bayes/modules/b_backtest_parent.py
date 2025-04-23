import pandas as pd
import os
import json
from multiprocessing import Pool, cpu_count
import numpy as np

def run_backtest(ticker, data_folder, backtest_save_path, stop_losses, reward_ratios, positions, intervals):
    results = []
    trade_results_folder = os.path.join(data_folder, 'trade_results')

    if not os.path.exists(trade_results_folder):
        os.makedirs(trade_results_folder)

    for interval in intervals:
        price_data_path = os.path.join(data_folder, f'{ticker}_{interval}m_price_data.csv')
        if not os.path.exists(price_data_path):
            print(f"No data found for interval {interval}. Skipping.")
            continue

        data = pd.read_csv(price_data_path, index_col='Datetime', parse_dates=True)

        # Ensure numeric data types
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
        data.dropna(subset=['Open', 'High', 'Low'], inplace=True)

        with Pool(cpu_count()) as pool:
            params = [
                (data, stop_loss, reward_ratio, position, interval, trade_results_folder)
                for stop_loss in stop_losses
                for reward_ratio in reward_ratios
                for position in positions
            ]
            new_results = pool.starmap(process_single_backtest, params)
            results.extend(new_results)

    results_df = pd.DataFrame(results)
    results_df.to_csv(backtest_save_path, index=False)

def process_single_backtest(data, stop_loss, reward_ratio, position, interval, trade_results_folder):
    json_file_name = f"{stop_loss}_{reward_ratio}_{interval}_{position}.json"
    json_file_path = os.path.join(trade_results_folder, json_file_name)

    # Load existing trades if any
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            trades = json.load(file)
    else:
        trades = []

    # Run backtest logic
    new_trades = backtest_logic(data, stop_loss, reward_ratio, position, interval, trades)
    trades.extend(new_trades)

    # Save trades to JSON file
    with open(json_file_path, 'w') as file:
        json.dump(trades, file, indent=4)

    # Calculate metrics
    net_profit = sum(trade['P&L'] for trade in new_trades)
    num_trades = len(new_trades)
    batting_avg = sum(1 for trade in new_trades if trade["Target_Hit(Y/n)"] == "Y") / num_trades if num_trades > 0 else 0

    return {
        'stop_loss': stop_loss,
        'reward_ratio': reward_ratio,
        'position': position,
        'interval': interval,
        'num_trades': num_trades,
        'net_profit': net_profit,
        'batting_avg': batting_avg
    }

def backtest_logic(data, stop_loss, reward_ratio, position, interval, existing_trades):
    new_trades = []
    start_idx = len(existing_trades)

    entry_prices = data['Open'].values
    high_prices = data['High'].values
    low_prices = data['Low'].values
    dates = data.index

    # Ensure numeric arrays
    entry_prices = entry_prices.astype(float)
    high_prices = high_prices.astype(float)
    low_prices = low_prices.astype(float)

    # Calculate targets and stops
    if position == 'long':
        targets = entry_prices + reward_ratio * stop_loss
        stops = entry_prices - stop_loss
    else:
        targets = entry_prices - reward_ratio * stop_loss
        stops = entry_prices + stop_loss

    # Iterate over the data
    for i in range(start_idx, len(entry_prices) - interval):
        hit_target = False
        hit_stop = False
        exit_index = i + interval

        for j in range(i, exit_index):
            if j >= len(entry_prices):
                break

            if position == 'long':
                if high_prices[j] >= targets[i]:
                    hit_target = True
                    exit_index = j
                    break
                elif low_prices[j] <= stops[i]:
                    hit_stop = True
                    exit_index = j
                    break
            else:
                if low_prices[j] <= targets[i]:
                    hit_target = True
                    exit_index = j
                    break
                elif high_prices[j] >= stops[i]:
                    hit_stop = True
                    exit_index = j
                    break

        trade_entry = entry_prices[i]
        trade_exit = targets[i] if hit_target else stops[i] if hit_stop else entry_prices[exit_index]

        pnl = trade_exit - trade_entry if position == 'long' else trade_entry - trade_exit

        new_trade = {
            "Entry": float(trade_entry),
            "Stop": float(stops[i]),
            "Risk": abs(trade_entry - stops[i]),
            "Target_": float(targets[i]),
            "Target_Hit(Y/n)": "Y" if hit_target else "N",
            "Time_Date_Entered": dates[i].strftime("%Y-%m-%d %H:%M:%S"),
            "Time_Date_Exited": dates[exit_index].strftime("%Y-%m-%d %H:%M:%S") if exit_index < len(dates) else "",
            "P&L": float(pnl),
            "Gross_P&L": float(pnl)
        }
        new_trades.append(new_trade)

    return new_trades
