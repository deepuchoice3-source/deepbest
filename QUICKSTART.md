# Quick Start Guide

## Option 1: Demo Mode (No Upstox Account Required)

If you want to test the application without Upstox credentials:

```bash
# Install dependencies
pip install -r requirements.txt

# Run mock server with simulated data
python3 mock_server.py
```

Then open your browser to `http://localhost:5000`

Click "Start Stream" to see simulated market data and metrics.

## Option 2: With Upstox API (Real Market Data)

### Step 1: Get Upstox API Credentials

1. Go to [Upstox Developer Console](https://account.upstox.com/developer/apps)
2. Register/Login to your account
3. Create a new app:
   - App Name: DeepBest (or any name)
   - Redirect URL: http://localhost:5000
4. Note down your **API Key** and **API Secret**

### Step 2: Generate Access Token

Run this Python script to generate access token:

```python
# Upstox uses OAuth 2.0 authentication
# Follow these steps:

# 1. Visit this URL in your browser (replace YOUR_API_KEY):
# https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=YOUR_API_KEY&redirect_uri=http://localhost:5000

# 2. Login and authorize the app
# 3. You'll be redirected to: http://localhost:5000?code=YOUR_AUTH_CODE
# 4. Copy the code parameter from the URL

# 5. Exchange the code for access token using POST request
import requests

api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"
auth_code = "YOUR_AUTH_CODE"

response = requests.post(
    "https://api.upstox.com/v2/login/authorization/token",
    headers={"accept": "application/json"},
    data={
        "code": auth_code,
        "client_id": api_key,
        "client_secret": api_secret,
        "redirect_uri": "http://localhost:5000",
        "grant_type": "authorization_code"
    }
)

token_data = response.json()
access_token = token_data.get("access_token")
print(f"Access Token: {access_token}")
```

### Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

Add your credentials:
```
UPSTOX_ACCESS_TOKEN=your_actual_access_token_here
UPSTOX_API_KEY=your_api_key_here
```

### Step 4: Run Application

```bash
# Using startup script
./start.sh

# OR directly
python3 app.py
```

Access dashboard at `http://localhost:5000`

## Usage Guide

### Dashboard Features

1. **Connection Status**: Shows if connected to data feed (green = connected)
2. **Start Stream**: Begins receiving real-time market data
3. **Stop Stream**: Pauses data updates
4. **Metrics Table**: Displays all calculated metrics for each stock
5. **Signals**: BUY/SELL/HOLD recommendations based on metrics

### Understanding the Metrics

- **Alpha**: Shows if stock is outperforming the market
  - Positive = beating the market
  - Negative = underperforming

- **Beta**: Measures volatility relative to market
  - < 1.0 = Less volatile than market
  - = 1.0 = Moves with market
  - > 1.0 = More volatile than market

- **R²**: How closely stock follows the index
  - 0.0-0.3 = Weak relationship
  - 0.3-0.7 = Moderate relationship
  - 0.7-1.0 = Strong relationship

- **Correlation**: Direction and strength of relationship
  - -1.0 to 0 = Negative correlation
  - 0 to +1.0 = Positive correlation

- **Volatility**: Annualized risk measure
  - Lower = Less risky
  - Higher = More risky

- **Elasticity**: How much stock price changes per Nifty point
  - Useful for hedging calculations

### Trading Signals

- **BUY**: Alpha > 0.5, Beta < 1.5, Correlation > 0.7
  - Stock is outperforming with manageable risk
  
- **SELL**: Alpha < -0.5 OR Volatility > 0.5
  - Stock is underperforming or too risky
  
- **HOLD**: All other conditions
  - Wait for better opportunity

## Testing Without Market Hours

Use the demo mode or `demo.py` script:

```bash
python3 demo.py
```

This generates 40 periods of simulated market data and shows metrics calculation in action.

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Port 5000 already in use
Edit `config.py` and change `PORT = 5000` to another port like `5001`

### WebSocket connection fails
- Check if access token is valid (tokens expire)
- Verify internet connection
- Check if Upstox API is accessible

### No data appearing
- Ensure it's market hours (9:15 AM - 3:30 PM IST)
- Check if subscription includes market data
- Verify stock symbols are correct

## API Endpoints

### GET /api/metrics
Returns current metrics for all stocks

### GET /api/start
Starts the data stream

### GET /api/stop
Stops the data stream

## WebSocket Events

Listen to these events for real-time updates:

- `metrics_update`: Single stock update
- `metrics_batch`: Batch of all stocks
- `connection_response`: Connection status

## Support

For issues:
1. Check logs in console
2. Verify .env configuration
3. Test with demo mode first
4. Review Upstox API documentation
