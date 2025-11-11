"""
Buy/Sell Signal Generator based on financial metrics
"""
from typing import Dict, Literal


class SignalGenerator:
    """Generate buy/sell signals based on financial metrics"""
    
    @staticmethod
    def generate_signal(metrics: Dict[str, float]) -> Dict[str, any]:
        """
        Generate buy/sell signal based on multiple metrics
        
        Signal Logic:
        - BUY: Alpha > 0, Beta < 1.5, R² > 0.5, Correlation > 0.5, Volatility < 0.5
        - SELL: Alpha < -0.02, Beta > 1.8, Volatility > 0.7
        - HOLD: Otherwise
        
        Returns:
            Dict with signal, strength, and reasoning
        """
        alpha = metrics.get('alpha', 0)
        beta = metrics.get('beta', 1)
        r_squared = metrics.get('r_squared', 0)
        correlation = metrics.get('correlation', 0)
        volatility = metrics.get('volatility', 0)
        
        buy_score = 0
        sell_score = 0
        reasons = []
        
        # Alpha analysis
        if alpha > 0.05:
            buy_score += 3
            reasons.append(f"Strong positive alpha ({alpha:.2%})")
        elif alpha > 0:
            buy_score += 1
            reasons.append(f"Positive alpha ({alpha:.2%})")
        elif alpha < -0.02:
            sell_score += 2
            reasons.append(f"Negative alpha ({alpha:.2%})")
        
        # Beta analysis
        if 0.8 <= beta <= 1.2:
            buy_score += 2
            reasons.append(f"Moderate beta ({beta:.2f})")
        elif beta > 1.8:
            sell_score += 2
            reasons.append(f"High beta/volatility risk ({beta:.2f})")
        elif beta < 0.5:
            reasons.append(f"Low market sensitivity ({beta:.2f})")
        
        # R² analysis
        if r_squared > 0.7:
            buy_score += 1
            reasons.append(f"Strong index correlation ({r_squared:.2f})")
        elif r_squared < 0.3:
            reasons.append(f"Weak index correlation ({r_squared:.2f})")
        
        # Correlation analysis
        if correlation > 0.6:
            buy_score += 1
            reasons.append(f"Positive market correlation ({correlation:.2f})")
        elif correlation < -0.3:
            sell_score += 1
            reasons.append(f"Negative market correlation ({correlation:.2f})")
        
        # Volatility analysis
        if volatility > 0.7:
            sell_score += 2
            reasons.append(f"High volatility risk ({volatility:.2%})")
        elif volatility < 0.3:
            buy_score += 1
            reasons.append(f"Low volatility ({volatility:.2%})")
        
        # Determine signal
        if buy_score >= 5 and buy_score > sell_score + 2:
            signal = "BUY"
            strength = min(buy_score * 10, 100)
        elif sell_score >= 4 and sell_score > buy_score + 2:
            signal = "SELL"
            strength = min(sell_score * 10, 100)
        else:
            signal = "HOLD"
            strength = 50
        
        return {
            'signal': signal,
            'strength': strength,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'reasons': reasons,
            'metrics': metrics
        }
    
    @staticmethod
    def get_signal_color(signal: str) -> str:
        """Get color for signal display"""
        colors = {
            'BUY': '#10b981',   # Green
            'SELL': '#ef4444',  # Red
            'HOLD': '#f59e0b'   # Yellow
        }
        return colors.get(signal, '#6b7280')
    
    @staticmethod
    def get_signal_icon(signal: str) -> str:
        """Get icon for signal display"""
        icons = {
            'BUY': '📈',
            'SELL': '📉',
            'HOLD': '⏸️'
        }
        return icons.get(signal, '➖')
