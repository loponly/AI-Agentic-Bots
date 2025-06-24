"""
Comprehensive Test Suite for Trading Backtesting System
=======================================================

This test suite validates all aspects of the trading backtesting system using pytest.
"""

import sys
import os
import pytest
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def test_basic_imports():
    """Test that all required modules can be imported."""
    import pandas as pd
    import numpy as np
    import backtrader as bt
    import sqlite3
    
    # If we get here, all imports succeeded
    assert True


def test_data_utils():
    """Test data utilities functionality."""
    from data_utils import generate_synthetic_data, validate_ohlcv_data
    
    # Generate test data
    df = generate_synthetic_data(
        start_date='2023-01-01',
        end_date='2023-01-31',
        initial_price=100,
        seed=42
    )
    
    assert len(df) > 0, "Should generate data"
    
    # Validate data
    validate_ohlcv_data(df)  # Should not raise
    
    # Basic data checks
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    assert all(col in df.columns for col in required_columns), "Missing required columns"


def test_strategy_imports():
    """Test strategy classes."""
    from trading_backtest import (
        SimpleMovingAverageStrategy,
        RSIStrategy,
        BollingerBandsStrategy
    )
    
    # All strategy classes should be importable
    assert SimpleMovingAverageStrategy is not None
    assert RSIStrategy is not None
    assert BollingerBandsStrategy is not None


def test_database_functionality():
    """Test database functionality."""
    from trading_backtest import DatabaseManager
    
    # Create database manager with temporary file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db = DatabaseManager(db_path)
        
        # Test data
        test_results = {
            'strategy_name': 'TestStrategy',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'initial_cash': 100000,
            'final_cash': 105000,
            'total_return': 5000,
            'total_return_pct': 5.0,
            'sharpe_ratio': 1.5,
            'max_drawdown': -2000,
            'max_drawdown_pct': -2.0,
            'total_trades': 10,
            'winning_trades': 6,
            'losing_trades': 4,
            'win_rate': 60.0,
            'avg_trade_return': 500.0,
            'strategy_params': {'test_param': 'test_value'},
            'data_info': {'rows': 31}
        }
        
        # Save to database
        backtest_id = db.save_backtest_result(test_results)
        assert backtest_id is not None
        
    finally:
        # Clean up test database
        if os.path.exists(db_path):
            os.remove(db_path)


def test_modular_structure():
    """Test that the new modular structure works."""
    # Test src package imports
    from src.strategies import SimpleMovingAverageStrategy
    from src.data import DataProvider
    from src.backtesting import BacktestEngine
    
    assert SimpleMovingAverageStrategy is not None
    assert DataProvider is not None
    assert BacktestEngine is not None


def test_backward_compatibility():
    """Test that backward compatibility layer works."""
    from trading_backtest import run_backtest, SimpleMovingAverageStrategy
    from data_utils import generate_synthetic_data
    
    # These imports should work for backward compatibility
    assert run_backtest is not None
    assert SimpleMovingAverageStrategy is not None
    assert generate_synthetic_data is not None


def test_full_backtest_integration():
    """Test complete backtesting workflow with both new and old APIs."""
    # Test new modular API
    from src.data import DataProvider
    from src.backtesting import BacktestEngine
    from src.strategies import SimpleMovingAverageStrategy
    
    provider = DataProvider()
    data_feed = provider.generate_synthetic(
        start_date='2023-01-01',
        end_date='2023-03-31',
        initial_price=100,
        seed=42
    )
    
    engine = BacktestEngine(initial_cash=10000)
    results = engine.run_backtest(
        data_feed=data_feed,
        strategy_class=SimpleMovingAverageStrategy,
        strategy_params={'short_period': 5, 'long_period': 15}
    )
    
    # Validate new API results
    assert 'strategy_name' in results
    assert 'total_return_pct' in results
    assert 'total_trades' in results
    assert isinstance(results['total_return_pct'], (int, float))
    
    # Test backward compatibility API
    from trading_backtest import run_backtest
    from data_utils import generate_synthetic_data
    
    data = generate_synthetic_data(
        start_date='2023-01-01',
        end_date='2023-03-31',
        initial_price=100,
        seed=42
    )
    
    compat_results = run_backtest(
        data=data,
        strategy_class=SimpleMovingAverageStrategy,
        initial_cash=10000,
        strategy_params={'short_period': 5, 'long_period': 15},
        save_to_db=False
    )
    
    # Validate backward compatibility results
    assert 'strategy_name' in compat_results
    assert 'total_return_pct' in compat_results
    assert 'total_trades' in compat_results
    assert isinstance(compat_results['total_return_pct'], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
