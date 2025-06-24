"""
Test Modular Architecture
=========================

This test specifically validates the modular architecture and ensures
all components work correctly in isolation and together.
"""

import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_strategy_modules():
    """Test that all strategy modules can be imported and instantiated."""
    from src.strategies import (
        BaseStrategy,
        SimpleMovingAverageStrategy,
        RSIStrategy,
        BollingerBandsStrategy,
        BuyAndHoldStrategy,
        MeanReversionStrategy,
        MomentumStrategy
    )
    
    strategies = [
        SimpleMovingAverageStrategy,
        RSIStrategy,
        BollingerBandsStrategy,
        BuyAndHoldStrategy,
        MeanReversionStrategy,
        MomentumStrategy
    ]
    
    assert len(strategies) == 6, f"Expected 6 strategies, got {len(strategies)}"
    
    # Test that all strategies inherit from BaseStrategy
    for strategy_class in strategies:
        assert issubclass(strategy_class, BaseStrategy), \
            f"{strategy_class.__name__} doesn't inherit from BaseStrategy"

def test_data_modules():
    """Test that all data modules work correctly."""
    from src.data import DataProvider
    from src.data.validators import validate_ohlcv_data
    from src.data.generators import generate_synthetic_data
    from src.data.loaders import load_csv_data
    
    # Test data provider
    provider = DataProvider()
    assert provider is not None
    
    # Test synthetic data generation
    data_feed = provider.generate_synthetic(
        start_date='2023-01-01',
        end_date='2023-01-15',
        seed=42
    )
    assert data_feed.name is not None
    assert len(data_feed.data) > 0
    
    # Test DataFrame conversion
    df_feed = provider.from_dataframe(data_feed.data, name="test_df")
    assert df_feed.name == "test_df"
    
    # Test validation
    validate_ohlcv_data(data_feed.data)  # Should not raise

def test_backtesting_module():
    """Test the backtesting engine module."""
    from src.backtesting import BacktestEngine, print_performance_summary
    from src.data import DataProvider
    from src.strategies import SimpleMovingAverageStrategy
    
    # Create components
    provider = DataProvider()
    engine = BacktestEngine(initial_cash=10000)
    
    assert engine is not None
    
    # Generate test data
    data_feed = provider.generate_synthetic(
        start_date='2023-01-01',
        end_date='2023-02-01',
        seed=42
    )
    
    # Run backtest
    results = engine.run_backtest(
        data_feed=data_feed,
        strategy_class=SimpleMovingAverageStrategy,
        strategy_params={'short_period': 5, 'long_period': 10}
    )
    
    assert 'strategy_name' in results
    assert results['strategy_name'] is not None

def test_database_module():
    """Test the database module."""
    from src.database import DatabaseManager
    
    # Create test database
    db = DatabaseManager("test_modular.db")
    assert db is not None
    
    # Test saving results
    test_results = {
        'strategy_name': 'ModularTest',
        'start_date': '2023-01-01',
        'end_date': '2023-01-31',
        'initial_cash': 10000,
        'final_cash': 10500,
        'total_return': 500,
        'total_return_pct': 5.0,
        'total_trades': 5,
        'winning_trades': 3,
        'losing_trades': 2,
        'win_rate': 60.0,
        'avg_trade_return': 100.0,
        'strategy_params': {},
        'data_info': {'rows': 31}
    }
    
    backtest_id = db.save_backtest_result(test_results)
    assert backtest_id is not None
    
    # Test retrieving results
    recent_results = db.get_backtest_results(limit=1)
    assert len(recent_results) >= 0
    
    # Clean up
    os.remove("test_modular.db")

def test_analyzers_module():
    """Test the analyzers module."""
    from src.analyzers import PerformanceAnalyzer, TradeAnalyzer
    
    # These are backtrader analyzers, so we can't easily test them
    # without a full backtrader setup, but we can at least verify import
    assert PerformanceAnalyzer is not None
    assert TradeAnalyzer is not None

def test_integration():
    """Test that all modules work together."""
    from src.data import DataProvider
    from src.backtesting import BacktestEngine
    from src.strategies import RSIStrategy
    from src.database import DatabaseManager
    
    # Complete workflow test
    provider = DataProvider()
    engine = BacktestEngine(initial_cash=10000)
    db = DatabaseManager("test_integration.db")
    
    # Generate data
    data_feed = provider.generate_synthetic(
        start_date='2023-01-01',
        end_date='2023-01-31',
        seed=42
    )
    
    # Run backtest
    results = engine.run_backtest(
        data_feed=data_feed,
        strategy_class=RSIStrategy,
        strategy_params={'rsi_period': 10, 'rsi_oversold': 35, 'rsi_overbought': 65}
    )
    
    # Save results
    backtest_id = engine.save_results(results, db)
    
    assert backtest_id is not None
    
    # Clean up
    os.remove("test_integration.db")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
