"""
Market Metrics Calculator
Calculates Alpha, Beta, R², Correlation, Volatility, and Elasticity
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate market metrics for stocks vs index"""
    
    def __init__(self, window_size: int = 30):
        """
        Initialize metrics calculator
        
        Args:
            window_size: Number of data points for rolling calculations
        """
        self.window_size = window_size
        self.price_data = {}  # {symbol: [prices]}
        self.returns_data = {}  # {symbol: [returns]}
        
    def add_price_data(self, symbol: str, price: float, timestamp: float):
        """
        Add new price data point
        
        Args:
            symbol: Stock symbol
            price: Current price
            timestamp: Timestamp of the price
        """
        if symbol not in self.price_data:
            self.price_data[symbol] = []
            
        self.price_data[symbol].append({
            'price': price,
            'timestamp': timestamp
        })
        
        # Keep only the required window size
        if len(self.price_data[symbol]) > self.window_size + 1:
            self.price_data[symbol] = self.price_data[symbol][-(self.window_size + 1):]
    
    def calculate_returns(self, symbol: str) -> np.ndarray:
        """
        Calculate returns for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Array of returns
        """
        if symbol not in self.price_data or len(self.price_data[symbol]) < 2:
            return np.array([])
        
        prices = np.array([p['price'] for p in self.price_data[symbol]])
        returns = np.diff(prices) / prices[:-1]
        
        return returns
    
    def calculate_metrics(self, stock_symbol: str, index_symbol: str) -> Dict:
        """
        Calculate all metrics for a stock vs index
        
        Args:
            stock_symbol: Stock symbol
            index_symbol: Index symbol
            
        Returns:
            Dictionary with all calculated metrics
        """
        # Get returns
        stock_returns = self.calculate_returns(stock_symbol)
        index_returns = self.calculate_returns(index_symbol)
        
        # Need minimum data points
        if len(stock_returns) < 5 or len(index_returns) < 5:
            return self._empty_metrics()
        
        # Ensure same length
        min_len = min(len(stock_returns), len(index_returns))
        stock_returns = stock_returns[-min_len:]
        index_returns = index_returns[-min_len:]
        
        # Calculate Beta using linear regression
        beta, alpha_value = self._calculate_beta_alpha(stock_returns, index_returns)
        
        # Calculate R-squared
        r_squared = self._calculate_r_squared(stock_returns, index_returns)
        
        # Calculate Correlation
        correlation = self._calculate_correlation(stock_returns, index_returns)
        
        # Calculate Volatility (annualized)
        volatility = self._calculate_volatility(stock_returns)
        
        # Calculate Elasticity (price change per index point)
        elasticity = self._calculate_elasticity(stock_symbol, index_symbol)
        
        # Generate signal
        signal = self._generate_signal(alpha_value, beta, correlation, volatility)
        
        return {
            'symbol': stock_symbol,
            'alpha': round(alpha_value, 4),
            'beta': round(beta, 4),
            'r_squared': round(r_squared, 4),
            'correlation': round(correlation, 4),
            'volatility': round(volatility, 4),
            'elasticity': round(elasticity, 4),
            'signal': signal,
            'last_price': self.price_data[stock_symbol][-1]['price'] if stock_symbol in self.price_data else 0
        }
    
    def _calculate_beta_alpha(self, stock_returns: np.ndarray, index_returns: np.ndarray) -> Tuple[float, float]:
        """Calculate Beta and Alpha using linear regression"""
        try:
            slope, intercept, _, _, _ = stats.linregress(index_returns, stock_returns)
            beta = slope
            
            # Alpha = Average stock return - Beta * Average index return
            alpha = np.mean(stock_returns) - beta * np.mean(index_returns)
            
            # Annualize alpha (assuming daily data, 252 trading days)
            alpha_annualized = alpha * 252
            
            return beta, alpha_annualized
        except Exception as e:
            logger.error(f"Error calculating beta/alpha: {e}")
            return 1.0, 0.0
    
    def _calculate_r_squared(self, stock_returns: np.ndarray, index_returns: np.ndarray) -> float:
        """Calculate R-squared (coefficient of determination)"""
        try:
            correlation = np.corrcoef(stock_returns, index_returns)[0, 1]
            r_squared = correlation ** 2
            return r_squared
        except Exception as e:
            logger.error(f"Error calculating R-squared: {e}")
            return 0.0
    
    def _calculate_correlation(self, stock_returns: np.ndarray, index_returns: np.ndarray) -> float:
        """Calculate Pearson correlation coefficient"""
        try:
            correlation = np.corrcoef(stock_returns, index_returns)[0, 1]
            return correlation
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    def _calculate_volatility(self, returns: np.ndarray) -> float:
        """Calculate annualized volatility (standard deviation of returns)"""
        try:
            # Annualize volatility (assuming daily data, 252 trading days)
            volatility = np.std(returns) * np.sqrt(252)
            return volatility
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def _calculate_elasticity(self, stock_symbol: str, index_symbol: str) -> float:
        """
        Calculate elasticity: rupee change in stock per point change in index
        
        Elasticity = (Change in Stock Price / Change in Index Points)
        """
        try:
            if (stock_symbol not in self.price_data or index_symbol not in self.price_data or
                len(self.price_data[stock_symbol]) < 2 or len(self.price_data[index_symbol]) < 2):
                return 0.0
            
            stock_prices = np.array([p['price'] for p in self.price_data[stock_symbol]])
            index_prices = np.array([p['price'] for p in self.price_data[index_symbol]])
            
            # Calculate average change ratio
            min_len = min(len(stock_prices), len(index_prices))
            stock_changes = np.diff(stock_prices[-min_len:])
            index_changes = np.diff(index_prices[-min_len:])
            
            # Avoid division by zero
            valid_indices = index_changes != 0
            if not np.any(valid_indices):
                return 0.0
            
            elasticity = np.mean(stock_changes[valid_indices] / index_changes[valid_indices])
            
            return elasticity
        except Exception as e:
            logger.error(f"Error calculating elasticity: {e}")
            return 0.0
    
    def _generate_signal(self, alpha: float, beta: float, correlation: float, volatility: float) -> str:
        """
        Generate buy/sell/hold signal based on metrics
        
        Buy Signal:
        - Positive alpha (outperforming market)
        - Beta < 1.5 (not too volatile)
        - High correlation (>0.7)
        
        Sell Signal:
        - Negative alpha (underperforming market)
        - Very high volatility
        
        Args:
            alpha: Alpha value
            beta: Beta value
            correlation: Correlation coefficient
            volatility: Volatility value
            
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        # Buy conditions
        if alpha > 0.5 and beta < 1.5 and correlation > 0.7:
            return 'BUY'
        
        # Sell conditions
        if alpha < -0.5 or volatility > 0.5:
            return 'SELL'
        
        return 'HOLD'
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'symbol': '',
            'alpha': 0.0,
            'beta': 0.0,
            'r_squared': 0.0,
            'correlation': 0.0,
            'volatility': 0.0,
            'elasticity': 0.0,
            'signal': 'HOLD',
            'last_price': 0.0
        }
