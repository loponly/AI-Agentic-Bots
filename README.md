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
   python tests/test_restructured_system.py
   ```

6. **Run All Tests**:
   ```bash
   python tests/run_all_tests.py
   ```

### 📁 Project Structure

```
├── src/                                    # Main source code (modular architecture)
│   ├── __init__.py                        # Package initialization
│   ├── agent.py                           # Legacy agent code
│   ├── adk_agents/                        # ADK AI agents
│   │   ├── __init__.py                    # Package initialization
│   │   ├── backtest_agent.py              # Backtesting AI agent
│   │   └── market_research_agent.py       # Market research AI agent
│   ├── agents/                            # Trading agents
│   │   ├── __init__.py                    # Package initialization
│   │   └── trading_agent.py               # Advanced trading agent
│   ├── strategies/                        # Trading strategies
│   │   ├── __init__.py                    # Package initialization
│   │   ├── base.py                        # Base strategy class
│   │   ├── sma.py                         # Simple Moving Average strategy
│   │   ├── rsi.py                         # RSI strategy
│   │   ├── bollinger.py                   # Bollinger Bands strategy
│   │   ├── buy_hold.py                    # Buy & Hold strategy
│   │   ├── mean_reversion.py              # Mean Reversion strategy
│   │   └── momentum.py                    # Momentum strategy
│   ├── data/                              # Data handling modules
│   │   ├── __init__.py                    # Package initialization
│   │   ├── providers.py                   # Data provider abstraction
│   │   ├── loaders.py                     # CSV, Yahoo Finance loaders
│   │   ├── validators.py                  # Data validation utilities
│   │   └── generators.py                  # Synthetic data generators
│   ├── backtesting/                       # Core backtesting engine
│   │   ├── __init__.py                    # Package initialization
│   │   └── engine.py                      # Decoupled backtesting engine
│   ├── database/                          # Database management
│   │   ├── __init__.py                    # Package initialization
│   │   └── manager.py                     # SQLite operations
│   └── analyzers/                         # Performance analyzers
│       ├── __init__.py                    # Package initialization
│       ├── performance.py                 # Performance metrics
│       └── trades.py                      # Trade analysis
├── examples/                              # Usage examples and demos
│   ├── example_usage.py                   # Basic usage examples
│   ├── advanced_example.py                # Advanced strategies and optimization
│   ├── binance_backtest_example.py        # Binance backtesting examples
│   ├── demo_adk.py                        # ADK agent demonstration
│   ├── demo_trading_agent.py              # Trading agent demo
│   ├── full_demo.py                       # Complete system demo
│   ├── trading_agent_binance_example.py   # Binance trading agent example
│   ├── trading_agent_example.py           # Trading agent usage example
│   └── verify_setup.py                    # Setup verification script
├── tests/                                 # Test scripts and validation
│   ├── conftest.py                        # Pytest configuration
│   ├── README.md                          # Testing documentation
│   ├── run_adk_tests.py                   # ADK-specific tests runner
│   ├── run_all_tests.py                   # All tests runner
│   ├── test_adk_chat.py                   # ADK chat functionality tests
│   ├── test_agent_adk_integration.py      # Agent-ADK integration tests
│   ├── test_agent_fix.py                  # Agent fix validation tests
│   ├── test_binance_provider.py           # Binance provider tests
│   ├── test_binance_unit.py               # Binance unit tests
│   ├── test_comprehensive_agent.py        # Comprehensive agent tests
│   ├── test_modular_architecture.py       # Architecture validation tests
│   ├── test_restructured_system.py        # Restructured system tests
│   ├── test_simple_adk.py                 # Simple ADK functionality tests
│   ├── test_system_old.py                 # Legacy system tests
│   ├── test_system.py                     # Main system tests
│   ├── test_trading_agent.py              # Trading agent tests
│   └── validate_adk_agent.py              # ADK agent validation
├── docs/                                  # Documentation
│   ├── external/                          # External API documentation
│   │   ├── adk.md                         # ADK documentation
│   │   ├── backtrader.md                  # Backtrader library documentation
│   │   └── binance-api.md                 # Binance API documentation
│   └── internal/                          # Internal project documentation
│       ├── ADK_AGENT_FIX.md               # ADK agent fixes documentation
│       ├── BINANCE_IMPLEMENTATION.md      # Binance implementation guide
│       ├── BINANCE_IMPLEMENTATION_SUMMARY.md # Binance implementation summary
│       ├── FILE_ORGANIZATION.md           # File organization guide
│       ├── ORGANIZATION_COMPLETED.md      # Organization completion status
│       ├── ORGANIZATION_SUMMARY.md        # Organization summary
│       ├── QUICKSTART.md                  # Quick start guide
│       ├── README_ADK.md                  # ADK-specific README
│       └── trading_agent.md               # Trading agent documentation
├── prompts/                               # AI prompts and templates
│   ├── agent.md                           # Agent prompt templates
│   ├── backtrader.md                      # Backtrader prompts
│   └── TRADING_AGENT_IMPLEMENTATION.md    # Trading agent implementation prompts
├── data/                                  # Data storage directory
├── __init__.py                            # Root package initialization
├── agent.py                               # Legacy agent implementation
├── simplified_agents.py                   # Simplified agent implementations
├── trading_backtest.py                    # Backward compatibility layer
├── data_utils.py                          # Backward compatibility for data utilities
├── requirements.txt                       # Python package dependencies
├── pyproject.toml                         # Python project configuration
├── btc_usdt_sample.csv                    # Sample trading data
├── backtest_results.db                    # SQLite database (created after first run)
└── README.md                              # This file
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

