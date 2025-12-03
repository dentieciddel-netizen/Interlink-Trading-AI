from flask import Flask, jsonify
import pandas as pd
import plotly.graph_objs as go
import json
import os
import ccxt
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
EXCHANGE = os.getenv("EXCHANGE", "binance")
SYMBOL = os.getenv("SYMBOL", "ICP/USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "1m")

def get_exchange():
    """Initialize the exchange based on environment variables."""
    exchange_class = getattr(ccxt, EXCHANGE)
    return exchange_class({
        "apiKey": API_KEY,
        "secret": API_SECRET,
        "enableRateLimit": True,
    })

exchange = get_exchange()

@app.route("/")
def index():
    return "Multi-Exchange Trading App Running"

@app.route("/ohlcv")
def ohlcv():
    """Fetch OHLCV data and return a candlestick chart as JSON."""
    bars = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=50)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")

    fig = go.Figure(data=[go.Candlestick(
        x=df["datetime"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])
    fig.update_layout(title=f"{SYMBOL} ({EXCHANGE}) Live", xaxis_rangeslider_visible=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
