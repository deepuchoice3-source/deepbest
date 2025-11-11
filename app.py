"""
Flask web application for displaying Nifty 50 metrics and signals
"""
from flask import Flask, render_template, jsonify
import os
from datetime import datetime, timedelta
from upstox_client import UpstoxClient
from metrics_calculator import MetricsCalculator
from signal_generator import SignalGenerator
import numpy as np

app = Flask(__name__)

# Initialize Upstox client with the provided token
UPSTOX_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2S0FBWTgiLCJqdGkiOiI2OTEzMDQ1MGQ4YTc1MTYyOGRjODU4YjMiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaWF0IjoxNzYyODUzOTY4LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NjI4OTg0MDB9.GWzlm2tLuGUPuEN8OAhD6r-UprsbqvevzHyZbtJesWA"

# Use mock data by default for demo purposes
USE_MOCK_DATA = True

try:
    if not USE_MOCK_DATA:
        upstox_client = UpstoxClient(api_token=UPSTOX_TOKEN)
    else:
        upstox_client = None
        print("Using mock data for demonstration")
except Exception as e:
    print(f"Error initializing Upstox client: {e}. Using mock data.")
    upstox_client = None


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/nifty-index')
def get_nifty_index():
    """Get Nifty index current data"""
    # Always use mock data for demo
    return jsonify({
        'symbol': 'Nifty 50',
        'price': 24500.50 + np.random.randn() * 50,
        'change': 125.30 + np.random.randn() * 20,
        'change_percent': 0.51 + np.random.randn() * 0.1,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stocks')
def get_stocks():
    """Get all Nifty 50 stocks with metrics and signals"""
    # Use mock data for demo
    return jsonify(get_mock_stocks_data())


@app.route('/api/chart/<symbol>')
def get_chart_data(symbol):
    """Get historical chart data for a symbol"""
    # Generate mock intraday data
    now = datetime.now()
    data_points = []
    
    base_price = 24500 if symbol == 'NIFTY' else 1500
    
    for i in range(100):
        timestamp = now - timedelta(minutes=100-i)
        price = base_price * (1 + np.random.randn() * 0.002)
        
        data_points.append({
            'timestamp': timestamp.isoformat(),
            'price': round(price, 2),
            'volume': int(np.random.randint(1000, 10000))
        })
    
    return jsonify(data_points)


def get_mock_stocks_data():
    """Generate mock data for demonstration"""
    stocks = [
        {'name': 'RELIANCE', 'base_price': 2450},
        {'name': 'TCS', 'base_price': 3650},
        {'name': 'HDFCBANK', 'base_price': 1650},
        {'name': 'INFY', 'base_price': 1450},
        {'name': 'ICICIBANK', 'base_price': 1050},
        {'name': 'BHARTIARTL', 'base_price': 1200},
        {'name': 'AXISBANK', 'base_price': 1100},
        {'name': 'SBIN', 'base_price': 750},
        {'name': 'ITC', 'base_price': 450},
        {'name': 'BAJFINANCE', 'base_price': 6800},
    ]
    
    nifty_prices = [24500 * (1 + np.random.randn() * 0.01) for _ in range(30)]
    
    stocks_data = []
    for stock in stocks:
        stock_prices = [stock['base_price'] * (1 + np.random.randn() * 0.015) for _ in range(30)]
        
        metrics = MetricsCalculator.calculate_all_metrics(
            stock_prices, nifty_prices, stock['base_price'], 24500
        )
        
        signal_data = SignalGenerator.generate_signal(metrics)
        
        stocks_data.append({
            'symbol': stock['name'],
            'price': stock['base_price'],
            'change': round(np.random.randn() * 20, 2),
            'change_percent': round(np.random.randn() * 1.5, 2),
            'metrics': metrics,
            'signal': signal_data['signal'],
            'signal_strength': signal_data['strength'],
            'signal_reasons': signal_data['reasons']
        })
    
    return stocks_data


if __name__ == '__main__':
    # Note: Debug mode is enabled for development. 
    # For production, set debug=False or use a production WSGI server like Gunicorn
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
