"""
Main application - Flask server with WebSocket for real-time metrics
"""
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import threading
import logging
from typing import Dict, Any
import config
from upstox_client import UpstoxWebSocket
from metrics_calculator import MetricsCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
upstox_ws = None
metrics_calc = MetricsCalculator(window_size=config.WINDOW_SIZE)
latest_metrics = {}
is_running = False


def on_market_data(data: Dict[str, Any]):
    """
    Callback for market data from Upstox WebSocket
    
    Args:
        data: Market data dictionary
    """
    global latest_metrics
    
    try:
        # Parse market data
        # Note: Actual data format depends on Upstox API response
        # This is a simplified implementation
        
        if isinstance(data, dict):
            # Extract symbol and price from data
            # Upstox sends data in specific format - adjust as needed
            symbol = data.get('symbol', '')
            price = data.get('ltp', 0) or data.get('last_price', 0)
            timestamp = time.time()
            
            if symbol and price:
                # Add price data to calculator
                metrics_calc.add_price_data(symbol, price, timestamp)
                
                # Calculate metrics for stocks (not for index itself)
                if symbol != config.NIFTY_INDEX_SYMBOL:
                    metrics = metrics_calc.calculate_metrics(symbol, config.NIFTY_INDEX_SYMBOL)
                    latest_metrics[symbol] = metrics
                    
                    # Emit update to connected clients
                    socketio.emit('metrics_update', metrics)
                    logger.info(f"Updated metrics for {symbol}: {metrics['signal']}")
                    
    except Exception as e:
        logger.error(f"Error processing market data: {e}")


def start_upstox_stream():
    """Start Upstox WebSocket stream"""
    global upstox_ws, is_running
    
    if not config.UPSTOX_ACCESS_TOKEN:
        logger.error("Upstox access token not configured!")
        return
    
    try:
        upstox_ws = UpstoxWebSocket(
            access_token=config.UPSTOX_ACCESS_TOKEN,
            symbols=config.NIFTY_50_SYMBOLS
        )
        upstox_ws.connect(on_market_data)
        is_running = True
        logger.info("Upstox stream started successfully")
    except Exception as e:
        logger.error(f"Error starting Upstox stream: {e}")
        is_running = False


def stop_upstox_stream():
    """Stop Upstox WebSocket stream"""
    global upstox_ws, is_running
    
    if upstox_ws:
        upstox_ws.close()
        is_running = False
        logger.info("Upstox stream stopped")


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
    """API endpoint to start data stream"""
    if not is_running:
        thread = threading.Thread(target=start_upstox_stream)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already running'})


@app.route('/api/stop')
def stop_stream():
    """API endpoint to stop data stream"""
    stop_upstox_stream()
    return jsonify({'status': 'stopped'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connection_response', {'status': 'connected'})


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
    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    
    # Start Upstox stream in background
    stream_thread = threading.Thread(target=start_upstox_stream)
    stream_thread.daemon = True
    stream_thread.start()
    
    # Run Flask server with SocketIO
    socketio.run(app, host=config.HOST, port=config.PORT, debug=config.DEBUG)
