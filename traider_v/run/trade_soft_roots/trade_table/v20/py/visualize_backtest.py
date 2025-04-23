import pandas as pd
import plotly.express as px
import os

# Define folder paths relative to the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_folder = os.path.join(root_dir, 'data')
static_folder = os.path.join(root_dir, 'static')

def generate_visualizations(ticker):
    """
    Generates scatter plots based on the backtest results
    for a given ticker, including multiple timeframes.
    Saves the visualizations as HTML files.
    """
    # Load backtest results
    results_file = os.path.join(data_folder, f"backtest_results_{ticker}.csv")
    if not os.path.exists(results_file):
        print(f"Backtest results for {ticker} not found.")
        return None

    # Read the CSV file
    results_df = pd.read_csv(results_file)

    # If the dataframe is empty, no data to visualize
    if results_df.empty:
        print(f"No data available for {ticker}. Backtest CSV is empty.")
        return None

    # Ensure the output folder exists for visualizations
    output_folder = os.path.join(static_folder, f"{ticker}_correlations")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    visualizations = {
        "scatter_plots": []
    }

    # Define the intervals to visualize (1min, 5min, 15min, 30min, 60min)
    intervals = ["1min", "5min", "15min", "30min", "60min"]

    # Create scatter plots for relevant metrics against "Net P/L (%)"
    metrics = ["Stop Loss", "Reward", "Gross Profit", "Gross Loss", "Wins", "Losses"]

    for interval in intervals:
        # Filter the data by the interval
        interval_df = results_df[results_df["Interval"] == interval]

        if not interval_df.empty:
            for metric in metrics:
                if metric in interval_df.columns:
                    fig = px.scatter(
                        interval_df,
                        x=metric,
                        y="Net P/L (%)",
                        title=f"{metric} vs. Net P/L (%) for {ticker} - {interval}",
                        hover_name="Interval",
                        hover_data={
                            "Stop Loss": True,
                            "Reward": True,
                            "Net P/L (%)": True,
                            "Gross Profit": True,
                            "Gross Loss": True
                        },
                        color="Net P/L (%)",
                        color_continuous_scale=px.colors.sequential.Viridis
                    )
                    fig.update_layout(
                        plot_bgcolor="#0A0A0A",
                        paper_bgcolor="#121212",
                        font=dict(color="#7cff81"),
                        title_font=dict(size=20)
                    )
                    # Save plot as HTML
                    scatter_plot_filename = f"scatter_{interval}_{metric.replace(' ', '_')}_vs_Net_P_L.html"
                    scatter_plot_path = os.path.join(output_folder, scatter_plot_filename)
                    fig.write_html(scatter_plot_path)

                    # Append the path relative to the static folder for Flask
                    relative_path = f"{ticker}_correlations/{scatter_plot_filename}"
                    visualizations["scatter_plots"].append(relative_path)

    return visualizations

if __name__ == "__main__":
    ticker = "VTI"  # Example for testing
    generate_visualizations(ticker)
