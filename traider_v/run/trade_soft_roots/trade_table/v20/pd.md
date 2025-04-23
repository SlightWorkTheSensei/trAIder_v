trAIder_ii/
├── trade_table/
│   ├── v15/
│   │   ├── py/                          # Python-related scripts
│   │   │   ├── app.py                   # Main Flask app
│   │   │   ├── data_collector.py        # Script for collecting Yahoo Finance data
│   │   │   ├── compile_run.py           # Script for compiling and running C++ backtesting
│   │   │   ├── visualize_backtest.py    # Script for generating visualizations from backtest data
│   │   ├── cpp/                         # C++-related code
│   │   │   ├── backtest.cpp             # C++ logic for backtesting
│   │   ├── static/                      # Static assets (e.g., CSS, JS, images)
│   │   │   ├── SPY_correlations/        # Folder containing generated correlation matrix images for SPY ticker
│   │   │   ├── AAPL_correlations/       # Folder containing generated correlation matrix images for AAPL ticker
│   │   │   └── (ticker)_correlations/   # Similar folders for each ticker (dynamically created)
│   │   ├── templates/                   # Flask HTML templates
│   │   │   ├── index.html               # Main HTML page for user interaction
│   │   └── data/                        # Collected data (CSV files)
│   │       ├── SPY_1min.csv             # Example CSV for SPY ticker's 1-minute data
│   │       ├── AAPL_1min.csv            # Example CSV for AAPL ticker's 1-minute data
│   │       └── backtest_results_SPY.csv # Backtest results for SPY
│   │
│   └── README.md                        # Documentation for the project, including instructions on how to run it
└── requirements.txt                     # Dependencies for Python (e.g., Flask, yfinance, pandas)
