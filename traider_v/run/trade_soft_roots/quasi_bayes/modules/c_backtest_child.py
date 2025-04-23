import pandas as pd
import os
import json
from multiprocessing import Pool, cpu_count

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

    # Load full trade history
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            trades = json.load(file)
    else:
        print(f"No trade data available for child backtest in {json_file_name}")
        return {
            'stop_loss': stop_loss,
            'reward_ratio': reward_ratio,
            'position': position,
            'interval': interval,
            'num_trades': 0,
            'net_profit': 0,
            'batting_avg': 0
        }

    # Determine truncation size for child backtest
    if interval == 1:
        trades = trades[-120:]
    elif interval == 5:
        trades = trades[-240:]
    elif interval == 15:
        trades = trades[-64:]
    elif interval == 60:
        trades = trades[-72:]

    net_profit = sum(trade['P&L'] for trade in trades)
    num_trades = len(trades)
    batting_avg = sum(1 for trade in trades if trade["Target_Hit(Y/n)"] == "Y") / num_trades if num_trades > 0 else 0

    return {
        'stop_loss': stop_loss,
        'reward_ratio': reward_ratio,
        'position': position,
        'interval': interval,
        'num_trades': num_trades,
        'net_profit': net_profit,
        'batting_avg': batting_avg
    }
