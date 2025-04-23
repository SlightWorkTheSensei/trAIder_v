import pandas as pd
from scipy.stats import norm

def calculate_confidence_interval(batting_avg, sample_size, confidence_level=0.95):
    if sample_size == 0:
        return (None, None)
    z_score = norm.ppf(1 - (1 - confidence_level) / 2)
    standard_error = ((batting_avg * (1 - batting_avg)) / sample_size) ** 0.5
    lower_bound = batting_avg - z_score * standard_error
    upper_bound = batting_avg + z_score * standard_error
    return (lower_bound, upper_bound)

def calculate_z_score(parent_avg, child_avg, parent_size, child_size):
    if parent_size == 0 or child_size == 0:
        return 0
    pooled_variance = parent_avg * (1 - parent_avg)
    standard_error = (pooled_variance / parent_size + pooled_variance / child_size) ** 0.5
    if standard_error == 0:
        return 0
    return (child_avg - parent_avg) / standard_error

def compare_backtests(parent_backtest_path, child_backtest_path, compare_save_path):
    parent_df = pd.read_csv(parent_backtest_path)
    child_df = pd.read_csv(child_backtest_path)

    # Merge on common columns
    merged_df = pd.merge(
        parent_df, child_df,
        on=['stop_loss', 'reward_ratio', 'position', 'interval'],
        suffixes=('_parent', '_child')
    )

    # Calculate z-score and confidence intervals
    merged_df['parent_confidence_interval'] = merged_df.apply(
        lambda row: calculate_confidence_interval(row['batting_avg_parent'], row['num_trades_parent']), axis=1
    )
    merged_df['z_score'] = merged_df.apply(
        lambda row: calculate_z_score(
            row['batting_avg_parent'], row['batting_avg_child'],
            row['num_trades_parent'], row['num_trades_child']
        ), axis=1
    )

    # Calculate percentage difference
    merged_df['percent_diff'] = merged_df.apply(
        lambda row: ((row['batting_avg_child'] - row['batting_avg_parent']) / abs(row['batting_avg_parent']) * 100)
        if row['batting_avg_parent'] != 0 else 0, axis=1
    )

    # Define performance classification
    def performance(row):
        if abs(row['z_score']) > 1.96:
            return 'OVER' if row['z_score'] > 0 else 'UNDER'
        elif row['percent_diff'] > 0:
            return 'OVER'
        elif row['percent_diff'] < 0:
            return 'UNDER'
        else:
            return 'UNDER'

    merged_df['performance'] = merged_df.apply(performance, axis=1)

    # Save results
    merged_df.to_csv(compare_save_path, index=False)

def read_comparison_results(compare_path):
    return pd.read_csv(compare_path)
