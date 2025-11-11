"""
Financial Metrics Calculator
Computes Alpha, Beta, R², Correlation, Volatility, and Elasticity
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class MetricsCalculator:
    """Calculate financial metrics for stocks"""
    
    @staticmethod
    def calculate_returns(prices: List[float]) -> np.ndarray:
        """Calculate percentage returns from prices"""
        prices_array = np.array(prices)
        returns = np.diff(prices_array) / prices_array[:-1]
        return returns
    
    @staticmethod
    def calculate_beta(stock_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """
        Calculate Beta - Market sensitivity
        Beta = Covariance(Stock, Market) / Variance(Market)
        """
        if len(stock_returns) != len(market_returns):
            min_len = min(len(stock_returns), len(market_returns))
            stock_returns = stock_returns[:min_len]
            market_returns = market_returns[:min_len]
        
        covariance = np.cov(stock_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 0.0
        
        return covariance / market_variance
    
    @staticmethod
    def calculate_alpha(stock_returns: np.ndarray, market_returns: np.ndarray, 
                       beta: float, risk_free_rate: float = 0.06) -> float:
        """
        Calculate Alpha - Extra return beyond market expectation
        Alpha = Stock_Return - (Risk_Free_Rate + Beta * (Market_Return - Risk_Free_Rate))
        """
        avg_stock_return = np.mean(stock_returns)
        avg_market_return = np.mean(market_returns)
        
        # Annualized returns (assuming daily data)
        annual_stock_return = avg_stock_return * 252
        annual_market_return = avg_market_return * 252
        
        expected_return = risk_free_rate + beta * (annual_market_return - risk_free_rate)
        alpha = annual_stock_return - expected_return
        
        return alpha
    
    @staticmethod
    def calculate_r_squared(stock_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """
        Calculate R² - How much movement explained by index
        R² is the square of correlation coefficient
        """
        if len(stock_returns) != len(market_returns):
            min_len = min(len(stock_returns), len(market_returns))
            stock_returns = stock_returns[:min_len]
            market_returns = market_returns[:min_len]
        
        correlation = np.corrcoef(stock_returns, market_returns)[0, 1]
        r_squared = correlation ** 2
        
        return r_squared if not np.isnan(r_squared) else 0.0
    
    @staticmethod
    def calculate_correlation(stock_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """
        Calculate Correlation (ρ) - Direction & strength of movement
        """
        if len(stock_returns) != len(market_returns):
            min_len = min(len(stock_returns), len(market_returns))
            stock_returns = stock_returns[:min_len]
            market_returns = market_returns[:min_len]
        
        correlation = np.corrcoef(stock_returns, market_returns)[0, 1]
        
        return correlation if not np.isnan(correlation) else 0.0
    
    @staticmethod
    def calculate_volatility(returns: np.ndarray) -> float:
        """
        Calculate Volatility (σ) - Intraday risk
        Annualized standard deviation of returns
        """
        std_dev = np.std(returns)
        # Annualize (assuming daily data)
        annualized_volatility = std_dev * np.sqrt(252)
        
        return annualized_volatility
    
    @staticmethod
    def calculate_elasticity(stock_price: float, index_price: float, beta: float) -> float:
        """
        Calculate Elasticity - ₹ change per Nifty point
        Elasticity = (Stock_Price / Index_Price) * Beta
        """
        if index_price == 0:
            return 0.0
        
        elasticity = (stock_price / index_price) * beta
        
        return elasticity
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI)
        RSI > 70 = Overbought, RSI < 30 = Oversold
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI if insufficient data
        
        prices_array = np.array(prices)
        deltas = np.diff(prices_array)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, 
                      slow_period: int = 26, signal_period: int = 9) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        Returns: {'macd': value, 'signal': value, 'histogram': value}
        """
        if len(prices) < slow_period + signal_period:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
        
        prices_array = np.array(prices)
        
        # Calculate EMAs
        ema_fast = pd.Series(prices_array).ewm(span=fast_period, adjust=False).mean()
        ema_slow = pd.Series(prices_array).ewm(span=slow_period, adjust=False).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': round(float(macd_line.iloc[-1]), 4),
            'signal': round(float(signal_line.iloc[-1]), 4),
            'histogram': round(float(histogram.iloc[-1]), 4)
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, 
                                  std_dev: int = 2) -> Dict[str, float]:
        """
        Calculate Bollinger Bands
        Returns: {'upper': value, 'middle': value, 'lower': value, 'bandwidth': value}
        """
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return {
                'upper': current_price,
                'middle': current_price,
                'lower': current_price,
                'bandwidth': 0.0
            }
        
        prices_array = np.array(prices[-period:])
        middle_band = np.mean(prices_array)
        std = np.std(prices_array)
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        bandwidth = (upper_band - lower_band) / middle_band * 100 if middle_band != 0 else 0
        
        return {
            'upper': round(upper_band, 2),
            'middle': round(middle_band, 2),
            'lower': round(lower_band, 2),
            'bandwidth': round(bandwidth, 2)
        }
    
    @staticmethod
    def calculate_moving_averages(prices: List[float]) -> Dict[str, float]:
        """
        Calculate various Moving Averages
        Returns: {'sma_20': value, 'sma_50': value, 'sma_200': value, 'ema_20': value}
        """
        prices_series = pd.Series(prices)
        
        result = {}
        
        # Simple Moving Averages
        if len(prices) >= 20:
            result['sma_20'] = round(float(prices_series.rolling(window=20).mean().iloc[-1]), 2)
        else:
            result['sma_20'] = round(float(np.mean(prices)), 2)
        
        if len(prices) >= 50:
            result['sma_50'] = round(float(prices_series.rolling(window=50).mean().iloc[-1]), 2)
        else:
            result['sma_50'] = round(float(np.mean(prices)), 2)
        
        if len(prices) >= 200:
            result['sma_200'] = round(float(prices_series.rolling(window=200).mean().iloc[-1]), 2)
        else:
            result['sma_200'] = round(float(np.mean(prices)), 2)
        
        # Exponential Moving Average
        if len(prices) >= 20:
            result['ema_20'] = round(float(prices_series.ewm(span=20, adjust=False).mean().iloc[-1]), 2)
        else:
            result['ema_20'] = round(float(np.mean(prices)), 2)
        
        return result
    
    @classmethod
    def calculate_all_metrics(cls, stock_prices: List[float], market_prices: List[float],
                             current_stock_price: float, current_index_price: float) -> Dict[str, float]:
        """
        Calculate all metrics for a stock
        
        Returns:
            Dict with keys: alpha, beta, r_squared, correlation, volatility, elasticity,
                           rsi, macd, bollinger_bands, moving_averages
        """
        stock_returns = cls.calculate_returns(stock_prices)
        market_returns = cls.calculate_returns(market_prices)
        
        beta = cls.calculate_beta(stock_returns, market_returns)
        alpha = cls.calculate_alpha(stock_returns, market_returns, beta)
        r_squared = cls.calculate_r_squared(stock_returns, market_returns)
        correlation = cls.calculate_correlation(stock_returns, market_returns)
        volatility = cls.calculate_volatility(stock_returns)
        elasticity = cls.calculate_elasticity(current_stock_price, current_index_price, beta)
        
        # Advanced indicators
        rsi = cls.calculate_rsi(stock_prices)
        macd = cls.calculate_macd(stock_prices)
        bollinger = cls.calculate_bollinger_bands(stock_prices)
        moving_avgs = cls.calculate_moving_averages(stock_prices)
        
        return {
            'alpha': round(alpha, 4),
            'beta': round(beta, 4),
            'r_squared': round(r_squared, 4),
            'correlation': round(correlation, 4),
            'volatility': round(volatility, 4),
            'elasticity': round(elasticity, 4),
            'rsi': rsi,
            'macd': macd,
            'bollinger_bands': bollinger,
            'moving_averages': moving_avgs
        }
