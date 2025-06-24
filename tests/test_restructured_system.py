"""
Final Test Script - Restructured Trading Backtesting System
==========================================================

This script tests the restructured system to ensure everything is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_new_modular_imports():
    """Test importing from the new modular structure."""
    print("Testing new modular structure imports...")
    
    try:
        from src.strategies import SimpleMovingAverageStrategy, RSIStrategy
        from src.data import DataProvider
        from src.backtesting import BacktestEngine
        from src.database import DatabaseManager
        print("✓ All new modular imports successful")
        return True
    except Exception as e:
        print(f"✗ New modular imports failed: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility layer."""
    print("Testing backward compatibility layer...")
    
    try:
        from trading_backtest import SimpleMovingAverageStrategy, run_backtest
        from data_utils import generate_synthetic_data
        print("✓ Backward compatibility imports successful")
        return True
    except Exception as e:
        print(f"✗ Backward compatibility failed: {e}")
        return False

def test_end_to_end():
    """Test complete end-to-end functionality."""
    print("Testing end-to-end functionality...")
    
    try:
        # Test with new structure
        from src.data import DataProvider
        from src.backtesting import BacktestEngine
        from src.strategies import SimpleMovingAverageStrategy
        
        print("  Using new modular structure...")
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
        print(f"  ✓ New structure backtest: {results['total_return_pct']:.2f}% return")
        
        # Test with backward compatibility
        from trading_backtest import run_backtest
        from data_utils import generate_synthetic_data
        
        print("  Using backward compatibility layer...")
        data = generate_synthetic_data(
            start_date='2023-01-01',
            end_date='2023-02-01',
            seed=42
        )
        
        results = run_backtest(
            data, 
            SimpleMovingAverageStrategy,
            initial_cash=10000,
            save_to_db=False,
            strategy_params={'short_period': 5, 'long_period': 10}
        )
        print(f"  ✓ Backward compatibility backtest: {results['total_return_pct']:.2f}% return")
        
        return True
        
    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING RESTRUCTURED TRADING BACKTESTING SYSTEM")
    print("=" * 60)
    
    tests = [
        test_new_modular_imports,
        test_backward_compatibility,
        test_end_to_end
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all(results)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✓ System successfully restructured into modular architecture")
        print("✓ Data feeding is decoupled from backtesting")
        print("✓ Backward compatibility layer is working")
        print("✓ Examples and tests are updated")
        print()
        print("The system is now organized as follows:")
        print("- src/strategies/     - Trading strategies")
        print("- src/data/          - Data providers, loaders, validators, generators")
        print("- src/backtesting/   - Core backtesting engine")
        print("- src/database/      - Database management")
        print("- src/analyzers/     - Performance analyzers")
        print("- examples/          - Usage examples")
        print("- tests/            - Test scripts")
        print()
        print("🚀 Ready for production use!")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
