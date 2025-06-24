# Binance Data Provider Implementation

## Overview

This implementation adds comprehensive Binance API support to the AI-Agentic-Bots trading system, enabling real-time cryptocurrency data fetching, backtesting, and trading agent integration.

## Features

### 🚀 Core Features
- **Real-time Data**: Fetch live cryptocurrency prices and market data
- **Historical Data**: Download OHLCV candlestick data with flexible timeframes
- **Multiple Timeframes**: Support for 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
- **Backtesting Integration**: Seamless integration with existing backtesting engine
- **Trading Agent Support**: Ready-to-use with AI trading agents
- **Data Validation**: Comprehensive data validation and error handling
- **Rate Limiting**: Built-in rate limiting to respect API limits

### 📊 Supported Data Types
- **Klines/Candlesticks**: OHLCV data for any trading pair
- **Ticker Data**: 24hr price change statistics
- **Current Prices**: Real-time price feeds
- **Symbol Information**: Trading pair metadata
- **Volume Analysis**: Trading volume and liquidity data

## Installation & Setup

### 1. Dependencies
```bash
pip install -r requirements.txt
```

The implementation uses these key dependencies:
- `requests>=2.25.0` - HTTP requests to Binance API
- `cryptography>=3.4.0` - For API authentication (if using private endpoints)
- `pandas>=1.5.0` - Data manipulation
- `backtrader==1.9.78.123` - Backtesting framework

### 2. Basic Usage

#### Loading Cryptocurrency Data
```python
from src.data.providers import DataProvider

# Initialize data provider
provider = DataProvider()

# Load BTC/USDT daily data
btc_feed = provider.load_binance(
    symbol='BTCUSDT',
    interval='1d',
    limit=100
)

# Get current price
current_price = provider.binance_loader.get_price('BTCUSDT')
print(f"Current BTC price: ${current_price:,.2f}")
```

#### Multiple Cryptocurrencies
```python
# Load multiple cryptocurrencies
sources = {
    'BTC': {'type': 'binance', 'symbol': 'BTCUSDT', 'interval': '1d', 'limit': 100},
    'ETH': {'type': 'binance', 'symbol': 'ETHUSDT', 'interval': '1d', 'limit': 100},
    'ADA': {'type': 'binance', 'symbol': 'ADAUSDT', 'interval': '1d', 'limit': 100}
}

feeds = provider.load_multiple(sources)
```

#### Different Timeframes
```python
# Hourly data for day trading
hourly_feed = provider.load_binance('BTCUSDT', interval='1h', limit=168)  # 1 week

# 4-hour data for swing trading
swing_feed = provider.load_binance('BTCUSDT', interval='4h', limit=180)   # 30 days

# Weekly data for position trading
weekly_feed = provider.load_binance('BTCUSDT', interval='1w', limit=52)   # 1 year
```

## Integration Examples

### 1. Backtesting Integration
```python
# The BTC data can be directly used with the backtesting engine
from src.backtesting.engine import BacktestEngine
from src.strategies.sma import SMAStrategy

engine = BacktestEngine(initial_cash=10000.0)

result = engine.run_backtest(
    data_feed=btc_feed,
    strategy_class=SMAStrategy,
    strategy_params={'fast_period': 20, 'slow_period': 50}
)

print(f"Final Value: ${result['final_portfolio_value']:,.2f}")
```

### 2. Trading Agent Integration
```python
from src.agents.trading_agent import TradingAgent

# Create trading agent with Binance data
agent = TradingAgent(data_provider=provider)

# Analyze current market
analysis = agent.analyze_market('BTCUSDT')
signal = agent.generate_signal('BTCUSDT')

print(f"Market Analysis: {analysis}")
print(f"Trading Signal: {signal}")
```

### 3. Real-time Monitoring
```python
import time

def monitor_cryptocurrency(symbol, interval=60):
    """Monitor cryptocurrency prices in real-time."""
    while True:
        try:
            # Get current price
            price = provider.binance_loader.get_price(symbol)
            
            # Get 24hr statistics
            ticker = provider.binance_loader.get_24hr_ticker(symbol)
            
            print(f"{symbol}: ${price:,.2f} ({ticker['priceChangePercent']}%)")
            
            time.sleep(interval)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# Monitor BTC every minute
monitor_cryptocurrency('BTCUSDT', 60)
```

## API Reference

### BinanceLoader Class

#### Methods

##### `load(symbol, interval='1d', start_time=None, end_time=None, limit=500)`
Load OHLCV kline data from Binance.

**Parameters:**
- `symbol` (str): Trading pair symbol (e.g., 'BTCUSDT')
- `interval` (str): Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
- `start_time` (str, optional): Start time in 'YYYY-MM-DD' format
- `end_time` (str, optional): End time in 'YYYY-MM-DD' format
- `limit` (int): Number of klines to return (max 1000)

**Returns:** pandas.DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']

##### `get_price(symbol)`
Get current price for a symbol.

**Parameters:**
- `symbol` (str): Trading pair symbol

**Returns:** float - Current price

##### `get_24hr_ticker(symbol)`
Get 24hr ticker price change statistics.

**Parameters:**
- `symbol` (str): Trading pair symbol

**Returns:** dict - 24hr statistics including price change, volume, etc.

##### `get_symbol_info(symbol)`
Get symbol information from Binance.

**Parameters:**
- `symbol` (str): Trading pair symbol

**Returns:** dict - Symbol information including status, base asset, quote asset

### DataProvider Class

#### Additional Method

##### `load_binance(symbol, interval='1d', start_time=None, end_time=None, limit=500, name=None)`
Load data from Binance and return as DataFeed.

**Parameters:** Same as BinanceLoader.load() plus:
- `name` (str, optional): Name for the data feed

**Returns:** DataFeed object

## Testing

### Run Basic Tests
```bash
python tests/test_binance_provider.py
```

### Run Unit Tests
```bash
python tests/test_binance_unit.py
```

### Run Trading Agent Example
```bash
python examples/trading_agent_binance_example.py
```

### Run Backtesting Example
```bash
python examples/binance_backtest_example.py
```

## Error Handling

The implementation includes comprehensive error handling:

### API Rate Limits
- Automatic rate limiting between requests
- Retry logic for temporary failures
- Clear error messages for rate limit violations

### Data Validation
- Validates symbol formats
- Checks interval validity
- Ensures data completeness
- Handles missing data gracefully

### Network Issues
- Timeout handling (10 seconds default)
- Connection error recovery
- Fallback mechanisms

## Performance Considerations

### Caching
```python
# Cache frequently used data
provider.cache_feed('btc_daily', btc_feed)
cached_feed = provider.get_cached_feed('btc_daily')
```

### Batch Loading
```python
# Load multiple symbols efficiently
symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT']
feeds = {}

for symbol in symbols:
    feeds[symbol] = provider.load_binance(symbol, interval='1d', limit=100)
    time.sleep(0.1)  # Rate limiting
```

### Memory Management
```python
# Clear cache when not needed
provider.clear_cache()

# Use smaller datasets for testing
test_feed = provider.load_binance('BTCUSDT', interval='1h', limit=24)  # Last 24 hours
```

## Supported Trading Pairs

The implementation works with all Binance spot trading pairs:

### Major Cryptocurrencies
- Bitcoin: `BTCUSDT`, `BTCBUSD`, `BTCEUR`
- Ethereum: `ETHUSDT`, `ETHBUSD`, `ETHBTC`
- Binance Coin: `BNBUSDT`, `BNBBUSD`, `BNBBTC`

### Altcoins
- Cardano: `ADAUSDT`, `ADABTC`
- Polkadot: `DOTUSDT`, `DOTBTC`
- Chainlink: `LINKUSDT`, `LINKBTC`
- And 500+ more pairs

### Stablecoins
- Tether: `USDTBUSD`
- USD Coin: `USDCUSDT`
- Binance USD: `BUSDUSDT`

## Advanced Features

### Date Range Queries
```python
# Get specific date range
historical_feed = provider.load_binance(
    symbol='BTCUSDT',
    interval='1d',
    start_time='2023-01-01',
    end_time='2023-12-31'
)
```

### Resampling
```python
# Convert daily data to weekly
weekly_feed = daily_feed.resample('1W')

# Convert hourly data to 4-hour
four_hour_feed = hourly_feed.resample('4H')
```

### Statistics
```python
# Get comprehensive statistics
stats = btc_feed.get_statistics()
print(f"Total Return: {stats['price_stats']['price_change_pct']:.2f}%")
print(f"Volatility: {stats['return_stats']['annualized_volatility']:.2f}%")
print(f"Sharpe Ratio: {stats['return_stats']['sharpe_ratio']:.2f}")
```

## Security Notes

### API Keys (Optional)
- API keys are only needed for private endpoints (account data, trading)
- Market data is publicly available without authentication
- Store API keys securely using environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

provider = DataProvider(
    binance_api_key=os.getenv('BINANCE_API_KEY'),
    binance_api_secret=os.getenv('BINANCE_API_SECRET')
)
```

### Rate Limiting
- Default rate limits: 1200 requests per minute
- Weight-based system (different endpoints have different weights)
- Automatic backoff on rate limit violations

## Troubleshooting

### Common Issues

#### 1. Import Errors
```python
# Ensure you're in the project root directory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

#### 2. Network Timeouts
```python
# Increase timeout for slow connections
loader = BinanceLoader()
loader.timeout = 30  # Increase to 30 seconds
```

#### 3. Invalid Symbols
```python
# Check if symbol exists
try:
    symbol_info = loader.get_symbol_info('BTCUSDT')
    print(f"Symbol status: {symbol_info['status']}")
except ValueError:
    print("Symbol not found")
```

#### 4. Data Validation Errors
```python
# Load data without validation for debugging
data = loader.load('BTCUSDT', validate=False)
print(data.info())
```

## Contributing

To extend the Binance integration:

1. Add new methods to `BinanceLoader` class in `src/data/loaders.py`
2. Update `DataProvider` class in `src/data/providers.py` if needed
3. Add comprehensive tests
4. Update documentation

## Changelog

### Version 1.0.0
- Initial implementation
- Support for all major Binance endpoints
- Integration with backtesting engine
- Trading agent compatibility
- Comprehensive test suite
- Full documentation

## Future Enhancements

### Planned Features
- WebSocket streaming data support
- Advanced order book analysis
- Futures contract support
- Options data integration
- Cross-exchange arbitrage detection
- Machine learning price prediction

### Performance Improvements
- Async API calls
- Database caching
- Data compression
- Parallel processing

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test scripts to verify functionality
3. Review the example implementations
4. Check Binance API documentation for rate limits and updates

## License

This implementation follows the same license as the main project.
