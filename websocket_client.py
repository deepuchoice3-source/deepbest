"""
WebSocket client for real-time market data streaming from Upstox
"""
import websocket
import json
import threading
from typing import Callable, List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class UpstoxWebSocket:
    """WebSocket client for real-time Upstox market data"""
    
    def __init__(self, api_token: str, on_message_callback: Callable = None):
        """Initialize WebSocket client"""
        self.api_token = api_token
        self.on_message_callback = on_message_callback
        self.ws = None
        self.is_connected = False
        self.subscribed_symbols = []
        
        # Upstox WebSocket URL
        self.ws_url = "wss://api.upstox.com/v2/feed/market-data-feed/authorize"
    
    def connect(self):
        """Connect to Upstox WebSocket"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Accept': 'application/json'
            }
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header=headers,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            print("WebSocket connection initiated")
            return True
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")
            return False
    
    def _on_open(self, ws):
        """Handle WebSocket connection opened"""
        self.is_connected = True
        print("WebSocket connected successfully")
        
        # Subscribe to symbols if any were added before connection
        if self.subscribed_symbols:
            self.subscribe(self.subscribed_symbols)
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Process the message
            if self.on_message_callback:
                self.on_message_callback(data)
            else:
                self._default_message_handler(data)
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
    
    def _default_message_handler(self, data: Dict):
        """Default message handler"""
        # Extract relevant data from message
        if 'feeds' in data:
            for symbol, feed_data in data['feeds'].items():
                if 'ff' in feed_data:  # Full feed
                    market_data = feed_data['ff']['marketFF']
                    ltp = market_data.get('ltpc', {}).get('ltp', 0)
                    print(f"{symbol}: ₹{ltp}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket error"""
        print(f"WebSocket error: {error}")
        self.is_connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        print(f"WebSocket closed: {close_msg}")
        self.is_connected = False
    
    def subscribe(self, symbols: List[str], mode: str = "full"):
        """
        Subscribe to symbols for real-time data
        
        Args:
            symbols: List of instrument keys (e.g., ['NSE_EQ|INE002A01018'])
            mode: 'full' for complete data or 'ltpc' for last traded price only
        """
        if not self.is_connected:
            print("WebSocket not connected. Storing symbols for later subscription.")
            self.subscribed_symbols.extend(symbols)
            return
        
        try:
            subscribe_message = {
                "guid": "someguid",
                "method": "sub",
                "data": {
                    "mode": mode,
                    "instrumentKeys": symbols
                }
            }
            
            self.ws.send(json.dumps(subscribe_message))
            self.subscribed_symbols.extend(symbols)
            print(f"Subscribed to {len(symbols)} symbols")
        except Exception as e:
            print(f"Error subscribing to symbols: {e}")
    
    def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols"""
        if not self.is_connected:
            print("WebSocket not connected")
            return
        
        try:
            unsubscribe_message = {
                "guid": "someguid",
                "method": "unsub",
                "data": {
                    "instrumentKeys": symbols
                }
            }
            
            self.ws.send(json.dumps(unsubscribe_message))
            
            # Remove from subscribed list
            for symbol in symbols:
                if symbol in self.subscribed_symbols:
                    self.subscribed_symbols.remove(symbol)
            
            print(f"Unsubscribed from {len(symbols)} symbols")
        except Exception as e:
            print(f"Error unsubscribing from symbols: {e}")
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()
            self.is_connected = False
            print("WebSocket disconnected")


# Example usage
if __name__ == "__main__":
    def message_handler(data):
        """Custom message handler"""
        print(f"Received: {json.dumps(data, indent=2)}")
    
    # Initialize WebSocket client
    token = os.getenv('UPSTOX_API_TOKEN')
    ws_client = UpstoxWebSocket(token, message_handler)
    
    # Connect
    ws_client.connect()
    
    # Subscribe to symbols
    symbols = [
        'NSE_EQ|INE002A01018',  # Reliance
        'NSE_INDEX|Nifty 50'    # Nifty 50
    ]
    ws_client.subscribe(symbols)
    
    # Keep running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws_client.disconnect()
