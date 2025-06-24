#!/usr/bin/env python3
"""
Unit tests for Binance Data Provider
===================================

This module contains comprehensive tests for the Binance data provider implementation.
"""

import unittest
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data.loaders import BinanceLoader
from data.providers import DataProvider, DataFeed


class TestBinanceLoader(unittest.TestCase):
    """Test cases for BinanceLoader."""
    
    def setUp(self):
        """Set up test cases."""
        self.loader = BinanceLoader()
    
    def test_initialization(self):
        """Test BinanceLoader initialization."""
        # Test without API keys
        loader = BinanceLoader()
        self.assertIsNone(loader.api_key)
        self.assertIsNone(loader.api_secret)
        self.assertEqual(loader.base_url, "https://api.binance.com")
        
        # Test with API keys
        loader_with_keys = BinanceLoader("test_key", "test_secret")
        self.assertEqual(loader_with_keys.api_key, "test_key")
        self.assertEqual(loader_with_keys.api_secret, "test_secret")
    
    def test_interval_validation(self):
        """Test interval validation."""
        valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        
        for interval in valid_intervals:
            # This should not raise an error
            try:
                # We'll mock the API call to avoid making real requests in tests
                with patch.object(self.loader, '_make_request') as mock_request:
                    mock_request.return_value = self._create_mock_kline_data()
                    result = self.loader.load('BTCUSDT', interval=interval, limit=10)
                    self.assertIsInstance(result, pd.DataFrame)
            except ValueError:
                self.fail(f"Valid interval {interval} raised ValueError")
        
        # Test invalid interval
        with self.assertRaises(ValueError):
            with patch.object(self.loader, '_make_request') as mock_request:
                mock_request.return_value = self._create_mock_kline_data()
                self.loader.load('BTCUSDT', interval='invalid')
    
    def _create_mock_kline_data(self):
        """Create mock kline data for testing."""
        return [
            [
                1640995200000,  # Open time
                "50000.00",     # Open
                "51000.00",     # High
                "49000.00",     # Low
                "50500.00",     # Close
                "100.5",        # Volume
                1641081599999,  # Close time
                "5050000.00",   # Quote asset volume
                1000,           # Number of trades
                "50.25",        # Taker buy base asset volume
                "2525000.00",   # Taker buy quote asset volume
                "0"             # Unused field
            ]
        ]
    
    @patch('requests.get')
    def test_load_method(self, mock_get):
        """Test the load method with mocked API response."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self._create_mock_kline_data()
        mock_get.return_value = mock_response
        
        # Test loading data
        result = self.loader.load('BTCUSDT', interval='1d', limit=1)
        
        # Verify result structure
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        
        expected_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        self.assertListEqual(list(result.columns), expected_columns)
        
        # Verify data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['date']))
        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.assertTrue(pd.api.types.is_numeric_dtype(result[col]))
    
    @patch('requests.get')
    def test_get_price_method(self, mock_get):
        """Test the get_price method."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"symbol": "BTCUSDT", "price": "50000.00"}
        mock_get.return_value = mock_response
        
        price = self.loader.get_price('BTCUSDT')
        
        self.assertEqual(price, 50000.00)
        self.assertIsInstance(price, float)
    
    @patch('requests.get')
    def test_get_symbol_info_method(self, mock_get):
        """Test the get_symbol_info method."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "baseAsset": "BTC",
                    "quoteAsset": "USDT"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        symbol_info = self.loader.get_symbol_info('BTCUSDT')
        
        self.assertEqual(symbol_info['symbol'], 'BTCUSDT')
        self.assertEqual(symbol_info['status'], 'TRADING')
        self.assertEqual(symbol_info['baseAsset'], 'BTC')
        self.assertEqual(symbol_info['quoteAsset'], 'USDT')
    
    def test_date_conversion(self):
        """Test date string to timestamp conversion."""
        with patch.object(self.loader, '_make_request') as mock_request:
            mock_request.return_value = self._create_mock_kline_data()
            
            # Test with date string
            result = self.loader.load(
                'BTCUSDT', 
                interval='1d', 
                start_time='2022-01-01',
                end_time='2022-01-02',
                limit=10
            )
            
            # Verify the API was called with timestamp parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args[1]['params']
            self.assertIn('startTime', call_args)
            self.assertIn('endTime', call_args)
            self.assertIsInstance(call_args['startTime'], int)
            self.assertIsInstance(call_args['endTime'], int)


class TestDataProvider(unittest.TestCase):
    """Test cases for DataProvider with Binance integration."""
    
    def setUp(self):
        """Set up test cases."""
        self.provider = DataProvider()
    
    def test_initialization(self):
        """Test DataProvider initialization."""
        # Test without API keys
        provider = DataProvider()
        self.assertIsNotNone(provider.binance_loader)
        self.assertIsNone(provider.binance_loader.api_key)
        
        # Test with API keys
        provider_with_keys = DataProvider("test_key", "test_secret")
        self.assertEqual(provider_with_keys.binance_loader.api_key, "test_key")
        self.assertEqual(provider_with_keys.binance_loader.api_secret, "test_secret")
    
    @patch('src.data.loaders.BinanceLoader.load')
    def test_load_binance_method(self, mock_load):
        """Test the load_binance method."""
        # Mock the loader's load method
        mock_data = pd.DataFrame({
            'date': pd.date_range('2022-01-01', periods=5),
            'open': [50000, 50100, 50200, 50300, 50400],
            'high': [50500, 50600, 50700, 50800, 50900],
            'low': [49500, 49600, 49700, 49800, 49900],
            'close': [50200, 50300, 50400, 50500, 50600],
            'volume': [100, 110, 120, 130, 140]
        })
        mock_load.return_value = mock_data
        
        # Test loading data
        feed = self.provider.load_binance('BTCUSDT', interval='1d', limit=5)
        
        # Verify feed properties
        self.assertIsInstance(feed, DataFeed)
        self.assertEqual(feed.name, 'binance_BTCUSDT_1d')
        self.assertEqual(feed.metadata['source'], 'binance')
        self.assertEqual(feed.metadata['symbol'], 'BTCUSDT')
        self.assertEqual(feed.metadata['interval'], '1d')
        
        # Verify data
        self.assertEqual(len(feed.data), 5)
        self.assertListEqual(list(feed.data.columns), ['date', 'open', 'high', 'low', 'close', 'volume'])
    
    @patch('src.data.loaders.BinanceLoader.load')
    def test_load_multiple_with_binance(self, mock_load):
        """Test loading multiple sources including Binance."""
        # Mock the loader's load method
        mock_data = pd.DataFrame({
            'date': pd.date_range('2022-01-01', periods=3),
            'open': [50000, 50100, 50200],
            'high': [50500, 50600, 50700],
            'low': [49500, 49600, 49700],
            'close': [50200, 50300, 50400],
            'volume': [100, 110, 120]
        })
        mock_load.return_value = mock_data
        
        # Test configuration
        sources = {
            'BTC': {
                'type': 'binance',
                'symbol': 'BTCUSDT',
                'interval': '1d',
                'limit': 3
            }
        }
        
        feeds = self.provider.load_multiple(sources)
        
        # Verify results
        self.assertIn('BTC', feeds)
        self.assertIsInstance(feeds['BTC'], DataFeed)
        self.assertEqual(feeds['BTC'].metadata['source'], 'binance')


class TestDataFeed(unittest.TestCase):
    """Test cases for DataFeed functionality with Binance data."""
    
    def setUp(self):
        """Set up test cases."""
        self.sample_data = pd.DataFrame({
            'date': pd.date_range('2022-01-01', periods=10),
            'open': [50000 + i*100 for i in range(10)],
            'high': [50500 + i*100 for i in range(10)],
            'low': [49500 + i*100 for i in range(10)],
            'close': [50200 + i*100 for i in range(10)],
            'volume': [100 + i*10 for i in range(10)]
        })
        self.feed = DataFeed(self.sample_data, "test_feed")
    
    def test_data_feed_creation(self):
        """Test DataFeed creation with Binance-like data."""
        self.assertEqual(self.feed.name, "test_feed")
        self.assertEqual(len(self.feed.data), 10)
        self.assertListEqual(list(self.feed.data.columns), ['date', 'open', 'high', 'low', 'close', 'volume'])
    
    def test_backtrader_conversion(self):
        """Test conversion to backtrader feed."""
        bt_feed = self.feed.to_backtrader_feed()
        self.assertIsNotNone(bt_feed)
        # Note: We can't easily test backtrader internals without more setup
    
    def test_statistics(self):
        """Test statistics calculation."""
        stats = self.feed.get_statistics()
        
        # Verify structure
        self.assertIn('data_info', stats)
        self.assertIn('price_stats', stats)
        self.assertIn('return_stats', stats)
        self.assertIn('volume_stats', stats)
        
        # Verify some values
        self.assertEqual(stats['data_info']['rows'], 10)
        self.assertGreater(stats['price_stats']['price_change_pct'], 0)  # Upward trend in test data
    
    def test_resampling(self):
        """Test data resampling."""
        # Create data with more granular timestamps
        detailed_data = pd.DataFrame({
            'date': pd.date_range('2022-01-01', periods=30, freq='1H'),
            'open': [50000 + i*10 for i in range(30)],
            'high': [50050 + i*10 for i in range(30)],
            'low': [49950 + i*10 for i in range(30)],
            'close': [50020 + i*10 for i in range(30)],
            'volume': [100 + i for i in range(30)]
        })
        
        detailed_feed = DataFeed(detailed_data, "detailed_test")
        resampled_feed = detailed_feed.resample('1D')
        
        # Should have fewer rows after resampling hourly to daily
        self.assertLess(len(resampled_feed.data), len(detailed_feed.data))
        self.assertEqual(resampled_feed.name, "detailed_test_1D")


def run_tests():
    """Run all tests."""
    print("🧪 Running Binance Data Provider Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBinanceLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProvider))
    suite.addTests(loader.loadTestsFromTestCase(TestDataFeed))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
