# ADK Trading Agents

A sophisticated multi-agent trading system built with Google's Agent Development Kit (ADK). This system provides two specialized AI agents for comprehensive trading strategy development and market analysis.

## 🤖 Available Agents

### 1. Backtest Strategy Agent
**Specializes in strategy development and testing**

**Capabilities:**
- Create various trading strategies (SMA, RSI, Bollinger Bands, Momentum)
- Run comprehensive backtests with historical data
- Compare multiple strategies performance
- Optimize strategy parameters using grid search
- Analyze performance metrics and risk indicators

**Example Queries:**
- "Create an SMA strategy backtest for BTCUSDT"
- "Compare RSI and Bollinger Bands strategies on ETHUSDT"
- "Optimize momentum strategy parameters"
- "Show me available trading strategies"

### 2. Market Research Agent
**Specializes in market analysis and research**

**Capabilities:**
- Analyze market trends across multiple cryptocurrencies
- Perform detailed technical analysis with various indicators
- Identify chart patterns and support/resistance levels
- Compare asset performance across different timeframes
- Assess market sentiment and generate trading signals

**Example Queries:**
- "Analyze current market trends for major cryptocurrencies"
- "Perform technical analysis on BTCUSDT"
- "Compare performance of BTC, ETH, and ADA over 30 days"
- "What's the current market sentiment?"

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your Google AI API key in .env file
# Get your key from: https://aistudio.google.com/app/apikey
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

### 2. Run the Web Interface (Recommended)

```bash
# Launch the interactive web interface
adk web
```

This opens a browser-based chat interface where you can interact with both agents naturally.

### 3. Alternative: Terminal Interface

```bash
# Run in terminal mode
adk run
```

### 4. Alternative: API Server

```bash
# Start REST API server
adk api_server
```

### 5. Run Demo

```bash
# Run programmatic demo
python examples/demo_adk.py demo
```

## 📋 Prerequisites

- Python 3.9+
- Google AI API key (free from Google AI Studio)
- Internet connection for fetching market data

## 🛠️ Technical Features

### Backtest Agent Tools
- `create_strategy_backtest()` - Create and run strategy backtests
- `compare_strategies()` - Compare multiple strategies
- `optimize_strategy_parameters()` - Parameter optimization
- `get_available_strategies()` - List available strategies

### Market Research Agent Tools
- `analyze_market_trends()` - Multi-asset trend analysis
- `perform_technical_analysis()` - Comprehensive technical analysis
- `compare_market_performance()` - Performance comparison
- `get_market_sentiment()` - Market sentiment analysis

### Supported Strategies
- **SMA (Simple Moving Average)** - Crossover strategy
- **RSI (Relative Strength Index)** - Momentum oscillator
- **Bollinger Bands** - Volatility-based strategy
- **Momentum** - Price momentum strategy

### Supported Assets
- BTCUSDT, ETHUSDT, ADAUSDT, BNBUSDT, XRPUSDT
- Multiple timeframes: 1h, 4h, 1d, 1w

## 💡 Usage Examples

### Strategy Development
```
User: "Create a Bollinger Bands strategy for ETHUSDT and run a 90-day backtest"

Agent: Creates strategy, fetches historical data, runs backtest, and provides:
- Performance metrics (return, Sharpe ratio, max drawdown)
- Trade analysis (win rate, number of trades)
- Comparison with buy-and-hold
- Risk metrics and recommendations
```

### Market Analysis
```
User: "Analyze the technical indicators for BTCUSDT"

Agent: Performs comprehensive analysis including:
- Price action and trend analysis
- Technical indicators (RSI, MACD, Bollinger Bands)
- Support/resistance levels
- Chart pattern recognition
- Trading signals and recommendations
```

### Strategy Comparison
```
User: "Which performs better: RSI or SMA strategy for BTCUSDT?"

Agent: Runs backtests for both strategies and provides:
- Side-by-side performance comparison
- Risk-adjusted returns
- Trade statistics
- Recommendations based on results
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
GOOGLE_API_KEY=your_google_ai_api_key

# Optional
GOOGLE_GENAI_USE_VERTEXAI=FALSE
DEFAULT_INITIAL_CASH=100000.0
DEFAULT_COMMISSION=0.001
```

### Custom Parameters
Both agents support custom parameters:
- Initial cash amounts
- Commission rates
- Lookback periods
- Timeframes
- Strategy-specific parameters

## 📊 Performance Metrics

The system provides comprehensive performance analysis:

- **Returns**: Total return, annualized return
- **Risk Metrics**: Sharpe ratio, maximum drawdown, volatility
- **Trade Statistics**: Win rate, average trade, number of trades
- **Benchmark Comparison**: Performance vs buy-and-hold
- **Technical Analysis**: 20+ technical indicators

## 🔒 Safety Features

- Input validation for all parameters
- Error handling and graceful failures
- Rate limiting for data requests
- Comprehensive logging
- Risk warnings and disclaimers

## 🤝 Agent Collaboration

The agents can work together:
1. Market Research Agent analyzes market conditions
2. Backtest Agent creates strategies based on analysis
3. Combined insights for better decision making

## 📚 Project Structure

```
├── agent.py                 # Main ADK entry point
├── simplified_agents.py     # Simplified trading agents  
├── examples/
│   ├── demo_adk.py         # Demo script
│   └── verify_setup.py     # Setup verification
├── tests/
│   ├── test_simple_adk.py  # Simple ADK tests
│   └── test_agent_fix.py   # Agent fix tests
├── .env                    # Environment configuration
└── requirements.txt        # Dependencies
```

## 🚨 Important Notes

- **Paper Trading Only**: This system is for educational and research purposes
- **No Financial Advice**: All outputs are for informational purposes only
- **Backtesting Limitations**: Past performance doesn't guarantee future results
- **API Limits**: Respect data provider rate limits

## 🛟 Support

### Common Issues

1. **"Import error"** - Make sure you're in the project root directory
2. **"API key error"** - Verify your Google AI API key in `.env`
3. **"Data fetch failed"** - Check internet connection and try again

### Getting Help

- Check the demo script: `python examples/demo_adk.py`
- Review the ADK documentation
- Verify environment setup

## 🔄 Updates

The agents automatically use the latest market data and can be extended with:
- Additional trading strategies
- More technical indicators
- Additional data sources
- Custom analysis tools

---

**Disclaimer**: This software is for educational purposes only. Always consult with financial professionals before making investment decisions.
