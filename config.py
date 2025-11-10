"""
Configuration file for Upstox Market Metrics Application
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Upstox API Configuration
UPSTOX_ACCESS_TOKEN = os.getenv('UPSTOX_ACCESS_TOKEN', '')
UPSTOX_API_KEY = os.getenv('UPSTOX_API_KEY', '')

# Upstox API URLs
UPSTOX_WS_URL = "wss://api-v2.upstox.com/feed/market-data-feed/v2"
UPSTOX_REST_API_URL = "https://api-v2.upstox.com"

# Server Configuration
HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Nifty 50 Stock Symbols (Upstox format: NSE_EQ|INE...)
# Using common stock symbols for Nifty 50
NIFTY_50_SYMBOLS = [
    'NSE_INDEX|Nifty 50',  # Nifty Index
    'NSE_EQ|INE040A01034',  # HDFC Bank
    'NSE_EQ|INE002A01018',  # Reliance Industries
    'NSE_EQ|INE009A01021',  # Infosys
    'NSE_EQ|INE467B01029',  # TCS
    'NSE_EQ|INE090A01021',  # ICICI Bank
    'NSE_EQ|INE256A01028',  # Bharti Airtel
    'NSE_EQ|INE066F01012',  # Kotak Mahindra Bank
    'NSE_EQ|INE019A01038',  # Asian Paints
    'NSE_EQ|INE030A01027',  # HCL Technologies
    'NSE_EQ|INE155A01022',  # Titan Company
]

# Simplified list for demonstration - add more as needed
NIFTY_INDEX_SYMBOL = 'NSE_INDEX|Nifty 50'

# Metrics calculation parameters
WINDOW_SIZE = 30  # Number of data points for rolling calculations
ALPHA_THRESHOLD = 0.5  # Threshold for buy signal
BETA_THRESHOLD = 1.5  # High beta threshold
CORRELATION_THRESHOLD = 0.7  # Strong correlation threshold
