# Trading Agent - AI-Powered Trading Strategy Implementation

This module implements an intelligent trading agent that combines traditional trading strategies with Google's Agent Development Kit (ADK) for intelligent decision-making and analysis.

## Overview

The `TradingAgent` class provides:

- **AI-Powered Strategy Execution**: Uses Google's Gemini models for intelligent trading decisions
- **Backtest Analysis**: Automated backtesting with performance analysis
- **Risk Management**: Built-in risk management and position sizing
- **Conversational Interface**: Natural language interaction for strategy analysis
- **Modular Architecture**: Integrates seamlessly with existing backtesting framework

## Components

### 1. TradingAgent
Main agent class that provides AI-powered trading capabilities:
- Strategy backtesting and analysis
- Market data generation
- Trading decision making
- Performance evaluation
- Conversational interface

### 2. TradingAgentStrategy
A strategy class that inherits from `BaseStrategy` and can be controlled by an ADK agent:
- Agent-driven buy/sell decisions
- Risk-adjusted position sizing
- Real-time market analysis

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google AI API key:
```bash
export GOOGLE_API_KEY="your-api-key-here"
export GOOGLE_GENAI_USE_VERTEXAI="False"
```

Get your API key from: https://aistudio.google.com/app/apikey

## Quick Start

### Basic Usage

```python
import asyncio
from src.agents.trading_agent import TradingAgent

# Create agent
agent = TradingAgent(
    name="my_trading_agent",
    model="gemini-2.0-flash",
    initial_cash=100000.0
)

# Run a backtest
result = agent.run_backtest(
    strategy_name="sma",
    start_date="2022-01-01",
    end_date="2023-12-31",
    strategy_params={"short_period": 10, "long_period": 30}
)

print(f"Final Value: ${result['final_value']:,.2f}")
print(f"Total Return: {result['total_return']:.2%}")
```

### Conversational Interface

```python
async def chat_example():
    agent = TradingAgent()
    session_id = await agent.setup_session()
    
    response = await agent.chat(
        "What's the best strategy for a volatile market?",
        session_id=session_id
    )
    print("Agent:", response)

# Run async
asyncio.run(chat_example())
```

### Integration with Existing Framework

```python
from src.data import DataProvider
from src.backtesting import BacktestEngine
from src.agents.trading_agent import TradingAgentStrategy

# Generate data
data_provider = DataProvider()
data_feed = data_provider.generate_synthetic(
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# Run backtest with agent-driven strategy
engine = BacktestEngine(initial_cash=100000)
results = engine.run_backtest(
    data_feed=data_feed,
    strategy_class=TradingAgentStrategy,
    strategy_params={'agent_enabled': True}
)
```

## Available Tools

The TradingAgent provides the following tools:

### 1. run_backtest
Execute backtests with various strategies:
```python
result = agent.run_backtest(
    strategy_name="rsi",  # Available: sma, rsi, bollinger
    start_date="2022-01-01",
    end_date="2023-12-31",
    strategy_params={"period": 14, "oversold": 30, "overbought": 70}
)
```

### 2. analyze_strategy_performance
Analyze backtest results:
```python
analysis = agent.analyze_strategy_performance()
print(f"Overall Rating: {analysis['overall_rating']}")
print(f"Sharpe Ratio: {analysis['performance_summary']['sharpe_ratio']}")
```

### 3. generate_market_data
Create synthetic market data:
```python
data = agent.generate_market_data(
    start_date="2023-01-01",
    end_date="2023-12-31",
    initial_price=100,
    volatility=0.2
)
```

### 4. get_trading_decision
Get AI-powered trading recommendations:
```python
market_data = {
    'close': 105.50,
    'previous_close': 103.25,
    'portfolio_value': 110000,
    'position': 0
}

decision = agent.get_trading_decision(market_data)
print(f"Action: {decision['action']}")
print(f"Confidence: {decision['confidence']}")
print(f"Reasoning: {decision['reasoning']}")
```

## Example Conversations

The agent can handle natural language queries like:

- "Run a backtest using SMA strategy with 10 and 30 day periods"
- "What's the best risk management approach for my portfolio?"
- "Analyze the performance of my last backtest"
- "Should I buy or sell based on current market conditions?"

## Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google AI API key (required)
- `GOOGLE_GENAI_USE_VERTEXAI`: Set to "False" for Google AI Studio

### Agent Parameters
- `name`: Agent identifier
- `model`: LLM model to use (default: "gemini-2.0-flash")
- `initial_cash`: Starting capital for backtests

### Strategy Parameters
- `agent_enabled`: Enable agent-driven decisions
- `risk_tolerance`: Risk per trade (default: 2%)
- `max_position_size`: Maximum position size (default: 10%)

## Supported Strategies

- **SMA (Simple Moving Average)**: Crossover strategy
- **RSI (Relative Strength Index)**: Momentum strategy
- **Bollinger Bands**: Mean reversion strategy

Add new strategies by implementing them in the `src/strategies/` directory.

## Performance Metrics

The agent provides comprehensive performance analysis:

- **Return Metrics**: Total return, annualized return
- **Risk Metrics**: Sharpe ratio, maximum drawdown, volatility
- **Trading Metrics**: Win rate, profit factor, total trades
- **Advanced Metrics**: Value at Risk, Expected Shortfall

## Error Handling

The agent includes robust error handling:
- Invalid strategy names
- Missing API keys
- Data generation failures
- Network connectivity issues

## Examples

See `examples/trading_agent_example.py` for comprehensive usage examples including:
- Synchronous tool usage
- Async conversational interface
- Strategy integration
- Performance analysis

## Architecture

```
TradingAgent
├── ADK Agent (Google AI)
│   ├── Tools (run_backtest, analyze_performance, etc.)
│   ├── Session Management
│   └── Conversation Interface
├── Strategy Integration
│   ├── TradingAgentStrategy (inherits BaseStrategy)
│   ├── Risk Management
│   └── Position Sizing
└── Framework Integration
    ├── DataProvider
    ├── BacktestEngine
    └── Performance Analysis
```

## Contributing

To add new capabilities:

1. **New Tools**: Add methods to `TradingAgent` and include in the `tools` list
2. **New Strategies**: Implement in `src/strategies/` and update the strategy map
3. **New Models**: Add support for additional LLMs via LiteLLM

## License

This project is part of the AI-Agentic-Bots trading framework.
