# DeepBest - Nifty 50 Market Metrics Analysis

Real-time market metrics calculator for Nifty 50 stocks using Upstox API. This application calculates Alpha, Beta, R², Correlation, Volatility, and Elasticity metrics to generate buy/sell signals.

## Features

- **Real-time Data Streaming**: WebSocket connection to Upstox API for live market data
- **Advanced Metrics Calculation**:
  - **Alpha**: Extra return beyond market expectation
  - **Beta**: Market sensitivity
  - **R²**: How much movement explained by index
  - **Correlation (ρ)**: Direction & strength of movement
  - **Volatility (σ)**: Intraday risk
  - **Elasticity**: ₹ change per Nifty point
- **Buy/Sell Signals**: Automated trading signals based on calculated metrics
- **Web Dashboard**: Real-time visualization with WebSocket updates
- **REST API**: Endpoints for programmatic access

## Requirements

- Python 3.8+
- Upstox API Account with valid access token
- Modern web browser

## Installation

1. Clone the repository:
```bash
git clone https://github.com/deepuchoice3-source/deepbest.git
cd deepbest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Quick Start Options:**

   **Option A: Demo Mode (No Upstox Account Required)**
   ```bash
   python3 mock_server.py
   ```
   Opens http://localhost:5000 with simulated market data

   **Option B: Real Market Data (Requires Upstox Account)**
   
   First, get your Upstox access token:
   ```bash
   python3 get_token.py
   ```
   
   This interactive script will:
   - Guide you through Upstox OAuth authorization
   - Generate your access token
   - Automatically update your .env file
   
   Then start the application:
   ```bash
   python3 app.py
   # OR use the startup script
   ./start.sh
   ```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## Getting Upstox Access Token

### Easy Method (Recommended)
Run the included helper script:
```bash
python3 get_token.py
```

This interactive script handles the OAuth flow and automatically updates your `.env` file.

### Manual Method
1. Register at [Upstox Developer Console](https://account.upstox.com/developer/apps)
2. Create a new app to get API Key and Secret
3. Use OAuth 2.0 flow to generate access token
4. Add the access token to `.env` file

**Note:** Access tokens expire after 24 hours and need to be regenerated.

## Usage

### Demo Mode (Testing Without Upstox)

```bash
python3 demo.py        # Console-based metrics demo
python3 mock_server.py # Web dashboard with simulated data
```

### Production Mode (Real Market Data)

```bash
./start.sh    # Interactive startup script
# OR
python3 app.py
```

The server will start on `http://localhost:5000`

### Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

### Using the Dashboard

1. **Start Stream**: Click "Start Stream" button to begin receiving real-time market data
2. **View Metrics**: Monitor calculated metrics for each Nifty 50 stock
3. **Trading Signals**: Observe BUY/SELL/HOLD signals based on metrics
4. **Stop Stream**: Click "Stop Stream" to pause data updates

### API Endpoints

#### Get Current Metrics
```bash
GET /api/metrics
```

Returns all calculated metrics for subscribed stocks.

#### Start Data Stream
```bash
GET /api/start
```

Starts the Upstox WebSocket connection.

#### Stop Data Stream
```bash
GET /api/stop
```

Stops the Upstox WebSocket connection.

## Metrics Explanation

| Metric              | Meaning                                | Ideal For                       |
| ------------------- | -------------------------------------- | ------------------------------- |
| **Alpha**           | Extra return beyond market expectation | Detect strong stocks            |
| **Beta**            | Market sensitivity                     | Volatility exposure             |
| **R²**              | How much movement explained by index   | Hedging or correlation strength |
| **Correlation (ρ)** | Direction & strength of movement       | Pair trading, diversification   |
| **Volatility (σ)**  | Intraday risk                          | Position sizing & stop loss     |
| **Elasticity**      | ₹ change per Nifty point               | Hedge ratio estimation          |

## Trading Signal Logic

### BUY Signal
- Alpha > 0.5 (positive excess return)
- Beta < 1.5 (moderate volatility)
- Correlation > 0.7 (strong correlation with index)

### SELL Signal
- Alpha < -0.5 (negative excess return)
- Volatility > 0.5 (high risk)

### HOLD Signal
- All other conditions

## Project Structure

```
deepbest/
├── app.py                    # Main Flask application (production)
├── mock_server.py           # Demo server with simulated data
├── config.py                # Configuration settings
├── upstox_client.py        # Upstox WebSocket client
├── metrics_calculator.py   # Metrics calculation logic
├── demo.py                 # Console demo with simulated data
├── get_token.py            # Helper to generate Upstox access token
├── start.sh                # Interactive startup script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── templates/
│   └── index.html         # Web dashboard UI
├── README.md              # This file
└── QUICKSTART.md         # Quick start guide
```

## Configuration

Edit `config.py` to customize:

- `WINDOW_SIZE`: Number of data points for rolling calculations (default: 30)
- `ALPHA_THRESHOLD`: Threshold for buy signal (default: 0.5)
- `BETA_THRESHOLD`: High beta threshold (default: 1.5)
- `CORRELATION_THRESHOLD`: Strong correlation threshold (default: 0.7)
- `NIFTY_50_SYMBOLS`: List of stock symbols to monitor

## WebSocket Events

### Client → Server
- `connect`: Establish connection
- `request_metrics`: Request current metrics
- `disconnect`: Close connection

### Server → Client
- `connection_response`: Connection acknowledgment
- `metrics_update`: Single stock metric update
- `metrics_batch`: Multiple stocks metrics

## Technology Stack

- **Backend**: Flask, Flask-SocketIO
- **WebSocket**: python-socketio, websocket-client
- **Data Processing**: NumPy, Pandas, SciPy
- **Frontend**: Vanilla JavaScript, Socket.IO client
- **API**: Upstox Market Data Feed API v2

## Troubleshooting

### WebSocket Connection Failed
- Verify your Upstox access token is valid and not expired
- Check internet connectivity
- Ensure firewall allows WebSocket connections

### No Data Received
- Confirm market hours (Indian stock market: 9:15 AM - 3:30 PM IST)
- Verify stock symbols are correctly formatted
- Check Upstox API subscription includes market data

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher

## Disclaimer

This application is for educational and research purposes only. It is not financial advice. Always conduct thorough research and consult with financial advisors before making investment decisions.

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Support

For issues and questions:
- Open an issue on GitHub
- Check Upstox API documentation: https://upstox.com/developer/api-documentation

## Author

DeepBest Team

## Changelog

### Version 1.0.0 (2025-11-10)
- Initial release
- Real-time market data streaming from Upstox API
- Calculation of 6 key metrics (Alpha, Beta, R², Correlation, Volatility, Elasticity)
- Web dashboard with live updates
- Buy/Sell/Hold signal generation
- REST API endpoints
