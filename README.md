# deepbest

**Real-time Nifty 50 Trading Dashboard** with Financial Metrics Analysis and Buy/Sell Signals

## Features

🚀 **Live Market Data** - Real-time Nifty 50 index and stock prices via Upstox API  
📊 **Interactive Charts** - Dynamic Plotly charts showing intraday price movements  
📈 **Financial Metrics** - Comprehensive analysis with 6 key metrics  
💡 **Smart Signals** - Automated buy/sell/hold signals based on multi-factor analysis  
🎨 **Beautiful UI** - Modern, responsive dashboard with real-time updates  

## Financial Metrics Reference

| Metric              | Meaning                                | Ideal For                       |
| ------------------- | -------------------------------------- | ------------------------------- |
| **Alpha (α)**       | Extra return beyond market expectation | Detect strong stocks            |
| **Beta (β)**        | Market sensitivity                     | Volatility exposure             |
| **R²**              | How much movement explained by index   | Hedging or correlation strength |
| **Correlation (ρ)** | Direction & strength of movement       | Pair trading, diversification   |
| **Volatility (σ)**  | Intraday risk                          | Position sizing & stop loss     |
| **Elasticity**      | ₹ change per Nifty point               | Hedge ratio estimation          |

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Upstox API account and access token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/deepuchoice3-source/deepbest.git
   cd deepbest
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment (Optional)**
   ```bash
   cp .env.example .env
   # Edit .env and add your Upstox API token
   ```
   
   Note: The token is already configured in `app.py`, but you can override it via `.env` file.

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

## How It Works

### 1. Data Collection
- Connects to Upstox API using provided access token
- Fetches real-time quotes for Nifty 50 index and constituent stocks
- Retrieves historical price data for metric calculations

### 2. Metrics Calculation
For each stock, the system calculates:

- **Alpha**: Measures excess returns compared to market expectations
- **Beta**: Indicates stock's volatility relative to the market
- **R²**: Shows how much of stock's movement is explained by the index
- **Correlation**: Measures directional relationship with the market
- **Volatility**: Quantifies price fluctuation and risk
- **Elasticity**: Estimates rupee change per Nifty point movement

### 3. Signal Generation
The algorithm analyzes all metrics to generate trading signals:

**BUY Signal** - When:
- Positive alpha (outperforming market)
- Moderate beta (0.8-1.2)
- High R² (>0.7) and correlation (>0.6)
- Low volatility (<0.3)

**SELL Signal** - When:
- Negative alpha (<-0.02)
- High beta (>1.8) or volatility (>0.7)
- Negative correlation (<-0.3)

**HOLD Signal** - All other conditions

### 4. Visualization
- Real-time dashboard with auto-refresh every 30 seconds
- Interactive Plotly charts for price movements
- Color-coded cards showing metrics and signals
- Detailed reasoning for each signal

## Project Structure

```
deepbest/
├── app.py                    # Flask web application
├── upstox_client.py          # Upstox API integration
├── metrics_calculator.py     # Financial metrics computation
├── signal_generator.py       # Buy/sell signal logic
├── templates/
│   └── index.html           # Dashboard UI
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/nifty-index` - Get current Nifty 50 index data
- `GET /api/stocks` - Get all stocks with metrics and signals
- `GET /api/chart/<symbol>` - Get historical chart data for a symbol

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Data Processing**: NumPy, Pandas
- **API Integration**: Upstox API, Requests
- **Visualization**: Plotly.js
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## Notes

- The application uses the Upstox API token provided in the code
- Data refreshes automatically every 30 seconds
- Mock data is used as fallback when API calls fail
- The signal generation algorithm is based on standard financial analysis techniques

## Future Enhancements

- WebSocket support for real-time streaming
- More sophisticated ML-based signal generation
- Portfolio tracking and backtesting
- Additional technical indicators (RSI, MACD, Moving Averages)
- Alert notifications for strong buy/sell signals
- Historical performance tracking

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This tool is for educational and informational purposes only. Always do your own research and consult with financial advisors before making investment decisions. Past performance does not guarantee future results.
