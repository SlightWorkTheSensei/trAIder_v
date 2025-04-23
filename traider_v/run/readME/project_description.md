# Project Descriptions

This document provides a summary of applications built using Python, Go, C++, JavaScript, and HTML/CSS.

---
1-----autoFTC---------------
2-----backtest_summary------
3-----candle_proj-----------
4-----levels----------------
5-----mainFTC---------------
6-----movers----------------
7-----stock-----------------
8-----trade_graphic---------
9-----trade_scan_II------------
10----trade_table-----------


## 1. autoFTC

Uses CSV saved data for Future Contracts, including details like Tick Value, Tick Size, 
Cost per Contract, and initial margin, to determine the number of contracts required. Inputs include:
- Ticker
- Entry Price
- Stop Price
- Buying Power
- Risk Exposure

---

## 2. backtest_summary

The user enters a Ticker, selects time interval(s) (e.g., 1 minute, 5 minutes, etc.), duration, 
and units. The app backtests trading plans based on these intervals, with data available for up to 30 days. 
The following metrics are tested and displayed in a sortable table:
- Number of trades based on interval
- Trade direction
- Stop loss size
- Target size
- Number of wins/losses
- Gross and unrealized gains/losses
- Neutral trades, batting average, and net profit/loss

---

## 3. candle_proj

Allows the user to input a ticker for stocks, futures, crypto, or forex. Provides a directional
 intensity highlight (similar to Heiken Ashi) for the daily timeframe. The app plans to allow 
 timeframe selection, with wider bars indicating potential reversals or pullbacks,
  aiding in backtest plan selection.

---

## 4. levels

Returns an RSI-equivalent based on reversal points, using historical data to indicate potential 
continuations or reversals based on price action. Supports daily, weekly, and monthly timeframes;
 currently being improved for intraday timeframes.

---

## 5. mainFTC

Calculates contract requirements for a Futures Contract. Input details include:
- Buying power
- Risk
- Entry Price
- Stop
- Contract size
- Initial Margin
- Tick Size
- Tick Value

Can also be used for stock calculations by adjusting the contract size,
 initial margin, tick size, and value accordingly.

---

## 6. movers

User clicks a 'Refresh Data' button to retrieve recent price and volume data. Calculates
 the average volume to determine Future Tickers' Commitment Ratio.

---

## 7. stock

A comprehensive Stock Trading Tool Dashboard with multiple features:
1. **Chat Log** - Saves timestamped thoughts.
2. **Initial Input** - Saves initial parameters like buying power, risk, and market bias.
3. **Shares Calculator** - Calculates lot size based on risk, entry price, and stop price.
4. **Average Trading Range Calculator** - Calculates range for multiple timeframes.
5. **Commitment Calculator** - Manually calculates volume-to-average volume ratio.
6. **Pre-trade Tracking** - Logs trade data to a Google Sheet for analysis.
7. **Trade Pattern Checklist** - Allows users to confirm pattern features before trading.

---

## 8. trade_graphic

Allows users to input ticker and trade details (e.g., interval, duration, stop loss, 
reward-to-risk ratio) to visualize a trading plan's success using the most recent data.
 Tracks clusters or groupings of success or failure and uses a heat map to suggest reversals for 
 large groupings or continuations for small ones.

---

## 9. trade_scan_II

Provides candlestick charts for 1-minute, 15-minute, hourly, and daily timeframes. Calculates and displays:
- Price change
- Average price change
- Volume
- Average trading range
- Ratios of current price/volume change to average values

These data points help contextualize recent price and volumetric actions.

---

## 10. trade_table

Enables users to enter a ticker, fetches 1-minute price data from Yahoo Finance, and saves it as a CSV. Data is backtested using C++, and results are saved into another CSV. Python and JavaScript then display these results for four timeframes as scatterplots. Over 1 million results can be displayed, with future support for chunking over four 5-day intraday intervals.

--- 
