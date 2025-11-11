"""
Upstox API Client for fetching Nifty 50 and Index data
"""
import requests
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class UpstoxClient:
    """Client for interacting with Upstox API"""
    
    BASE_URL = "https://api.upstox.com/v2"
    TIMEOUT = 5  # 5 second timeout for API calls
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize Upstox client with API token"""
        self.api_token = api_token or os.getenv('UPSTOX_API_TOKEN')
        if not self.api_token:
            raise ValueError("Upstox API token is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        # Nifty 50 stock symbols (sample - expand as needed)
        self.nifty50_symbols = [
            'NSE_EQ|INE002A01018',  # Reliance
            'NSE_EQ|INE467B01029',  # TCS
            'NSE_EQ|INE040A01034',  # HDFC Bank
            'NSE_EQ|INE009A01021',  # Infosys
            'NSE_EQ|INE030A01027',  # ICICI Bank
            'NSE_EQ|INE090A01021',  # Bharti Airtel
            'NSE_EQ|INE769A01020',  # Axis Bank
            'NSE_EQ|INE062A01020',  # State Bank
            'NSE_EQ|INE154A01025',  # ITC
            'NSE_EQ|INE101D01020',  # Bajaj Finance
        ]
        
        self.nifty_index = 'NSE_INDEX|Nifty 50'
    
    def get_market_quote(self, symbol: str) -> Dict:
        """Get market quote for a symbol"""
        url = f"{self.BASE_URL}/market-quote/quotes"
        params = {'symbol': symbol}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, interval: str = '1day', 
                           from_date: str = None, to_date: str = None) -> Dict:
        """Get historical candle data for a symbol"""
        url = f"{self.BASE_URL}/historical-candle/{symbol}/{interval}/{to_date}/{from_date}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return {}
    
    def get_nifty50_quotes(self) -> List[Dict]:
        """Get quotes for all Nifty 50 stocks"""
        quotes = []
        for symbol in self.nifty50_symbols:
            quote = self.get_market_quote(symbol)
            if quote:
                quotes.append(quote)
            time.sleep(0.1)  # Rate limiting
        return quotes
    
    def get_nifty_index_quote(self) -> Dict:
        """Get Nifty index quote"""
        return self.get_market_quote(self.nifty_index)
    
    def get_intraday_data(self, symbol: str) -> Dict:
        """Get intraday candle data"""
        url = f"{self.BASE_URL}/market-quote/ohlc"
        params = {'symbol': symbol, 'interval': '1minute'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching intraday data for {symbol}: {e}")
            return {}
