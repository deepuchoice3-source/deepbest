"""
Upstox WebSocket Client for Real-time Market Data
"""
import json
import websocket
import threading
import time
from typing import Callable, Dict, Any
import struct
import base64
from google.protobuf.json_format import MessageToDict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpstoxWebSocket:
    """WebSocket client for Upstox Market Data Feed"""
    
    def __init__(self, access_token: str, symbols: list):
        """
        Initialize Upstox WebSocket client
        
        Args:
            access_token: Upstox API access token
            symbols: List of instrument symbols to subscribe
        """
        self.access_token = access_token
        self.symbols = symbols
        self.ws = None
        self.on_message_callback = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    def connect(self, on_message: Callable[[Dict[str, Any]], None]):
        """
        Connect to Upstox WebSocket
        
        Args:
            on_message: Callback function for market data updates
        """
        self.on_message_callback = on_message
        
        # WebSocket URL with authorization
        ws_url = f"wss://api-v2.upstox.com/feed/market-data-feed/v2?access_token={self.access_token}"
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # Start WebSocket in a separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
    def _on_open(self, ws):
        """Handle WebSocket connection open"""
        logger.info("WebSocket connection established")
        self.is_connected = True
        self.reconnect_attempts = 0
        
        # Subscribe to symbols
        self._subscribe_symbols()
        
    def _subscribe_symbols(self):
        """Subscribe to market data for symbols"""
        if not self.symbols:
            return
            
        subscription_message = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": self.symbols
            }
        }
        
        try:
            self.ws.send(json.dumps(subscription_message))
            logger.info(f"Subscribed to {len(self.symbols)} symbols")
        except Exception as e:
            logger.error(f"Error subscribing to symbols: {e}")
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            # Check if message is binary or text
            if isinstance(message, bytes):
                # Parse binary protobuf message
                data = self._parse_binary_message(message)
            else:
                # Parse JSON message
                data = json.loads(message)
            
            if self.on_message_callback and data:
                self.on_message_callback(data)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _parse_binary_message(self, message: bytes) -> Dict:
        """
        Parse binary protobuf message from Upstox
        
        For this implementation, we'll use a simplified parser.
        In production, you should use the official protobuf schema.
        """
        try:
            # Simplified parsing - extract key data
            # This is a placeholder - actual implementation would use protobuf schema
            return {"type": "binary", "raw_data": message.hex()}
        except Exception as e:
            logger.error(f"Error parsing binary message: {e}")
            return {}
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        self.is_connected = False
        
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        self.is_connected = False
        
        # Attempt reconnection
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            time.sleep(2 ** self.reconnect_attempts)  # Exponential backoff
            self.connect(self.on_message_callback)
    
    def unsubscribe(self, symbols: list = None):
        """Unsubscribe from symbols"""
        symbols_to_unsub = symbols or self.symbols
        
        unsubscribe_message = {
            "guid": "someguid",
            "method": "unsub",
            "data": {
                "mode": "full",
                "instrumentKeys": symbols_to_unsub
            }
        }
        
        if self.ws and self.is_connected:
            self.ws.send(json.dumps(unsubscribe_message))
            logger.info(f"Unsubscribed from {len(symbols_to_unsub)} symbols")
    
    def close(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
            self.is_connected = False
