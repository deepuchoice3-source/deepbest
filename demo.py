"""
Demo script to test metrics calculation with simulated data
This allows testing without real Upstox API credentials
"""
import time
import numpy as np
from metrics_calculator import MetricsCalculator

def generate_simulated_price(base_price, volatility, correlation_with_index, index_return):
    """
    Generate simulated stock price based on index movement
    
    Args:
        base_price: Current stock price
        volatility: Stock volatility
        correlation_with_index: Correlation with index
        index_return: Index return percentage
    
    Returns:
        New simulated price
    """
    # Generate correlated return
    random_component = np.random.normal(0, volatility)
    stock_return = correlation_with_index * index_return + random_component
    
    new_price = base_price * (1 + stock_return)
    return new_price


def simulate_market_data():
    """Simulate market data and calculate metrics"""
    
    print("=" * 80)
    print("DeepBest Market Metrics Calculator - Demo Mode")
    print("=" * 80)
    print()
    
    # Initialize calculator
    calc = MetricsCalculator(window_size=30)
    
    # Simulated stocks
    stocks = {
        'RELIANCE': {'price': 2500, 'beta': 1.2, 'volatility': 0.02, 'correlation': 0.85},
        'HDFCBANK': {'price': 1600, 'beta': 0.9, 'volatility': 0.015, 'correlation': 0.90},
        'INFY': {'price': 1450, 'beta': 1.1, 'volatility': 0.018, 'correlation': 0.88},
        'TCS': {'price': 3500, 'beta': 1.0, 'volatility': 0.016, 'correlation': 0.92},
        'ICICIBANK': {'price': 950, 'beta': 1.3, 'volatility': 0.025, 'correlation': 0.87},
    }
    
    # Nifty index
    nifty_price = 19500
    index_symbol = 'NIFTY50'
    
    print("Simulating 40 time periods of market data...")
    print()
    
    # Simulate 40 time periods
    for i in range(40):
        timestamp = time.time() + i * 60  # 1 minute intervals
        
        # Generate index return
        index_return = np.random.normal(0, 0.01)  # 1% volatility
        nifty_price = nifty_price * (1 + index_return)
        
        # Add index price
        calc.add_price_data(index_symbol, nifty_price, timestamp)
        
        # Generate stock prices
        for symbol, params in stocks.items():
            new_price = generate_simulated_price(
                params['price'],
                params['volatility'],
                params['correlation'],
                index_return
            )
            params['price'] = new_price
            calc.add_price_data(symbol, new_price, timestamp)
        
        # Calculate and display metrics every 10 periods
        if i > 0 and (i + 1) % 10 == 0:
            print(f"\n--- Period {i + 1} Metrics ---")
            print(f"Nifty Index: ₹{nifty_price:.2f}")
            print()
            
            for symbol in stocks.keys():
                metrics = calc.calculate_metrics(symbol, index_symbol)
                print(f"{symbol:12} | Price: ₹{metrics['last_price']:8.2f} | "
                      f"Alpha: {metrics['alpha']:7.4f} | "
                      f"Beta: {metrics['beta']:6.4f} | "
                      f"R²: {metrics['r_squared']:6.4f} | "
                      f"ρ: {metrics['correlation']:6.4f} | "
                      f"σ: {metrics['volatility']:6.4f} | "
                      f"Signal: {metrics['signal']:4}")
    
    # Final metrics
    print()
    print("=" * 80)
    print("FINAL METRICS SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Stock':<12} {'Price':>10} {'Alpha':>8} {'Beta':>8} {'R²':>8} {'ρ':>8} {'σ':>8} {'Elast':>8} {'Signal':>8}")
    print("-" * 80)
    
    for symbol in stocks.keys():
        metrics = calc.calculate_metrics(symbol, index_symbol)
        print(f"{symbol:<12} "
              f"₹{metrics['last_price']:>9.2f} "
              f"{metrics['alpha']:>8.4f} "
              f"{metrics['beta']:>8.4f} "
              f"{metrics['r_squared']:>8.4f} "
              f"{metrics['correlation']:>8.4f} "
              f"{metrics['volatility']:>8.4f} "
              f"{metrics['elasticity']:>8.4f} "
              f"{metrics['signal']:>8}")
    
    print()
    print("=" * 80)
    print("Metric Explanations:")
    print("  Alpha:       Extra return beyond market expectation (annualized)")
    print("  Beta:        Market sensitivity (1.0 = moves with market)")
    print("  R²:          How much movement explained by index (0-1)")
    print("  ρ:           Correlation coefficient (-1 to 1)")
    print("  σ:           Volatility / Risk (annualized)")
    print("  Elast:       ₹ change per Nifty point")
    print("=" * 80)
    print()
    
    # Trading signals explanation
    print("Trading Signal Logic:")
    print("  BUY:  Alpha > 0.5, Beta < 1.5, Correlation > 0.7")
    print("  SELL: Alpha < -0.5 or Volatility > 0.5")
    print("  HOLD: All other conditions")
    print()


if __name__ == '__main__':
    simulate_market_data()
