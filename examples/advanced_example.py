"""
Advanced Example: Creating Custom Strategies and Analyzing Results
=================================================================

This example demonstrates how to create custom strategies and perform
detailed analysis of the results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from trading_backtest import run_backtest, print_performance_summary, DatabaseManager
from data_utils import generate_synthetic_data
import backtrader as bt
import pandas as pd
import sqlite3


class BuyAndHoldStrategy(bt.Strategy):
    """
    Simple Buy and Hold Strategy - buys at the beginning and holds.
    """
    
    def __init__(self):
        self.order = None
        self.bought = False
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"BOUGHT at ${order.executed.price:.2f}")
        self.order = None
    
    def next(self):
        if self.order:
            return
            
        if not self.bought:
            # Buy with 95% of available cash
            size = int(self.broker.getvalue() * 0.95 / self.data.close[0])
            self.order = self.buy(size=size)
            self.bought = True


class MeanReversionStrategy(bt.Strategy):
    """
    Mean Reversion Strategy - buys when price is below 20-day average,
    sells when price is above 20-day average.
    """
    
    params = (
        ('period', 20),
        ('threshold', 0.02),  # 2% threshold
    )
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.period
        )
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"BOUGHT at ${order.executed.price:.2f}")
            elif order.issell():
                print(f"SOLD at ${order.executed.price:.2f}")
        self.order = None
    
    def next(self):
        if self.order:
            return
            
        if len(self) < self.params.period:
            return
            
        current_price = self.data.close[0]
        sma_value = self.sma[0]
        
        if not self.position:
            # Buy when price is significantly below SMA
            if current_price < sma_value * (1 - self.params.threshold):
                size = int(self.broker.getvalue() * 0.95 / current_price)
                self.order = self.buy(size=size)
        else:
            # Sell when price is significantly above SMA
            if current_price > sma_value * (1 + self.params.threshold):
                self.order = self.sell()


class MomentumStrategy(bt.Strategy):
    """
    Momentum Strategy - buys when price increases for consecutive days,
    sells when price decreases for consecutive days.
    """
    
    params = (
        ('momentum_period', 3),  # Number of consecutive days
    )
    
    def __init__(self):
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"BOUGHT at ${order.executed.price:.2f}")
            elif order.issell():
                print(f"SOLD at ${order.executed.price:.2f}")
        self.order = None
    
    def next(self):
        if self.order:
            return
            
        if len(self) < self.params.momentum_period:
            return
        
        # Check for consecutive up days
        up_days = 0
        down_days = 0
        
        for i in range(self.params.momentum_period):
            if self.data.close[-i] > self.data.close[-i-1]:
                up_days += 1
            elif self.data.close[-i] < self.data.close[-i-1]:
                down_days += 1
        
        if not self.position:
            # Buy on momentum up
            if up_days >= self.params.momentum_period:
                size = int(self.broker.getvalue() * 0.95 / self.data.close[0])
                self.order = self.buy(size=size)
        else:
            # Sell on momentum down
            if down_days >= self.params.momentum_period:
                self.order = self.sell()


def analyze_database_results():
    """Analyze all results stored in the database."""
    print("\n" + "="*70)
    print("DATABASE ANALYSIS")
    print("="*70)
    
    try:
        # Connect to database
        conn = sqlite3.connect('backtest_results.db')
        
        # Get all backtest results
        df = pd.read_sql_query("""
            SELECT strategy_name, total_return_pct, sharpe_ratio, 
                   max_drawdown_pct, total_trades, win_rate,
                   start_date, end_date, created_at
            FROM backtest_results 
            ORDER BY created_at DESC
        """, conn)
        
        if len(df) > 0:
            print(f"Total backtests in database: {len(df)}")
            print("\nTop performing strategies by return:")
            top_strategies = df.nlargest(5, 'total_return_pct')
            
            for _, row in top_strategies.iterrows():
                print(f"  {row['strategy_name']}: {row['total_return_pct']:.2f}% "
                      f"(Sharpe: {row['sharpe_ratio']:.3f if pd.notna(row['sharpe_ratio']) else 'N/A'})")
        
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing database: {e}")


def main():
    """Main function demonstrating advanced usage."""
    print("Advanced Trading Backtesting Example")
    print("="*50)
    
    # Generate more volatile data for better strategy testing
    print("\n1. Generating test data with higher volatility...")
    data = generate_synthetic_data(
        start_date='2022-01-01',
        end_date='2023-12-31',
        initial_price=100,
        volatility=0.025,  # Higher volatility
        drift=0.0003,      # Lower drift for more trading opportunities
        seed=123
    )
    
    print(f"Generated data: {len(data)} rows")
    
    # Show basic data statistics
    print(f"Data characteristics:")
    print(f"  - Date range: {data['date'].min()} to {data['date'].max()}")
    print(f"  - Price range: ${data['close'].min():.2f} to ${data['close'].max():.2f}")
    print(f"  - Average volume: {data['volume'].mean():,.0f}")
    
    # Test different strategies
    strategies = [
        (BuyAndHoldStrategy, {}, "Buy and Hold"),
        (MeanReversionStrategy, {'period': 20, 'threshold': 0.03}, "Mean Reversion"),
        (MomentumStrategy, {'momentum_period': 3}, "Momentum"),
    ]
    
    results = []
    
    print(f"\n2. Testing {len(strategies)} different strategies...")
    print("="*70)
    
    for strategy_class, params, name in strategies:
        print(f"\nTesting {name} Strategy...")
        print("-" * 40)
        
        result = run_backtest(
            data=data,
            strategy_class=strategy_class,
            initial_cash=100000,
            strategy_params=params,
            save_to_db=True
        )
        
        results.append((name, result))
        print(f"Return: {result['total_return_pct']:.2f}% | "
              f"Max DD: {result['max_drawdown_pct']:.2f}% | "
              f"Trades: {result['total_trades']}")
    
    # Compare results
    print(f"\n3. Strategy Comparison")
    print("="*70)
    print(f"{'Strategy':<20} {'Return %':<12} {'Sharpe':<10} {'Max DD %':<12} {'Trades':<8}")
    print("-"*70)
    
    for name, result in results:
        sharpe = result['sharpe_ratio'] if result['sharpe_ratio'] else 0
        print(f"{name:<20} "
              f"{result['total_return_pct']:>8.2f}%   "
              f"{sharpe:>8.3f}  "
              f"{result['max_drawdown_pct']:>8.2f}%    "
              f"{result['total_trades']:>6}")
    
    # Show detailed results for best performing strategy
    best_result = max(results, key=lambda x: x[1]['total_return_pct'])
    print(f"\n4. Best Performing Strategy: {best_result[0]}")
    print_performance_summary(best_result[1])
    
    # Analyze database
    analyze_database_results()
    
    print(f"\n5. Parameter Optimization Example")
    print("="*70)
    
    # Test different parameters for Mean Reversion strategy
    print("Testing different thresholds for Mean Reversion strategy...")
    
    best_threshold_result = None
    best_return = -float('inf')
    
    thresholds = [0.01, 0.02, 0.03, 0.04, 0.05]
    
    for threshold in thresholds:
        result = run_backtest(
            data=data,
            strategy_class=MeanReversionStrategy,
            initial_cash=100000,
            strategy_params={'period': 20, 'threshold': threshold},
            save_to_db=False  # Don't save optimization runs
        )
        
        print(f"Threshold {threshold:.2f}: {result['total_return_pct']:.2f}% return")
        
        if result['total_return_pct'] > best_return:
            best_return = result['total_return_pct']
            best_threshold_result = result
    
    print(f"\nBest threshold result:")
    print(f"Parameters: {best_threshold_result['strategy_params']}")
    print(f"Return: {best_threshold_result['total_return_pct']:.2f}%")
    
    print(f"\n" + "="*70)
    print("🎯 Advanced example completed!")
    print("All results have been saved to the database for future analysis.")
    print("="*70)


if __name__ == "__main__":
    main()
