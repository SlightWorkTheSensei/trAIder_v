from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

app = Flask(__name__)

def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    
    hist_1min = stock.history(period="1d", interval="1m")
    hist_15min = stock.history(period="1d", interval="15m")
    hist_60min = stock.history(period="5d", interval="60m")
    hist_daily = stock.history(period="30d", interval="1d")
    
    data = {
        "Ticker": ticker,
    }
    
    if not hist_daily.empty:
        # Calculate current price change and volume
        data["Current Price Change"] = float((hist_daily['Close'][-1] - hist_daily['Open'][0]) / hist_daily['Open'][0] * 100)
        data["Current Volume"] = int(hist_daily['Volume'][-1])
        
        # Calculate price changes for each timeframe
        data["Price Change 1min"] = float(hist_1min['Close'].iloc[-1] - hist_1min['Close'].iloc[0]) if len(hist_1min) > 0 else 0
        data["Price Change 15min"] = float(hist_15min['Close'].iloc[-1] - hist_15min['Close'].iloc[0]) if len(hist_15min) > 0 else 0
        data["Price Change 60min"] = float(hist_60min['Close'].iloc[-1] - hist_60min['Close'].iloc[0]) if len(hist_60min) > 0 else 0
        data["Price Change Daily"] = float(hist_daily['Close'].iloc[-1] - hist_daily['Close'].iloc[0]) if len(hist_daily) > 0 else 0
        
        # Calculate volume changes for each timeframe
        data["Volume Change 1min"] = int(hist_1min['Volume'].iloc[-1] - hist_1min['Volume'].iloc[0]) if len(hist_1min) > 0 else 0
        data["Volume Change 15min"] = int(hist_15min['Volume'].iloc[-1] - hist_15min['Volume'].iloc[0]) if len(hist_15min) > 0 else 0
        data["Volume Change 60min"] = int(hist_60min['Volume'].iloc[-1] - hist_60min['Volume'].iloc[0]) if len(hist_60min) > 0 else 0
        data["Volume Change Daily"] = int(hist_daily['Volume'].iloc[-1] - hist_daily['Volume'].iloc[0]) if len(hist_daily) > 0 else 0
        
        # Calculate average price change and volume for different timeframes
        data["Avg Price Change 1min"] = float(((hist_1min['Close'] - hist_1min['High']).abs()).mean()) if len(hist_1min) > 0 else 0
        data["Avg Price Change 15min"] = float(((hist_15min['Close'] - hist_15min['High']).abs()).mean()) if len(hist_15min) > 0 else 0
        data["Avg Price Change 60min"] = float(((hist_60min['Close'] - hist_60min['High']).abs()).mean()) if len(hist_60min) > 0 else 0
        data["Avg Price Change Daily"] = float(((hist_daily['Close'] - hist_daily['High']).abs()).mean()) if len(hist_daily) > 0 else 0
        
        data["Avg Volume 1min"] = float(hist_1min['Volume'].mean()) if len(hist_1min) > 0 else 0
        data["Avg Volume 15min"] = float(hist_15min['Volume'].mean()) if len(hist_15min) > 0 else 0
        data["Avg Volume 60min"] = float(hist_60min['Volume'].mean()) if len(hist_60min) > 0 else 0
        data["Avg Volume Daily"] = float(hist_daily['Volume'].mean()) if len(hist_daily) > 0 else 0
        
        data["Avg Trading Range 1min"] = float((hist_1min['High'] - hist_1min['Low']).mean()) if len(hist_1min) > 0 else 0
        data["Avg Trading Range 15min"] = float((hist_15min['High'] - hist_15min['Low']).mean()) if len(hist_15min) > 0 else 0
        data["Avg Trading Range 60min"] = float((hist_60min['High'] - hist_60min['Low']).mean()) if len(hist_60min) > 0 else 0
        data["Avg Trading Range Daily"] = float((hist_daily['High'] - hist_daily['Low']).mean()) if len(hist_daily) > 0 else 0
        
        # Calculate ratios
        data["Ratio Current/Avg Price Change 1min"] = data["Current Price Change"] / data["Avg Price Change 1min"] if data["Avg Price Change 1min"] != 0 else 0
        data["Ratio Current/Avg Price Change 15min"] = data["Current Price Change"] / data["Avg Price Change 15min"] if data["Avg Price Change 15min"] != 0 else 0
        data["Ratio Current/Avg Price Change 60min"] = data["Current Price Change"] / data["Avg Price Change 60min"] if data["Avg Price Change 60min"] != 0 else 0
        data["Ratio Current/Avg Price Change Daily"] = data["Current Price Change"] / data["Avg Price Change Daily"] if data["Avg Price Change Daily"] != 0 else 0
        
        data["Ratio Current/Avg Volume 1min"] = data["Current Volume"] / data["Avg Volume 1min"] if data["Avg Volume 1min"] != 0 else 0
        data["Ratio Current/Avg Volume 15min"] = data["Current Volume"] / data["Avg Volume 15min"] if data["Avg Volume 15min"] != 0 else 0
        data["Ratio Current/Avg Volume 60min"] = data["Current Volume"] / data["Avg Volume 60min"] if data["Avg Volume 60min"] != 0 else 0
        data["Ratio Current/Avg Volume Daily"] = data["Current Volume"] / data["Avg Volume Daily"] if data["Avg Volume Daily"] != 0 else 0
    
    return data, hist_1min, hist_15min, hist_60min, hist_daily

def create_candlestick_volume_charts(data, interval):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        row_heights=[0.7, 0.3])
    
    candlestick = go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Candlesticks')
    
    volume_bar = go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='blue', opacity=0.5)
    
    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(volume_bar, row=2, col=1)
    
    fig.update_layout(title=f'{interval} Candlestick Chart with Volume for {data.index.name}',
                      xaxis_title='Time', yaxis_title='Price', yaxis2_title='Volume')
    
    return fig

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    data = request.get_json()
    ticker = data.get('ticker')

    data, hist_1min, hist_15min, hist_60min, hist_daily = fetch_stock_data(ticker)
    
    fig_1min = create_candlestick_volume_charts(hist_1min, '1 Minute')
    fig_15min = create_candlestick_volume_charts(hist_15min, '15 Minutes')
    fig_60min = create_candlestick_volume_charts(hist_60min, '1 Hour')
    fig_daily = create_candlestick_volume_charts(hist_daily, 'Daily')
    
    fig_1min_json = fig_1min.to_json()
    fig_15min_json = fig_15min.to_json()
    fig_60min_json = fig_60min.to_json()
    fig_daily_json = fig_daily.to_json()
    
    return jsonify({
        'data': data,
        'fig_1min': fig_1min_json,
        'fig_15min': fig_15min_json,
        'fig_60min': fig_60min_json,
        'fig_daily': fig_daily_json
    })

if __name__ == '__main__':
    app.run(debug=True, port=8888)
