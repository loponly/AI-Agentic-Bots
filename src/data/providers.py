"""
Data Provider Module
===================

Centralized data provider that abstracts data sources and provides a unified interface
for the backtesting system.
"""

import pandas as pd
import backtrader as bt
from typing import Dict, Any, Optional, Union, List
from abc import ABC, abstractmethod
from .validators import DataValidator
from .loaders import CSVLoader, YahooFinanceLoader, BinanceLoader
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
    
    def __init__(self, binance_api_key: Optional[str] = None, binance_api_secret: Optional[str] = None):
        """Initialize data provider."""
        self.csv_loader = CSVLoader()
        self.yahoo_loader = YahooFinanceLoader()
        self.binance_loader = BinanceLoader(binance_api_key, binance_api_secret)
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
    
    def load_binance(
        self,
        symbol: str,
        interval: str = '1d',
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 500,
        name: Optional[str] = None
    ) -> DataFeed:
        """
        Load data from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            start_time: Start time in 'YYYY-MM-DD' format
            end_time: End time in 'YYYY-MM-DD' format
            limit: Number of klines to return (max 1000)
            name: Name for the data feed
            
        Returns:
            DataFeed object
        """
        data = self.binance_loader.load(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        feed_name = name or f"binance_{symbol}_{interval}"
        
        return DataFeed(
            data=data,
            name=feed_name,
            metadata={
                'source': 'binance',
                'symbol': symbol,
                'interval': interval,
                'start_time': start_time,
                'end_time': end_time,
                'limit': limit
            }
        )
    
    def load_multiple(self, sources: Dict[str, Dict[str, Any]]) -> Dict[str, DataFeed]:
        """
        Load multiple data sources.
        
        Args:
            sources: Dictionary with source configurations
                    Format: {name: {'type': 'csv/yahoo/binance/synthetic', ...params}}
                    
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
            elif source_type == 'binance':
                feeds[name] = self.load_binance(name=name, **config)
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
    
    def load_binance_pairs(
        self,
        pairs: Optional[List[str]] = None,
        interval: str = '1d',
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 500,
        use_synthetic_fallback: bool = True
    ) -> Dict[str, DataFeed]:
        """
        Load data for multiple Binance trading pairs.
        
        Args:
            pairs: List of trading pairs (if None, uses popular pairs)
            interval: Kline interval
            start_time: Start time
            end_time: End time
            limit: Number of klines
            use_synthetic_fallback: Create synthetic data if real data fails
            
        Returns:
            Dictionary of DataFeed objects keyed by pair name
        """
        if pairs is None:
            pairs = get_popular_binance_pairs()[:10]  # Use first 10 popular pairs
        
        feeds = {}
        pair_info = get_binance_pair_info()
        
        for i, pair in enumerate(pairs):
            try:
                feed = self.load_binance(
                    symbol=pair,
                    interval=interval,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
                feeds[pair] = feed
                
            except Exception as e:
                if use_synthetic_fallback:
                    # Generate synthetic data with realistic characteristics
                    info = pair_info.get(pair, {})
                    typical_price = info.get('typical_price', 100)
                    volatility = info.get('volatility', 0.05)
                    
                    feed = self.generate_synthetic(
                        start_date=start_time or '2023-01-01',
                        end_date=end_time or '2023-12-31',
                        initial_price=typical_price,
                        volatility=volatility,
                        drift=0.001,
                        seed=42 + i,
                        name=f"synthetic_{pair}"
                    )
                    feeds[pair] = feed
                else:
                    print(f"Warning: Failed to load {pair}: {e}")
                    
        return feeds


def get_popular_binance_pairs() -> List[str]:
    """
    Get a list of popular Binance trading pairs.
    
    Returns:
        List of popular cryptocurrency trading pairs
    """
    return [
        'BTCUSDT',    # Bitcoin
        'ETHUSDT',    # Ethereum
        'BNBUSDT',    # Binance Coin
        'ADAUSDT',    # Cardano
        'DOTUSDT',    # Polkadot
        'XRPUSDT',    # Ripple
        'LTCUSDT',    # Litecoin
        'LINKUSDT',   # Chainlink
        'BCHUSDT',    # Bitcoin Cash
        'XLMUSDT',    # Stellar
        'UNIUSDT',    # Uniswap
        'VETUSDT',    # VeChain
        'EOSUSDT',    # EOS
        'TRXUSDT',    # TRON
        'ATOMUSDT',   # Cosmos
        'MATICUSDT',  # Polygon
        'AVAXUSDT',   # Avalanche
        'SOLUSDT',    # Solana
        'FTMUSDT',    # Fantom
        'AAVEUSDT'    # Aave
    ]


def get_binance_pair_info() -> Dict[str, Dict[str, Any]]:
    """
    Get information about popular Binance trading pairs.
    
    Returns:
        Dictionary with pair information including typical price ranges and characteristics
    """
    return {
        'BTCUSDT': {
            'name': 'Bitcoin',
            'typical_price': 30000,
            'volatility': 0.04,
            'category': 'major'
        },
        'ETHUSDT': {
            'name': 'Ethereum',
            'typical_price': 2000,
            'volatility': 0.05,
            'category': 'major'
        },
        'BNBUSDT': {
            'name': 'Binance Coin',
            'typical_price': 300,
            'volatility': 0.04,
            'category': 'exchange'
        },
        'ADAUSDT': {
            'name': 'Cardano',
            'typical_price': 0.5,
            'volatility': 0.06,
            'category': 'altcoin'
        },
        'DOTUSDT': {
            'name': 'Polkadot',
            'typical_price': 8,
            'volatility': 0.06,
            'category': 'altcoin'
        },
        'XRPUSDT': {
            'name': 'Ripple',
            'typical_price': 0.6,
            'volatility': 0.05,
            'category': 'altcoin'
        },
        'LTCUSDT': {
            'name': 'Litecoin',
            'typical_price': 100,
            'volatility': 0.04,
            'category': 'major'
        },
        'LINKUSDT': {
            'name': 'Chainlink',
            'typical_price': 15,
            'volatility': 0.06,
            'category': 'defi'
        },
        'BCHUSDT': {
            'name': 'Bitcoin Cash',
            'typical_price': 250,
            'volatility': 0.05,
            'category': 'major'
        },
        'XLMUSDT': {
            'name': 'Stellar',
            'typical_price': 0.12,
            'volatility': 0.06,
            'category': 'altcoin'
        },
        'UNIUSDT': {
            'name': 'Uniswap',
            'typical_price': 7,
            'volatility': 0.07,
            'category': 'defi'
        },
        'VETUSDT': {
            'name': 'VeChain',
            'typical_price': 0.03,
            'volatility': 0.07,
            'category': 'altcoin'
        },
        'EOSUSDT': {
            'name': 'EOS',
            'typical_price': 1.5,
            'volatility': 0.06,
            'category': 'altcoin'
        },
        'TRXUSDT': {
            'name': 'TRON',
            'typical_price': 0.08,
            'volatility': 0.06,
            'category': 'altcoin'
        },
        'ATOMUSDT': {
            'name': 'Cosmos',
            'typical_price': 12,
            'volatility': 0.06,
            'category': 'altcoin'
        },
        'MATICUSDT': {
            'name': 'Polygon',
            'typical_price': 1.2,
            'volatility': 0.07,
            'category': 'scaling'
        },
        'AVAXUSDT': {
            'name': 'Avalanche',
            'typical_price': 20,
            'volatility': 0.07,
            'category': 'altcoin'
        },
        'SOLUSDT': {
            'name': 'Solana',
            'typical_price': 25,
            'volatility': 0.08,
            'category': 'altcoin'
        },
        'FTMUSDT': {
            'name': 'Fantom',
            'typical_price': 0.4,
            'volatility': 0.08,
            'category': 'altcoin'
        },
        'AAVEUSDT': {
            'name': 'Aave',
            'typical_price': 80,
            'volatility': 0.07,
            'category': 'defi'
        }
    }


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
