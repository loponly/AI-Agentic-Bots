"""
Backward Compatibility Layer
===========================

This module provides backward compatibility for the old API while using the new modular structure.
"""

import pandas as pd
import backtrader as bt
from typing import Dict, Any, Optional, Type
import sys
import os

# Add current directory to path to enable imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.data.providers import DataProvider
    from src.backtesting.engine import BacktestEngine, print_performance_summary
    from src.database.manager import DatabaseManager
    
    # Re-export important classes for backward compatibility
    from src.strategies import (
        SimpleMovingAverageStrategy,
        RSIStrategy,
        BollingerBandsStrategy,
        BuyAndHoldStrategy,
        MeanReversionStrategy,
        MomentumStrategy
    )
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    IMPORTS_SUCCESSFUL = False


def create_data_feed(df: pd.DataFrame) -> bt.feeds.PandasData:
    """
    Create a backtrader data feed from a pandas DataFrame.
    
    Args:
        df: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
        
    Returns:
        Backtrader data feed object
    """
    # Ensure date column is datetime and set as index
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Sort by date
    df.sort_index(inplace=True)
    
    # Create data feed
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # Use index
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=None
    )
    
    return data


def run_backtest(
    data: pd.DataFrame,
    strategy_class: Type[bt.Strategy],
    initial_cash: float = 100000.0,
    commission: float = 0.001,
    strategy_params: Optional[Dict[str, Any]] = None,
    save_to_db: bool = True
) -> Dict[str, Any]:
    """
    Run a backtest with the specified parameters (backward compatibility function).
    
    Args:
        data: DataFrame with OHLCV data
        strategy_class: Strategy class to use
        initial_cash: Starting cash amount
        commission: Commission rate (default 0.1%)
        strategy_params: Parameters to pass to strategy
        save_to_db: Whether to save results to database
        
    Returns:
        Dictionary containing backtest results
    """
    if not IMPORTS_SUCCESSFUL:
        raise ImportError("Required modules could not be imported. Please check your installation.")
        
    # Create data provider and convert DataFrame to DataFeed
    data_provider = DataProvider()
    data_feed = data_provider.from_dataframe(data)
    
    # Create and run backtest
    engine = BacktestEngine(initial_cash=initial_cash, commission=commission)
    results = engine.run_backtest(
        data_feed=data_feed,
        strategy_class=strategy_class,
        strategy_params=strategy_params
    )
    
    # Save to database if requested
    if save_to_db:
        db_manager = DatabaseManager()
        backtest_id = engine.save_results(results, db_manager)
        results['backtest_id'] = backtest_id
        print(f"Results saved to database with ID: {backtest_id}")
    
    return results


if IMPORTS_SUCCESSFUL:
    __all__ = [
        'run_backtest',
        'create_data_feed',
        'print_performance_summary',
        'DatabaseManager',
        'SimpleMovingAverageStrategy',
        'RSIStrategy', 
        'BollingerBandsStrategy',
        'BuyAndHoldStrategy',
        'MeanReversionStrategy',
        'MomentumStrategy'
    ]
else:
    __all__ = [
        'run_backtest',
        'create_data_feed'
    ]
