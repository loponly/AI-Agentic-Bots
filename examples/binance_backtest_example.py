#!/usr/bin/env python3
"""
Binance Backtesting Example
==========================

This script demonstrates how to use the Binance data provider for backtesting
cryptocurrency trading strategies.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data.providers import DataProvider
from backtesting.engine import BacktestEngine
from strategies.sma import SMAStrategy
from strategies.rsi import RSIStrategy
from strategies.bollinger import BollingerBandsStrategy


def main():
    """Main function to demonstrate Binance data usage in backtesting."""
    print("🚀 Binance Data Provider - Backtesting Example")
    print("=" * 60)
    
    # Initialize data provider
    provider = DataProvider()
    
    # Load BTC/USDT data for backtesting
    print("1. Loading BTC/USDT data from Binance...")
    btc_feed = provider.load_binance(
        symbol='BTCUSDT',
        interval='1d',
        limit=365,  # Last year of data
        name='BTC_1Y'
    )
    
    print(f"✓ Loaded {len(btc_feed.data)} days of BTC/USDT data")
    print(f"✓ Date range: {btc_feed.data['date'].min()} to {btc_feed.data['date'].max()}")
    
    # Get data statistics
    stats = btc_feed.get_statistics()
    print(f"✓ Price range: ${stats['price_stats']['min_price']:,.2f} - ${stats['price_stats']['max_price']:,.2f}")
    print(f"✓ Total return: {stats['price_stats']['price_change_pct']:.2f}%")
    print(f"✓ Volatility: {stats['return_stats']['annualized_volatility']:.2f}%")
    
    # Initialize backtest engine
    print(f"\n2. Setting up backtesting engine...")
    engine = BacktestEngine(initial_cash=10000.0)
    
    # Test different strategies
    strategies = [
        ('SMA Crossover', SMAStrategy, {'fast_period': 20, 'slow_period': 50}),
        ('RSI Strategy', RSIStrategy, {'rsi_period': 14, 'oversold': 30, 'overbought': 70}),
        ('Bollinger Bands', BollingerBandsStrategy, {'period': 20, 'std_dev': 2})
    ]
    
    print(f"\n3. Running backtests on BTC/USDT...")
    results = {}
    
    for strategy_name, strategy_class, params in strategies:
        try:
            print(f"\n   Testing {strategy_name}...")
            
            # Run backtest
            result = engine.run_backtest(
                data_feed=btc_feed,
                strategy_class=strategy_class,
                strategy_params=params,
                verbose=False
            )
            
            results[strategy_name] = result
            
            # Print key metrics
            final_value = result['final_portfolio_value']
            total_return = ((final_value - 10000) / 10000) * 100
            num_trades = len(result.get('trades', []))
            
            print(f"   ✓ Final Value: ${final_value:,.2f}")
            print(f"   ✓ Total Return: {total_return:.2f}%")
            print(f"   ✓ Number of Trades: {num_trades}")
            
        except Exception as e:
            print(f"   ✗ {strategy_name} failed: {e}")
    
    # Compare strategies
    print(f"\n4. Strategy Comparison:")
    print("-" * 60)
    print(f"{'Strategy':<20} {'Return':<12} {'Trades':<10} {'Value':<12}")
    print("-" * 60)
    
    for name, result in results.items():
        if result:
            final_value = result['final_portfolio_value']
            total_return = ((final_value - 10000) / 10000) * 100
            num_trades = len(result.get('trades', []))
            
            print(f"{name:<20} {total_return:>8.2f}% {num_trades:>8} ${final_value:>10,.2f}")
    
    print("-" * 60)
    
    # Test with multiple cryptocurrencies
    print(f"\n5. Testing with multiple cryptocurrencies...")
    
    crypto_pairs = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT']
    crypto_results = {}
    
    for pair in crypto_pairs:
        try:
            print(f"\n   Loading {pair}...")
            
            # Load data
            feed = provider.load_binance(
                symbol=pair,
                interval='1d',
                limit=100,  # Last 100 days
                name=f'{pair}_100d'
            )
            
            # Run simple SMA strategy
            result = engine.run_backtest(
                data_feed=feed,
                strategy_class=SMAStrategy,
                strategy_params={'fast_period': 10, 'slow_period': 30},
                verbose=False
            )
            
            crypto_results[pair] = result
            
            final_value = result['final_portfolio_value']
            total_return = ((final_value - 10000) / 10000) * 100
            
            print(f"   ✓ {pair}: {total_return:.2f}% return")
            
        except Exception as e:
            print(f"   ✗ {pair} failed: {e}")
    
    # Multi-crypto comparison
    print(f"\n6. Multi-Cryptocurrency Comparison (SMA Strategy):")
    print("-" * 50)
    print(f"{'Pair':<12} {'Return':<12} {'Final Value':<12}")
    print("-" * 50)
    
    for pair, result in crypto_results.items():
        if result:
            final_value = result['final_portfolio_value']
            total_return = ((final_value - 10000) / 10000) * 100
            print(f"{pair:<12} {total_return:>8.2f}% ${final_value:>10,.2f}")
    
    print("-" * 50)
    
    # Test different timeframes
    print(f"\n7. Testing different timeframes for BTC/USDT...")
    
    timeframes = [
        ('4h', '4h', 200),   # 4-hour candles, last 200 (about 33 days)
        ('1h', '1h', 500),   # 1-hour candles, last 500 (about 21 days)
        ('1d', '1d', 30),    # Daily candles, last 30 days
    ]
    
    timeframe_results = {}
    
    for tf_name, interval, limit in timeframes:
        try:
            print(f"\n   Testing {tf_name} timeframe...")
            
            # Load data
            feed = provider.load_binance(
                symbol='BTCUSDT',
                interval=interval,
                limit=limit,
                name=f'BTC_{tf_name}'
            )
            
            # Run RSI strategy
            result = engine.run_backtest(
                data_feed=feed,
                strategy_class=RSIStrategy,
                strategy_params={'rsi_period': 14, 'oversold': 30, 'overbought': 70},
                verbose=False
            )
            
            timeframe_results[tf_name] = result
            
            final_value = result['final_portfolio_value']
            total_return = ((final_value - 10000) / 10000) * 100
            
            print(f"   ✓ {tf_name}: {total_return:.2f}% return")
            
        except Exception as e:
            print(f"   ✗ {tf_name} failed: {e}")
    
    # Timeframe comparison
    print(f"\n8. Timeframe Comparison (RSI Strategy on BTC/USDT):")
    print("-" * 50)
    print(f"{'Timeframe':<12} {'Return':<12} {'Final Value':<12}")
    print("-" * 50)
    
    for tf, result in timeframe_results.items():
        if result:
            final_value = result['final_portfolio_value']
            total_return = ((final_value - 10000) / 10000) * 100
            print(f"{tf:<12} {total_return:>8.2f}% ${final_value:>10,.2f}")
    
    print("-" * 50)
    
    print(f"\n🎉 Binance Backtesting Example Complete!")
    print("\nKey takeaways:")
    print("1. Binance data provider successfully integrates with backtesting")
    print("2. Multiple cryptocurrencies can be tested easily")
    print("3. Different timeframes provide different opportunities")
    print("4. Strategy performance varies significantly across assets")
    print("\nNext steps:")
    print("- Optimize strategy parameters")
    print("- Implement risk management")
    print("- Test on longer time periods")
    print("- Consider transaction costs")


if __name__ == "__main__":
    main()
