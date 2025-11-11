"""
Database module for storing historical price data and trading signals
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json


class Database:
    """Handle database operations for historical data storage"""
    
    def __init__(self, db_path: str = 'trading_data.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                volume INTEGER,
                change_percent REAL
            )
        ''')
        
        # Trading signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal TEXT NOT NULL,
                strength INTEGER,
                metrics TEXT,
                reasons TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                buy_date DATETIME NOT NULL,
                sell_price REAL,
                sell_date DATETIME,
                status TEXT DEFAULT 'OPEN'
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_symbol ON price_history(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_history(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_symbol ON trading_signals(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio(symbol)')
        
        conn.commit()
        conn.close()
    
    def save_price(self, symbol: str, price: float, volume: int = 0, change_percent: float = 0):
        """Save price data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO price_history (symbol, price, volume, change_percent)
            VALUES (?, ?, ?, ?)
        ''', (symbol, price, volume, change_percent))
        
        conn.commit()
        conn.close()
    
    def save_signal(self, symbol: str, signal: str, strength: int, 
                   metrics: Dict, reasons: List[str]):
        """Save trading signal to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metrics_json = json.dumps(metrics)
        reasons_json = json.dumps(reasons)
        
        cursor.execute('''
            INSERT INTO trading_signals (symbol, signal, strength, metrics, reasons)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, signal, strength, metrics_json, reasons_json))
        
        conn.commit()
        conn.close()
    
    def get_historical_prices(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get historical prices for a symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price, timestamp, volume, change_percent
            FROM price_history
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'price': row[0],
                'timestamp': row[1],
                'volume': row[2],
                'change_percent': row[3]
            }
            for row in rows
        ]
    
    def get_latest_signal(self, symbol: str) -> Optional[Dict]:
        """Get latest trading signal for a symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT signal, strength, metrics, reasons, timestamp
            FROM trading_signals
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'signal': row[0],
                'strength': row[1],
                'metrics': json.loads(row[2]),
                'reasons': json.loads(row[3]),
                'timestamp': row[4]
            }
        return None
    
    def add_to_portfolio(self, symbol: str, quantity: int, buy_price: float):
        """Add a position to portfolio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO portfolio (symbol, quantity, buy_price, buy_date)
            VALUES (?, ?, ?, ?)
        ''', (symbol, quantity, buy_price, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def close_position(self, symbol: str, sell_price: float):
        """Close an open position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE portfolio
            SET sell_price = ?, sell_date = ?, status = 'CLOSED'
            WHERE symbol = ? AND status = 'OPEN'
        ''', (sell_price, datetime.now(), symbol))
        
        conn.commit()
        conn.close()
    
    def get_portfolio(self) -> List[Dict]:
        """Get current portfolio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, quantity, buy_price, buy_date, sell_price, sell_date, status
            FROM portfolio
            ORDER BY buy_date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'symbol': row[0],
                'quantity': row[1],
                'buy_price': row[2],
                'buy_date': row[3],
                'sell_price': row[4],
                'sell_date': row[5],
                'status': row[6]
            }
            for row in rows
        ]
    
    def get_portfolio_pnl(self, current_prices: Dict[str, float]) -> Dict:
        """Calculate portfolio P&L"""
        portfolio = self.get_portfolio()
        total_investment = 0
        total_value = 0
        realized_pnl = 0
        unrealized_pnl = 0
        
        for position in portfolio:
            symbol = position['symbol']
            quantity = position['quantity']
            buy_price = position['buy_price']
            
            investment = quantity * buy_price
            total_investment += investment
            
            if position['status'] == 'CLOSED':
                sell_value = quantity * position['sell_price']
                pnl = sell_value - investment
                realized_pnl += pnl
            else:
                current_price = current_prices.get(symbol, buy_price)
                current_value = quantity * current_price
                total_value += current_value
                pnl = current_value - investment
                unrealized_pnl += pnl
        
        total_pnl = realized_pnl + unrealized_pnl
        pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        return {
            'total_investment': round(total_investment, 2),
            'current_value': round(total_value, 2),
            'realized_pnl': round(realized_pnl, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'total_pnl': round(total_pnl, 2),
            'pnl_percent': round(pnl_percent, 2)
        }
