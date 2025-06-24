"""
Data Provider Module
===================

Centralized data provider that abstracts data sources and provides a unified interface
for the backtesting system.
"""

import pandas as pd
import backtrader as bt
from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from .validators import DataValidator
from .loaders import CSVLoader, YahooFinanceLoader
from .generators import SyntheticDataGenerator


class DataFeed:
    """Represents a data feed for backtesting."""
    
    def __init__(self, data: pd.DataFrame, name: str = "data", metadata: Optional[Dict] = None):
        """
        Initialize data feed.
        
        Args:
            data: DataFrame with OHLCV data
            name: Name of the data feed
            metadata: Additional metadata about the data
        """
        self.data = data
        self.name = name
        self.metadata = metadata or {}
        
        # Validate data
        DataValidator.validate_ohlcv_data(self.data)
    
    def to_backtrader_feed(self) -> bt.feeds.PandasData:
        """
        Convert to backtrader data feed.
        
        Returns:
            Backtrader PandasData object
        """
        df = self.data.copy()
        
        # Ensure date column is datetime and set as index
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # Sort by date
        df.sort_index(inplace=True)
        
        # Create backtrader data feed
        return bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # Use index
            open='open',
            high='high', 
            low='low',
            close='close',
            volume='volume',
            openinterest=None
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data statistics."""
        from .validators import DataValidator
        return DataValidator.get_data_statistics(self.data)
    
    def resample(self, timeframe: str) -> 'DataFeed':
        """
        Resample data to different timeframe.
        
        Args:
            timeframe: Target timeframe ('1H', '4H', '1D', '1W', '1M')
            
        Returns:
            New DataFeed with resampled data
        """
        df = self.data.copy()
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # Resample using appropriate aggregation
        resampled = df.resample(timeframe).agg({
            'open': 'first',
            'high': 'max', 
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        
        # Remove rows with NaN values
        resampled = resampled.dropna()
        resampled = resampled.reset_index()
        
        return DataFeed(
            data=resampled,
            name=f"{self.name}_{timeframe}",
            metadata={**self.metadata, 'timeframe': timeframe}
        )


class DataProvider:
    """
    Centralized data provider that manages different data sources.
    Provides a unified interface for loading data from various sources.
    """
    
    def __init__(self):
        """Initialize data provider."""
        self.csv_loader = CSVLoader()
        self.yahoo_loader = YahooFinanceLoader()
        self.synthetic_generator = SyntheticDataGenerator()
        self._cached_feeds = {}
    
    def load_csv(self, file_path: str, name: Optional[str] = None, **kwargs) -> DataFeed:
        """
        Load data from CSV file.
        
        Args:
            file_path: Path to CSV file
            name: Name for the data feed
            **kwargs: Additional arguments for CSV loading
            
        Returns:
            DataFeed object
        """
        data = self.csv_loader.load(file_path, **kwargs)
        feed_name = name or f"csv_{file_path.split('/')[-1].split('.')[0]}"
        
        return DataFeed(
            data=data,
            name=feed_name,
            metadata={'source': 'csv', 'file_path': file_path}
        )
    
    def load_yahoo_finance(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        name: Optional[str] = None
    ) -> DataFeed:
        """
        Load data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            name: Name for the data feed
            
        Returns:
            DataFeed object
        """
        data = self.yahoo_loader.load(symbol, start_date, end_date)
        feed_name = name or f"yahoo_{symbol}"
        
        return DataFeed(
            data=data,
            name=feed_name,
            metadata={
                'source': 'yahoo_finance',
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date
            }
        )
    
    def generate_synthetic(
        self,
        start_date: str = '2020-01-01',
        end_date: str = '2023-12-31',
        initial_price: float = 100.0,
        volatility: float = 0.02,
        drift: float = 0.0005,
        seed: Optional[int] = None,
        name: Optional[str] = None
    ) -> DataFeed:
        """
        Generate synthetic data for testing.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            initial_price: Starting price
            volatility: Daily volatility
            drift: Daily drift
            seed: Random seed
            name: Name for the data feed
            
        Returns:
            DataFeed object
        """
        data = self.synthetic_generator.generate(
            start_date=start_date,
            end_date=end_date,
            initial_price=initial_price,
            volatility=volatility,
            drift=drift,
            seed=seed
        )
        
        feed_name = name or f"synthetic_{start_date}_{end_date}"
        
        return DataFeed(
            data=data,
            name=feed_name,
            metadata={
                'source': 'synthetic',
                'start_date': start_date,
                'end_date': end_date,
                'initial_price': initial_price,
                'volatility': volatility,
                'drift': drift,
                'seed': seed
            }
        )
    
    def load_multiple(self, sources: Dict[str, Dict[str, Any]]) -> Dict[str, DataFeed]:
        """
        Load multiple data sources.
        
        Args:
            sources: Dictionary with source configurations
                    Format: {name: {'type': 'csv/yahoo/synthetic', ...params}}
                    
        Returns:
            Dictionary of DataFeed objects
        """
        feeds = {}
        
        for name, config in sources.items():
            source_type = config.pop('type')
            
            if source_type == 'csv':
                feeds[name] = self.load_csv(name=name, **config)
            elif source_type == 'yahoo':
                feeds[name] = self.load_yahoo_finance(name=name, **config)
            elif source_type == 'synthetic':
                feeds[name] = self.generate_synthetic(name=name, **config)
            else:
                raise ValueError(f"Unknown source type: {source_type}")
        
        return feeds
    
    def cache_feed(self, name: str, feed: DataFeed):
        """Cache a data feed for reuse."""
        self._cached_feeds[name] = feed
    
    def get_cached_feed(self, name: str) -> Optional[DataFeed]:
        """Get a cached data feed."""
        return self._cached_feeds.get(name)
    
    def list_cached_feeds(self) -> list:
        """List all cached feed names."""
        return list(self._cached_feeds.keys())
    
    def clear_cache(self):
        """Clear all cached feeds."""
        self._cached_feeds.clear()
    
    def from_dataframe(self, data: pd.DataFrame, name: str = "dataframe") -> DataFeed:
        """
        Create a data feed from a pandas DataFrame.
        
        Args:
            data: DataFrame with OHLCV data
            name: Name for the data feed
            
        Returns:
            DataFeed object
        """
        return DataFeed(
            data=data,
            name=name,
            metadata={'source': 'dataframe'}
        )


# Example usage
if __name__ == "__main__":
    # Initialize data provider
    provider = DataProvider()
    
    # Generate synthetic data
    feed = provider.generate_synthetic(
        start_date='2022-01-01',
        end_date='2023-12-31',
        seed=42
    )
    
    print(f"Created data feed: {feed.name}")
    print(f"Data shape: {feed.data.shape}")
    print(f"Date range: {feed.data['date'].min()} to {feed.data['date'].max()}")
    
    # Get statistics
    stats = feed.get_statistics()
    print(f"Total return: {stats['price_stats']['price_change_pct']:.2f}%")
    
    # Convert to backtrader feed
    bt_feed = feed.to_backtrader_feed()
    print(f"Backtrader feed created: {type(bt_feed)}")
