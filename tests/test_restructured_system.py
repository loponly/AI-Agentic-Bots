"""
Final Test Script - Restructured Trading Backtesting System
==========================================================

This script tests the restructured system to ensure everything is working correctly.
"""

import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_new_modular_imports():
    """Test importing from the new modular structure."""
    from src.strategies import SimpleMovingAverageStrategy, RSIStrategy
    from src.data import DataProvider
    from src.backtesting import BacktestEngine
    from src.database import DatabaseManager
    
    # If we get here, all imports succeeded
    assert True

def test_backward_compatibility():
    """Test backward compatibility layer."""
    from trading_backtest import SimpleMovingAverageStrategy, run_backtest
    from data_utils import generate_synthetic_data
    
    # If we get here, all imports succeeded
    assert True

def test_end_to_end():
    """Test complete end-to-end functionality."""
    # Test with new structure
    from src.data import DataProvider
    from src.backtesting import BacktestEngine
    from src.strategies import SimpleMovingAverageStrategy
    
    data_provider = DataProvider()
    data_feed = data_provider.generate_synthetic(
        start_date='2023-01-01',
        end_date='2023-02-01',
        seed=42
    )
    
    engine = BacktestEngine(initial_cash=10000)
    results = engine.run_backtest(
        data_feed=data_feed,
        strategy_class=SimpleMovingAverageStrategy,
        strategy_params={'short_period': 5, 'long_period': 10}
    )
    
    # Assert we got results and they have the expected structure
    assert 'total_return_pct' in results
    assert isinstance(results['total_return_pct'], (int, float))
    
    # Test with backward compatibility
    from trading_backtest import run_backtest
    from data_utils import generate_synthetic_data
    
    data = generate_synthetic_data(
        start_date='2023-01-01',
        end_date='2023-02-01',
        seed=42
    )
    
    results_compat = run_backtest(
        data, 
        SimpleMovingAverageStrategy,
        initial_cash=10000,
        save_to_db=False,
        strategy_params={'short_period': 5, 'long_period': 10}
    )
    
    # Assert backward compatibility results
    assert 'total_return_pct' in results_compat
    assert isinstance(results_compat['total_return_pct'], (int, float))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
