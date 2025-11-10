"""
Mock server for testing the web application without real Upstox credentials
"""
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import threading
import numpy as np
import logging
from metrics_calculator import MetricsCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
metrics_calc = MetricsCalculator(window_size=30)
latest_metrics = {}
is_running = False
mock_thread = None


def generate_mock_price(base_price, volatility=0.01):
    """Generate mock price with random walk"""
    return base_price * (1 + np.random.normal(0, volatility))


def mock_data_stream():
    """Generate mock market data stream"""
    global latest_metrics, is_running
    
    logger.info("Starting mock data stream...")
    
    # Initial prices
    stocks = {
        'NSE_EQ|RELIANCE': 2500,
        'NSE_EQ|HDFCBANK': 1600,
        'NSE_EQ|INFY': 1450,
        'NSE_EQ|TCS': 3500,
        'NSE_EQ|ICICIBANK': 950,
        'NSE_EQ|BHARTI': 850,
        'NSE_EQ|KOTAKBANK': 1800,
        'NSE_EQ|ASIANPAINT': 3200,
        'NSE_EQ|HCLTECH': 1200,
        'NSE_EQ|TITAN': 3100,
    }
    
    nifty_price = 19500
    index_symbol = 'NSE_INDEX|Nifty 50'
    
    iteration = 0
    while is_running:
        try:
            iteration += 1
            timestamp = time.time()
            
            # Generate index price
            nifty_price = generate_mock_price(nifty_price, volatility=0.01)
            metrics_calc.add_price_data(index_symbol, nifty_price, timestamp)
            
            # Generate stock prices
            for symbol, base_price in stocks.items():
                new_price = generate_mock_price(base_price, volatility=0.015)
                stocks[symbol] = new_price
                metrics_calc.add_price_data(symbol, new_price, timestamp)
                
                # Calculate metrics after some data points
                if iteration > 10:
                    metrics = metrics_calc.calculate_metrics(symbol, index_symbol)
                    latest_metrics[symbol] = metrics
                    
                    # Emit update to connected clients
                    socketio.emit('metrics_update', metrics)
            
            logger.info(f"Generated mock data for {len(stocks)} stocks (iteration {iteration})")
            
            # Wait before next update
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error in mock data stream: {e}")
            break
    
    logger.info("Mock data stream stopped")


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get current metrics"""
    return jsonify({
        'metrics': list(latest_metrics.values()),
        'timestamp': time.time(),
        'is_running': is_running
    })


@app.route('/api/start')
def start_stream():
    """API endpoint to start mock data stream"""
    global is_running, mock_thread
    
    if not is_running:
        is_running = True
        mock_thread = threading.Thread(target=mock_data_stream)
        mock_thread.daemon = True
        mock_thread.start()
        return jsonify({'status': 'started', 'mode': 'mock'})
    return jsonify({'status': 'already running', 'mode': 'mock'})


@app.route('/api/stop')
def stop_stream():
    """API endpoint to stop mock data stream"""
    global is_running
    is_running = False
    return jsonify({'status': 'stopped'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connection_response', {'status': 'connected', 'mode': 'mock'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')


@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle request for current metrics"""
    emit('metrics_batch', {
        'metrics': list(latest_metrics.values()),
        'timestamp': time.time()
    })


if __name__ == '__main__':
    logger.info("Starting mock server on localhost:5000")
    logger.info("This is a DEMO mode - using simulated market data")
    logger.info("Access the dashboard at http://localhost:5000")
    
    # Run Flask server with SocketIO
    socketio.run(app, host='localhost', port=5000, debug=True, allow_unsafe_werkzeug=True)
