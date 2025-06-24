# AI-Agentic-Bots
AI-Agentic-Bots are intelligent, autonomous agents that understand context, reason through complex problems, and take action to accomplish tasks with minimal human input. By combining advanced language understanding, planning, and decision-making, these bots enable seamless automation and more productive, adaptable AI-driven workflows.

## 🚀 Trading Backtesting System

This repository now includes a comprehensive **Trading Backtesting System** built with Python and the `backtrader` library. The system provides a complete framework for testing trading strategies with professional-grade performance analysis and database storage.

### ✨ Features

- **Multiple Built-in Strategies**: Simple Moving Average, RSI, Bollinger Bands, Buy & Hold, Mean Reversion, and Momentum strategies
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, drawdown, win rate, and trade analysis
- **Database Storage**: SQLite integration for storing backtest results and trade history
- **Data Utilities**: Support for CSV files, Yahoo Finance data, and synthetic data generation
- **Modular Design**: Easy-to-extend strategy framework and flexible parameter optimization
- **Professional Reporting**: Detailed performance summaries and strategy comparisons

### 🏁 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Basic Example**:
   ```bash
   python examples/example_usage.py
   ```

3. **Test Advanced Strategies**:
   ```bash
   python examples/advanced_example.py
   ```

4. **Verify Installation**:
   ```bash
   python tests/test_system.py
   ```

5. **Test New Architecture**:
   ```bash
   python test_restructured_system.py
   ```

### 📁 Project Structure

```
├── src/                          # Main source code (modular architecture)
│   ├── strategies/              # Trading strategies
│   │   ├── base.py             # Base strategy class
│   │   ├── sma.py              # Simple Moving Average strategy
│   │   ├── rsi.py              # RSI strategy
│   │   ├── bollinger.py        # Bollinger Bands strategy
│   │   ├── buy_hold.py         # Buy & Hold strategy
│   │   ├── mean_reversion.py   # Mean Reversion strategy
│   │   └── momentum.py         # Momentum strategy
│   ├── data/                   # Data handling modules
│   │   ├── providers.py        # Data provider abstraction
│   │   ├── loaders.py          # CSV, Yahoo Finance loaders
│   │   ├── validators.py       # Data validation utilities
│   │   └── generators.py       # Synthetic data generators
│   ├── backtesting/            # Core backtesting engine
│   │   └── engine.py          # Decoupled backtesting engine
│   ├── database/               # Database management
│   │   └── manager.py         # SQLite operations
│   └── analyzers/              # Performance analyzers
│       ├── performance.py      # Performance metrics
│       └── trades.py          # Trade analysis
├── examples/                    # Usage examples
│   ├── example_usage.py        # Basic usage examples
│   └── advanced_example.py     # Advanced strategies and optimization
├── tests/                      # Test scripts
│   └── test_system.py         # System verification tests
├── data/                       # Data storage directory
├── requirements.txt            # Package dependencies
├── trading_backtest.py         # Backward compatibility layer
├── data_utils.py              # Backward compatibility for data utilities
├── TRADING_README.md           # Detailed documentation
├── backtest_results.db         # SQLite database (created after first run)
└── docs/
    └── backtrader.md          # Backtrader library documentation
```

### 🏗️ Architecture Features

- **Modular Design**: Clean separation of concerns with dedicated modules for strategies, data, backtesting, and analysis
- **Decoupled Data Feeding**: Data providers are completely separated from the backtesting engine
- **Backward Compatibility**: Existing code continues to work with the new architecture
- **Professional Structure**: Modern Python package layout following best practices
- **Extensible Framework**: Easy to add new strategies, data sources, and analyzers

### 🔄 Usage - Two Ways

#### Option 1: New Modular Structure (Recommended)
```python
from src.data import DataProvider
from src.backtesting import BacktestEngine
from src.strategies import SimpleMovingAverageStrategy

# Generate data using data provider
data_provider = DataProvider()
data_feed = data_provider.generate_synthetic(
    start_date='2022-01-01',
    end_date='2023-12-31',
    initial_price=100
)

# Run backtest using decoupled engine
engine = BacktestEngine(initial_cash=100000)
results = engine.run_backtest(
    data_feed=data_feed,
    strategy_class=SimpleMovingAverageStrategy,
    strategy_params={'short_period': 10, 'long_period': 30}
)
```

#### Option 2: Backward Compatibility Layer
```python
from trading_backtest import run_backtest, SimpleMovingAverageStrategy
from data_utils import generate_synthetic_data

# Generate sample data (old API)
data = generate_synthetic_data(
    start_date='2022-01-01',
    end_date='2023-12-31',
    initial_price=100
)

# Run backtest (old API)
results = run_backtest(
    data=data,
    strategy_class=SimpleMovingAverageStrategy,
    initial_cash=100000,
    strategy_params={'short_period': 10, 'long_period': 30}
)
```

Both approaches produce the same results, but the new modular structure provides better separation of concerns and extensibility.

### 📊 Sample Results

The system has been tested with various strategies showing realistic performance metrics:

| Strategy | Return | Sharpe Ratio | Max Drawdown | Trades |
|----------|--------|-------------|-------------|--------|
| Buy & Hold | 5.03% | 0.235 | 58.52% | 1 |
| Mean Reversion | 3.81% | 0.190 | 54.51% | 200+ |
| RSI Strategy | 51.14% | 0.888 | 26.95% | Variable |
| Bollinger Bands | 26.87% | 0.849 | 24.09% | Variable |

### 🔧 Key Components

1. **Strategy Framework**: Built-in strategies with easy customization
2. **Performance Analysis**: Comprehensive metrics and risk assessment
3. **Data Management**: Multiple data sources and validation
4. **Database Integration**: Persistent storage for results and analysis
5. **Parameter Optimization**: Tools for strategy fine-tuning

### 📖 Documentation

For detailed documentation, examples, and advanced usage, see [TRADING_README.md](TRADING_README.md).

### 🎯 Perfect for

- **Quantitative Researchers**: Testing and validating trading hypotheses
- **Algorithmic Traders**: Developing and optimizing automated strategies
- **Financial Students**: Learning about systematic trading approaches
- **Portfolio Managers**: Analyzing strategy performance and risk metrics

---

**Note**: This backtesting system is for educational and research purposes. Past performance does not guarantee future results. Always conduct thorough testing before implementing any trading strategy with real capital.

