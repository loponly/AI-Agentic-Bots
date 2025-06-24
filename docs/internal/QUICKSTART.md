# 🤖 ADK Trading Agents - Quick Start Guide

Welcome to the ADK-powered multi-agent cryptocurrency trading system! This guide will get you up and running in minutes.

## ⚡ Quick Start (3 steps)

### 1. Verify Setup
```bash
python examples/verify_setup.py
```
✅ Should show "Setup Complete! Ready to launch ADK agents"

### 2. Launch Web Interface
```bash
adk web
```
🌐 Opens browser interface for chatting with agents

### 3. Start Trading Analysis
Try these example questions:
- "What trading strategies work best for beginners?"
- "Analyze current market trends for Bitcoin"
- "Generate trading signals for ETHUSDT"
- "Compare RSI and momentum strategies"

## 🎯 Available Agents

### 📈 Strategy Agent
**Best for strategy development and learning**
- Analyzes SMA, RSI, and Momentum strategies
- Explains strategy parameters and risks
- Provides implementation guidance
- Recommends strategies for different market conditions

**Example questions:**
- "How does RSI strategy work?"
- "Which strategy is best for volatile markets?"
- "Explain momentum trading risks"

### 📊 Market Research Agent  
**Best for market analysis and signals**
- Analyzes market trends across cryptocurrencies
- Generates trading signals with reasoning
- Compares asset performance
- Provides market sentiment analysis

**Example questions:**
- "What's the Bitcoin trend today?"
- "Compare BTC vs ETH performance"
- "Generate trading signals for major cryptos"

## 🖥️ Interface Options

| Command | Description | Best For |
|---------|-------------|----------|
| `adk web` | Browser-based chat UI | Most users (recommended) |
| `adk run` | Terminal interface | Command-line users |
| `adk api_server` | REST API server | Developers/Integration |

## 🔧 Troubleshooting

**Agent doesn't respond?**
- Check GOOGLE_API_KEY in .env file
- Verify internet connection

**Import errors?**
- Run from project root directory
- Check: `python examples/verify_setup.py`

**Web UI won't start?**
- Ensure google-adk is installed: `pip install google-adk`
- Try: `pip install -r requirements.txt`

## 💡 Tips for Best Results

1. **Be specific** - Mention the cryptocurrency you're interested in
2. **Ask follow-up questions** - Agents can elaborate on any topic
3. **Request examples** - Ask for step-by-step guidance
4. **Specify timeframes** - "daily trends" vs "weekly performance"
5. **Ask for comparisons** - "Compare strategy A vs B"

## 🛡️ Important Notes

- **Educational Purpose Only** - Not financial advice
- **Paper Trading First** - Practice before real money
- **Risk Management** - Always consider volatility and risks
- **Do Your Research** - Agents provide analysis, you make decisions

## 📚 Sample Conversations

### Strategy Learning
```
You: "I'm new to trading. What strategy should I start with?"

Agent: "For beginners, I recommend starting with SMA (Simple Moving Average) strategy because:
1. Easy to understand - uses basic price averages
2. Lower complexity - fewer parameters to manage
3. Good for learning - shows clear entry/exit signals
4. Moderate risk - not as aggressive as momentum strategies

The SMA strategy uses two moving averages (like 10-day and 30-day). When the short average crosses above the long average, it signals a potential buy..."
```

### Market Analysis
```
You: "What's happening with Bitcoin today?"

Agent: "Based on current market data:
📈 BTC/USDT: $43,250 (+2.45% 24h)
📊 Trend: Bullish momentum with strong volume
🎯 Signals: Showing buy signals on RSI and momentum indicators
⚠️ Note: Market is volatile, monitor for reversal patterns..."
```

## 🚀 Advanced Features

- **Multi-timeframe analysis** - "Compare 1-hour vs daily trends"
- **Risk assessment** - "What are the risks of momentum trading?"
- **Strategy comparison** - "RSI vs Bollinger Bands for ETHUSDT"
- **Market sentiment** - "What's the overall crypto market sentiment?"

---

**Ready to start?** Run `adk web` and begin your trading analysis journey! 🚀

*Remember: This is for educational purposes only. Always do your own research and consider consulting financial professionals before making investment decisions.*
