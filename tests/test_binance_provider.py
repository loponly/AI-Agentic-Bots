#!/usr/bin/env python3
"""
Test script for Binance data provider.
Tests loading BTC/USDT data for backtesting and agent use.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data.providers import DataProvider
from data.loaders import BinanceLoader


def test_binance_loader():
    """Test the BinanceLoader directly."""
    print("=" * 60)
    print("Testing BinanceLoader")
    print("=" * 60)
    
    try:
        # Initialize Binance loader (no API keys needed for public data)
        loader = BinanceLoader()
        print("✓ BinanceLoader initialized successfully")
        
        # Test getting current price
        print("\n1. Testing current price...")
        current_price = loader.get_price('BTCUSDT')
        print(f"✓ Current BTC/USDT price: ${current_price:,.2f}")
        
        # Test getting 24hr ticker
        print("\n2. Testing 24hr ticker...")
        ticker = loader.get_24hr_ticker('BTCUSDT')
        print(f"✓ 24hr change: {ticker['priceChangePercent']}%")
        print(f"✓ 24hr volume: {float(ticker['volume']):,.2f} BTC")
        
        # Test getting symbol info
        print("\n3. Testing symbol info...")
        symbol_info = loader.get_symbol_info('BTCUSDT')
        print(f"✓ Symbol status: {symbol_info['status']}")
        print(f"✓ Base asset: {symbol_info['baseAsset']}")
        print(f"✓ Quote asset: {symbol_info['quoteAsset']}")
        
        # Test loading kline data - recent data (last 100 days)
        print("\n4. Testing kline data loading...")
        
        # Load daily data
        daily_data = loader.load('BTCUSDT', interval='1d', limit=100)
        print(f"✓ Loaded {len(daily_data)} daily candles")
        print(f"✓ Date range: {daily_data['date'].min()} to {daily_data['date'].max()}")
        print(f"✓ Data shape: {daily_data.shape}")
        print(f"✓ Columns: {list(daily_data.columns)}")
        
        # Display sample data
        print("\nSample data (last 5 rows):")
        print(daily_data.tail().to_string(index=False))
        
        # Test different intervals
        print("\n5. Testing different intervals...")
        intervals = ['1h', '4h', '1d', '1w']
        for interval in intervals:
            try:
                data = loader.load('BTCUSDT', interval=interval, limit=10)
                print(f"✓ {interval}: {len(data)} candles loaded")
            except Exception as e:
                print(f"✗ {interval}: Failed - {e}")
        
        # Test with date range
        print("\n6. Testing with date range...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        range_data = loader.load(
            'BTCUSDT', 
            interval='1d', 
            start_time=start_date, 
            end_time=end_date
        )
        print(f"✓ Loaded {len(range_data)} candles for date range {start_date} to {end_date}")
        
        return daily_data
        
    except Exception as e:
        print(f"✗ BinanceLoader test failed: {e}")
        return None


def test_data_provider():
    """Test the DataProvider with Binance integration."""
    print("\n" + "=" * 60)
    print("Testing DataProvider with Binance")
    print("=" * 60)
    
    try:
        # Initialize data provider
        provider = DataProvider()
        print("✓ DataProvider initialized successfully")
        
        # Test loading BTC/USDT data
        print("\n1. Loading BTC/USDT daily data...")
        btc_feed = provider.load_binance(
            symbol='BTCUSDT',
            interval='1d',
            limit=100,
            name='BTC_daily'
        )
        print(f"✓ Created data feed: {btc_feed.name}")
        print(f"✓ Data shape: {btc_feed.data.shape}")
        print(f"✓ Metadata: {btc_feed.metadata}")
        
        # Get statistics
        print("\n2. Getting data statistics...")
        stats = btc_feed.get_statistics()
        print(f"✓ Price range: ${stats['price_stats']['min_price']:.2f} - ${stats['price_stats']['max_price']:.2f}")
        print(f"✓ Average volume: {stats['volume_stats']['avg_volume']:,.2f}")
        print(f"✓ Total return: {stats['price_stats']['price_change_pct']:.2f}%")
        
        # Test converting to backtrader feed
        print("\n3. Converting to backtrader feed...")
        bt_feed = btc_feed.to_backtrader_feed()
        print(f"✓ Backtrader feed created: {type(bt_feed)}")
        
        # Test resampling to different timeframes
        print("\n4. Testing resampling...")
        weekly_feed = btc_feed.resample('1W')
        print(f"✓ Resampled to weekly: {weekly_feed.data.shape[0]} candles")
        
        # Test loading multiple symbols
        print("\n5. Testing multiple symbols...")
        try:
            symbols_config = {
                'BTC': {'type': 'binance', 'symbol': 'BTCUSDT', 'interval': '1d', 'limit': 50},
                'ETH': {'type': 'binance', 'symbol': 'ETHUSDT', 'interval': '1d', 'limit': 50},
            }
            
            multiple_feeds = provider.load_multiple(symbols_config)
            print(f"✓ Loaded {len(multiple_feeds)} feeds:")
            for name, feed in multiple_feeds.items():
                print(f"  - {name}: {feed.data.shape[0]} candles")
                
        except Exception as e:
            print(f"✗ Multiple symbols test failed: {e}")
        
        # Test caching
        print("\n6. Testing caching...")
        provider.cache_feed('btc_test', btc_feed)
        cached_feed = provider.get_cached_feed('btc_test')
        print(f"✓ Cached and retrieved feed: {cached_feed.name}")
        
        return btc_feed
        
    except Exception as e:
        print(f"✗ DataProvider test failed: {e}")
        return None


def test_integration_with_backtrader():
    """Test integration with backtrader."""
    print("\n" + "=" * 60)
    print("Testing Backtrader Integration")
    print("=" * 60)
    
    try:
        import backtrader as bt
        
        # Get data
        provider = DataProvider()
        btc_feed = provider.load_binance('BTCUSDT', interval='1d', limit=100)
        
        # Convert to backtrader feed
        bt_data = btc_feed.to_backtrader_feed()
        
        # Create a simple strategy for testing
        class TestStrategy(bt.Strategy):
            def __init__(self):
                self.dataclose = self.datas[0].close
                self.order = None
                
            def next(self):
                if not self.position:
                    if self.dataclose[0] > self.dataclose[-1]:
                        self.order = self.buy()
                else:
                    if self.dataclose[0] < self.dataclose[-1]:
                        self.order = self.sell()
        
        # Create cerebro instance
        cerebro = bt.Cerebro()
        cerebro.addstrategy(TestStrategy)
        cerebro.adddata(bt_data)
        cerebro.broker.setcash(10000.0)
        
        print("✓ Backtrader setup completed")
        print(f"✓ Initial cash: ${cerebro.broker.getvalue():,.2f}")
        
        # Run strategy
        cerebro.run()
        final_value = cerebro.broker.getvalue()
        
        print(f"✓ Final portfolio value: ${final_value:,.2f}")
        print(f"✓ Total return: {((final_value - 10000) / 10000) * 100:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"✗ Backtrader integration test failed: {e}")
        return False


def save_sample_data(data, filename='btc_usdt_sample.csv'):
    """Save sample data for further testing."""
    if data is not None:
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        data.to_csv(filepath, index=False)
        print(f"\n✓ Sample data saved to: {filepath}")
        return filepath
    return None


def main():
    """Main test function."""
    print("🚀 Starting Binance Data Provider Tests")
    print("=" * 60)
    
    # Test 1: BinanceLoader
    daily_data = test_binance_loader()
    
    # Test 2: DataProvider
    feed = test_data_provider()
    
    # Test 3: Backtrader integration
    test_integration_with_backtrader()
    
    # Save sample data
    if daily_data is not None:
        save_sample_data(daily_data)
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Use the data in your backtesting strategies")
    print("2. Integrate with trading agents")
    print("3. Set up API keys for private data if needed")
    print("4. Implement additional cryptocurrency pairs")


if __name__ == "__main__":
    main()
