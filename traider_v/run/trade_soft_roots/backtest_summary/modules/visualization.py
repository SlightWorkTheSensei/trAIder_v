import plotly.graph_objs as go
import plotly.io as pio

def create_charts(data, ticker):
    # Create candlestick chart
    fig_candlestick = go.Figure(data=[go.Candlestick(x=data.index,
                                                     open=data['Open'],
                                                     high=data['High'],
                                                     low=data['Low'],
                                                     close=data['Close'],
                                                     name='Price')])
    fig_candlestick.update_layout(title=f"{ticker} Price", xaxis_title="Date", yaxis_title="Price")

    # Create volume bar chart
    fig_volume = go.Figure(data=[go.Bar(x=data.index, y=data['Volume'], name='Volume')])
    fig_volume.update_layout(title=f"{ticker} Volume", xaxis_title="Date", yaxis_title="Volume")

    graph_candlestick = pio.to_html(fig_candlestick, full_html=False)
    graph_volume = pio.to_html(fig_volume, full_html=False)

    return graph_candlestick, graph_volume
