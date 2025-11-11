# Advanced Features Configuration Guide

## Table of Contents
1. [Advanced Technical Indicators](#advanced-technical-indicators)
2. [Database Storage](#database-storage)
3. [WebSocket Real-time Updates](#websocket-real-time-updates)
4. [Smart Alerts](#smart-alerts)
5. [Portfolio Management](#portfolio-management)

---

## Advanced Technical Indicators

### Available Indicators

#### 1. RSI (Relative Strength Index)
- **Range**: 0-100
- **Overbought**: RSI > 70
- **Oversold**: RSI < 30
- **Usage**: Identify potential reversal points

#### 2. MACD (Moving Average Convergence Divergence)
- **Components**: MACD line, Signal line, Histogram
- **Bullish**: MACD crosses above Signal line
- **Bearish**: MACD crosses below Signal line
- **Usage**: Trend following and momentum

#### 3. Bollinger Bands
- **Components**: Upper band, Middle band (SMA), Lower band
- **Signals**: 
  - Price near upper band = Overbought
  - Price near lower band = Oversold
- **Usage**: Volatility and price extremes

#### 4. Moving Averages
- **SMA 20**: Short-term trend
- **SMA 50**: Medium-term trend
- **SMA 200**: Long-term trend
- **EMA 20**: Exponential moving average (more responsive)

### How to Use

The indicators are automatically calculated for each stock. View them in the metrics object:

```python
metrics = {
    'rsi': 45.5,
    'macd': {'macd': 12.5, 'signal': 10.2, 'histogram': 2.3},
    'bollinger_bands': {'upper': 2500, 'middle': 2450, 'lower': 2400},
    'moving_averages': {'sma_20': 2455, 'sma_50': 2430, 'ema_20': 2460}
}
```

---

## Database Storage

### Overview
Historical price data, trading signals, and portfolio positions are stored in SQLite database for:
- Backtesting strategies
- Performance analysis
- Historical signal tracking

### Tables

#### 1. price_history
Stores historical price data for all symbols
```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    price REAL,
    timestamp DATETIME,
    volume INTEGER,
    change_percent REAL
)
```

#### 2. trading_signals  
Stores all generated trading signals
```sql
CREATE TABLE trading_signals (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    signal TEXT,
    strength INTEGER,
    metrics TEXT,
    reasons TEXT,
    timestamp DATETIME
)
```

#### 3. portfolio
Tracks all trading positions
```sql
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    quantity INTEGER,
    buy_price REAL,
    buy_date DATETIME,
    sell_price REAL,
    sell_date DATETIME,
    status TEXT
)
```

### Usage

```python
from database import Database

# Initialize database
db = Database('trading_data.db')

# Save price data
db.save_price('RELIANCE', 2450.50, volume=1000000, change_percent=1.5)

# Save trading signal
db.save_signal('RELIANCE', 'BUY', 75, metrics, reasons)

# Get historical prices
prices = db.get_historical_prices('RELIANCE', limit=100)

# Portfolio management
db.add_to_portfolio('RELIANCE', quantity=100, buy_price=2400)
db.close_position('RELIANCE', sell_price=2450)

# Get P&L
current_prices = {'RELIANCE': 2450, 'TCS': 3650}
pnl = db.get_portfolio_pnl(current_prices)
```

---

## WebSocket Real-time Updates

### Overview
WebSocket provides tick-by-tick real-time market data instead of 30-second polling.

### Setup

1. **Initialize WebSocket client**:
```python
from websocket_client import UpstoxWebSocket

def handle_message(data):
    """Process incoming market data"""
    print(f"Real-time update: {data}")

ws_client = UpstoxWebSocket(api_token, handle_message)
ws_client.connect()
```

2. **Subscribe to symbols**:
```python
symbols = [
    'NSE_EQ|INE002A01018',  # Reliance
    'NSE_INDEX|Nifty 50'     # Nifty 50
]
ws_client.subscribe(symbols, mode='full')
```

3. **Process updates**:
```python
def handle_message(data):
    if 'feeds' in data:
        for symbol, feed in data['feeds'].items():
            ltp = feed['ff']['marketFF']['ltpc']['ltp']
            print(f"{symbol}: ₹{ltp}")
```

### Benefits
- **Real-time**: Instant price updates (milliseconds vs 30 seconds)
- **Efficient**: Push-based instead of pull-based
- **Scalable**: Subscribe to multiple symbols simultaneously

---

## Smart Alerts

### Overview
Get notified via Email or Telegram when strong trading signals are detected.

### Configuration

Add to `.env` file:

```bash
# Email Alerts
ENABLE_EMAIL_ALERTS=True
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient1@example.com,recipient2@example.com

# Telegram Alerts
ENABLE_TELEGRAM_ALERTS=True
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Alert Threshold (only send for signals with strength >= 70%)
SIGNAL_STRENGTH_THRESHOLD=70
```

### Email Setup (Gmail)

1. Enable 2-factor authentication in your Google account
2. Generate an App Password:
   - Go to Google Account → Security → App Passwords
   - Create password for "Mail"
3. Use the generated password in `EMAIL_PASSWORD`

### Telegram Setup

1. Create a bot:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Copy the bot token

2. Get your chat ID:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Copy the "chat" → "id" value

### Usage

```python
from alerts import AlertService

alerts = AlertService()

# Send signal alert
stock_data = {
    'symbol': 'RELIANCE',
    'signal': 'BUY',
    'signal_strength': 85,
    'price': 2450.50,
    'change_percent': 2.5,
    'signal_reasons': ['Strong positive alpha', 'Oversold RSI']
}
alerts.send_signal_alert(stock_data)

# Send portfolio update
pnl_data = {
    'total_investment': 100000,
    'current_value': 105000,
    'total_pnl': 5000,
    'pnl_percent': 5.0
}
alerts.send_portfolio_update(pnl_data)
```

### Alert Types

1. **Signal Alerts**: Sent when BUY/SELL signal strength >= threshold
2. **Portfolio Updates**: Daily P&L summary

---

## Portfolio Management

### Overview
Track your trading positions, calculate P&L, and analyze performance.

### Features

1. **Position Tracking**
   - Record buy transactions
   - Close positions with sell transactions
   - Track open and closed positions

2. **P&L Calculation**
   - Realized P&L (closed positions)
   - Unrealized P&L (open positions)
   - Total P&L and percentage returns

3. **Portfolio Analytics**
   - Total investment
   - Current value
   - Return percentages

### Usage

```python
from database import Database

db = Database()

# Add position
db.add_to_portfolio(
    symbol='RELIANCE',
    quantity=100,
    buy_price=2400.00
)

# Close position
db.close_position(
    symbol='RELIANCE',
    sell_price=2450.00
)

# Get portfolio
portfolio = db.get_portfolio()
for position in portfolio:
    print(f"{position['symbol']}: {position['quantity']} @ ₹{position['buy_price']}")

# Calculate P&L
current_prices = {'RELIANCE': 2475.00, 'TCS': 3680.00}
pnl = db.get_portfolio_pnl(current_prices)

print(f"Total Investment: ₹{pnl['total_investment']:,.2f}")
print(f"Current Value: ₹{pnl['current_value']:,.2f}")
print(f"Realized P&L: ₹{pnl['realized_pnl']:,.2f}")
print(f"Unrealized P&L: ₹{pnl['unrealized_pnl']:,.2f}")
print(f"Total P&L: ₹{pnl['total_pnl']:,.2f} ({pnl['pnl_percent']}%)")
```

### Best Practices

1. **Record all trades**: Always log buy and sell transactions
2. **Review regularly**: Check P&L daily or weekly
3. **Set stop losses**: Use alerts to notify when losses exceed threshold
4. **Diversify**: Don't put all capital in one stock
5. **Track signals**: Compare actual performance vs signal recommendations

---

## Integration with Dashboard

All these features are integrated into the Flask application:

1. **Indicators**: Automatically calculated and displayed on each stock card
2. **Database**: Background storage of all price and signal data
3. **WebSocket**: Optional real-time updates (configure in app.py)
4. **Alerts**: Automatic notifications for strong signals
5. **Portfolio**: API endpoints for portfolio management

### API Endpoints

```
GET /api/portfolio - Get portfolio positions
POST /api/portfolio/add - Add position
POST /api/portfolio/close - Close position
GET /api/portfolio/pnl - Get P&L
GET /api/signals/history - Get signal history
```

---

## Troubleshooting

### Database Issues
- Ensure write permissions in directory
- Check database file isn't locked
- Use `:memory:` for testing

### WebSocket Connection
- Verify API token is valid
- Check network/firewall settings
- Ensure Upstox account has WebSocket access

### Email Alerts Not Sending
- Verify SMTP settings
- Use app-specific password for Gmail
- Check spam folder
- Enable "Less secure app access" if required

### Telegram Alerts Not Working
- Verify bot token is correct
- Ensure you've messaged the bot first
- Check chat ID is correct
- Bot must not be blocked

---

## Next Steps

1. **Backtest** strategies using historical data
2. **Optimize** signal thresholds based on performance
3. **Scale** by adding more stocks
4. **Automate** trading decisions (paper trading first!)
5. **Monitor** performance and refine strategies

For more advanced features, see **ADDON_SUGGESTIONS.md**.
