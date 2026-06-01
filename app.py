from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Market Analysis Engine
def get_signal(symbol):
    try:
        # 1m data fetch
        df = yf.download(f"{symbol}=X", period="1d", interval="1m", progress=False)
        if df.empty: return "AVOID", "No Data"
        
        # Indicators
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bb = ta.bbands(df['Close'], length=20)
        df['BBU'] = bb['BBU_20_2.0']
        df['BBL'] = bb['BBL_20_2.0']
        
        curr = df['Close'].iloc[-1]
        sma = df['SMA_20'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        
        # Logic: Price Action + Indicators Confluence
        if curr > sma and rsi < 65:
            return "UP", "Bullish Momentum & SMA Support"
        elif curr < sma and rsi > 35:
            return "DOWN", "Bearish Momentum & SMA Resistance"
        else:
            return "AVOID", "Market Consolidating - No clear breakout"
    except:
        return "ERROR", "Server Data Issue"

@app.route('/api/signals/<asset>')
def api_signals(asset):
    # Weekend check
    if datetime.now().weekday() >= 5:
        return jsonify({"status": "CLOSED", "signal": "MARKET CLOSED"})
    
    signal, confluence = get_signal(asset)
    return jsonify({
        "signal": signal,
        "confluence": confluence,
        "trend": "Bullish" if signal == "UP" else "Bearish" if signal == "DOWN" else "Neutral"
    })

if __name__ == '__main__':
    app.run()
  
