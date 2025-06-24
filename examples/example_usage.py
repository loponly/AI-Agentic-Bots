"""
Simple Example: How to use the Trading Backtesting System
=========================================================

This file demonstrates how to use the trading backtesting system with your own data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from trading_backtest import (
    run_backtest, 
    print_performance_summary,
    SimpleMovingAverageStrategy,
    RSIStrategy, 
    BollingerBandsStrategy
)
import pandas as pd
import numpy as np


def load_your_data(file_path: str) -> pd.DataFrame:
    """
    Load your trading data from a CSV file.
    
    Expected CSV format:
    date,open,high,low,close,volume
    2023-01-01,100.0,105.0,98.0,103.0,1000000
    ...
    
    Args:
        file_path: Path to your CSV file
        
    Returns:
        Pandas DataFrame with required columns
    """
    df = pd.read_csv(file_path)
    
    # Ensure date column is properly formatted
    df['date'] = pd.to_datetime(df['date'])
    
    # Validate required columns
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    return df


def create_sample_data() -> pd.DataFrame:
    """
    Create sample trading data for testing purposes.
    
    Returns:
        Sample DataFrame with OHLCV data
    """
    np.random.seed(42)
    
    # Generate 2 years of daily data
    dates = pd.date_range('2022-01-01', '2023-12-31', freq='D')
    
    # Simulate realistic stock price movements
    returns = np.random.normal(0.0008, 0.02, len(dates))  # Slightly positive drift
    prices = [100.0]  # Starting price
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(max(new_price, 1.0))  # Ensure price doesn't go negative
    
    # Create realistic OHLCV data
    data = []
    for i, (date, close_price) in enumerate(zip(dates, prices)):
        # Generate realistic open, high, low based on close
        open_price = close_price * (1 + np.random.normal(0, 0.005))
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
        volume = np.random.randint(50000, 500000)
        
        data.append({
            'date': date,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
    
    return pd.DataFrame(data)


def run_strategy_comparison(data: pd.DataFrame, initial_cash: float = 100000):
    """
    Compare performance of different strategies on the same data.
    
    Args:
        data: OHLCV DataFrame
        initial_cash: Starting cash amount
    """
    strategies = [
        (SimpleMovingAverageStrategy, {'short_period': 10, 'long_period': 30}),
        (RSIStrategy, {'rsi_period': 14}),
        (BollingerBandsStrategy, {'period': 20, 'devfactor': 2.0})
    ]
    
    results = []
    
    print("Running strategy comparison...")
    print("="*70)
    
    for strategy_class, params in strategies:
        print(f"\nTesting {strategy_class.__name__}...")
        
        result = run_backtest(
            data=data,
            strategy_class=strategy_class,
            initial_cash=initial_cash,
            strategy_params=params,
            save_to_db=True
        )
        
        results.append(result)
        print_performance_summary(result)
    
    # Summary comparison
    print("\n" + "="*70)
    print("STRATEGY COMPARISON SUMMARY")
    print("="*70)
    print(f"{'Strategy':<25} {'Return %':<12} {'Sharpe':<10} {'Max DD %':<12} {'Trades':<8}")
    print("-"*70)
    
    for result in results:
        sharpe = result['sharpe_ratio'] if result['sharpe_ratio'] else 0
        print(f"{result['strategy_name']:<25} "
              f"{result['total_return_pct']:>8.2f}%   "
              f"{sharpe:>8.3f}  "
              f"{result['max_drawdown_pct']:>8.2f}%    "
              f"{result['total_trades']:>6}")
    
    return results


def main():
    """Main function demonstrating usage."""
    print("Trading Backtesting System Example")
    print("="*50)
    
    # Option 1: Use sample data
    print("\n1. Creating sample data...")
    sample_data = create_sample_data()
    print(f"Created sample data with {len(sample_data)} rows")
    print(f"Date range: {sample_data['date'].min()} to {sample_data['date'].max()}")
    
    # Option 2: Load your own data (uncomment to use)
    # print("\n2. Loading your data...")
    # your_data = load_your_data('path/to/your/data.csv')
    
    # Run single strategy test
    print("\n" + "="*50)
    print("SINGLE STRATEGY TEST")
    print("="*50)
    
    results = run_backtest(
        data=sample_data,
        strategy_class=SimpleMovingAverageStrategy,
        initial_cash=100000,
        strategy_params={
            'short_period': 15,
            'long_period': 35,
            'stop_loss': 0.03,
            'take_profit': 0.08
        }
    )
    
    print_performance_summary(results)
    
    # Run strategy comparison
    print("\n" + "="*50)
    print("STRATEGY COMPARISON")
    print("="*50)
    
    comparison_results = run_strategy_comparison(sample_data, 100000)
    
    print(f"\nBacktest completed! Results saved to database.")
    print(f"Database file: backtest_results.db")


if __name__ == "__main__":
    main()
