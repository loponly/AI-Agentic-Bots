"""
Database Manager
===============

This module handles SQLite database operations for storing backtest results.
"""

import sqlite3
import json
from typing import Dict, Any


class DatabaseManager:
    """Handles SQLite database operations for storing backtest results."""
    
    def __init__(self, db_path: str = "backtest_results.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create backtest results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                initial_cash REAL NOT NULL,
                final_cash REAL NOT NULL,
                total_return REAL NOT NULL,
                total_return_pct REAL NOT NULL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                max_drawdown_pct REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                avg_trade_return REAL,
                strategy_params TEXT,
                data_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_id INTEGER,
                entry_date TEXT,
                exit_date TEXT,
                entry_price REAL,
                exit_price REAL,
                size REAL,
                pnl REAL,
                pnl_pct REAL,
                trade_duration INTEGER,
                FOREIGN KEY (backtest_id) REFERENCES backtest_results (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_backtest_result(self, results: Dict[str, Any]) -> int:
        """
        Save backtest results to database.
        
        Args:
            results: Dictionary containing backtest results
            
        Returns:
            Database ID of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backtest_results 
            (strategy_name, start_date, end_date, initial_cash, final_cash,
             total_return, total_return_pct, sharpe_ratio, max_drawdown,
             max_drawdown_pct, total_trades, winning_trades, losing_trades,
             win_rate, avg_trade_return, strategy_params, data_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            results['strategy_name'],
            results['start_date'],
            results['end_date'],
            results['initial_cash'],
            results['final_cash'],
            results['total_return'],
            results['total_return_pct'],
            results.get('sharpe_ratio'),
            results.get('max_drawdown'),
            results.get('max_drawdown_pct'),
            results.get('total_trades', 0),
            results.get('winning_trades', 0),
            results.get('losing_trades', 0),
            results.get('win_rate', 0),
            results.get('avg_trade_return', 0),
            json.dumps(results.get('strategy_params', {})),
            json.dumps(results.get('data_info', {}))
        ))
        
        backtest_id = cursor.lastrowid
        
        # Save individual trades if available
        if 'trades' in results:
            for trade in results['trades']:
                cursor.execute('''
                    INSERT INTO trades 
                    (backtest_id, entry_date, exit_date, entry_price, exit_price,
                     size, pnl, pnl_pct, trade_duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    backtest_id,
                    trade['entry_date'],
                    trade['exit_date'],
                    trade['entry_price'],
                    trade['exit_price'],
                    trade['size'],
                    trade['pnl'],
                    trade['pnl_pct'],
                    trade['trade_duration']
                ))
        
        conn.commit()
        conn.close()
        
        return backtest_id
        
    def get_backtest_results(self, limit: int = 10) -> list:
        """
        Retrieve recent backtest results from database.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of backtest result dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM backtest_results 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
        
    def get_trades(self, backtest_id: int) -> list:
        """
        Retrieve trades for a specific backtest.
        
        Args:
            backtest_id: ID of the backtest
            
        Returns:
            List of trade dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE backtest_id = ?
            ORDER BY entry_date
        ''', (backtest_id,))
        
        trades = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in trades]
