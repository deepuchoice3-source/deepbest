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
    
    @classmethod
    def calculate_all_metrics(cls, stock_prices: List[float], market_prices: List[float],
                             current_stock_price: float, current_index_price: float) -> Dict[str, float]:
        """
        Calculate all metrics for a stock
        
        Returns:
            Dict with keys: alpha, beta, r_squared, correlation, volatility, elasticity
        """
        stock_returns = cls.calculate_returns(stock_prices)
        market_returns = cls.calculate_returns(market_prices)
        
        beta = cls.calculate_beta(stock_returns, market_returns)
        alpha = cls.calculate_alpha(stock_returns, market_returns, beta)
        r_squared = cls.calculate_r_squared(stock_returns, market_returns)
        correlation = cls.calculate_correlation(stock_returns, market_returns)
        volatility = cls.calculate_volatility(stock_returns)
        elasticity = cls.calculate_elasticity(current_stock_price, current_index_price, beta)
        
        return {
            'alpha': round(alpha, 4),
            'beta': round(beta, 4),
            'r_squared': round(r_squared, 4),
            'correlation': round(correlation, 4),
            'volatility': round(volatility, 4),
            'elasticity': round(elasticity, 4)
        }
