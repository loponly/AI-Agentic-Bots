"""
Test Script for Trading Backtesting System
==========================================

This script tests the basic functionality of the trading backtesting system.
Run this to verify that everything is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        import backtrader as bt
        print("✓ backtrader imported successfully")
    except ImportError as e:
        print(f"✗ backtrader import failed: {e}")
        return False
    
    try:
        import sqlite3
        print("✓ sqlite3 imported successfully")
    except ImportError as e:
        print(f"✗ sqlite3 import failed: {e}")
        return False
    
    return True


def test_data_utils():
    """Test data utilities functionality."""
    print("\nTesting data utilities...")
    
    try:
        from data_utils import generate_synthetic_data, validate_ohlcv_data
        
        # Generate test data
        df = generate_synthetic_data(
            start_date='2023-01-01',
            end_date='2023-01-31',
            initial_price=100,
            seed=42
        )
        
        print(f"✓ Generated synthetic data: {len(df)} rows")
        
        # Validate data
        validate_ohlcv_data(df)
        print("✓ Data validation passed")
        
        # Basic data checks
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required_columns):
            print(f"✓ Data structure valid: {len(df)} rows with all required columns")
        else:
            raise ValueError("Missing required columns")
        
        return True, df
        
    except Exception as e:
        print(f"✗ Data utilities test failed: {e}")
        return False, None


def test_strategies():
    """Test strategy classes."""
    print("\nTesting strategy classes...")
    
    try:
        from trading_backtest import (
            SimpleMovingAverageStrategy,
            RSIStrategy,
            BollingerBandsStrategy
        )
        
        print("✓ All strategy classes imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Strategy import failed: {e}")
        return False


def test_database():
    """Test database functionality."""
    print("\nTesting database...")
    
    try:
        from trading_backtest import DatabaseManager
        
        # Create database manager
        db = DatabaseManager("test_backtest.db")
        print("✓ Database manager created")
        
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
        print(f"✓ Test results saved to database with ID: {backtest_id}")
        
        # Clean up test database
        os.remove("test_backtest.db")
        print("✓ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_full_backtest():
    """Test complete backtesting workflow."""
    print("\nTesting full backtest...")
    
    try:
        from trading_backtest import run_backtest, SimpleMovingAverageStrategy
        from data_utils import generate_synthetic_data
        
        # Generate small dataset for quick test
        data = generate_synthetic_data(
            start_date='2023-01-01',
            end_date='2023-03-31',
            initial_price=100,
            seed=42
        )
        
        # Run backtest
        results = run_backtest(
            data=data,
            strategy_class=SimpleMovingAverageStrategy,
            initial_cash=10000,
            strategy_params={'short_period': 5, 'long_period': 15},
            save_to_db=False  # Don't save test results
        )
        
        print(f"✓ Backtest completed successfully")
        print(f"  - Strategy: {results['strategy_name']}")
        print(f"  - Period: {results['start_date']} to {results['end_date']}")
        print(f"  - Total Return: {results['total_return_pct']:.2f}%")
        print(f"  - Total Trades: {results['total_trades']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full backtest failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Trading Backtesting System - Test Suite")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install required packages:")
        print("pip install -r requirements.txt")
        return False
    
    # Test data utilities
    data_success, test_data = test_data_utils()
    if not data_success:
        print("\n❌ Data utilities tests failed.")
        return False
    
    # Test strategies
    if not test_strategies():
        print("\n❌ Strategy tests failed.")
        return False
    
    # Test database
    if not test_database():
        print("\n❌ Database tests failed.")
        return False
    
    # Test full backtest
    if not test_full_backtest():
        print("\n❌ Full backtest test failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The trading backtesting system is ready to use.")
    print("\nNext steps:")
    print("1. Run 'python examples/example_usage.py' for a complete example")
    print("2. Check TRADING_README.md for detailed documentation")
    print("3. Create your own strategies and data files")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
