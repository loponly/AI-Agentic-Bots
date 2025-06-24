"""
Trading Agent Example Usage
==========================

This example demonstrates how to use the TradingAgent class for intelligent 
trading strategy execution and analysis.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        load_dotenv()
        print("✅ Loaded environment variables from current directory")
except ImportError:
    print("⚠️  python-dotenv not installed. Please set environment variables manually.")

import asyncio
from src.agents.trading_agent import TradingAgent, TradingAgentStrategy


async def main():
    """
    Example usage of the TradingAgent.
    """
    # Check if API key is loaded
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key == "your-google-api-key-here":
        print("⚠️  No valid GOOGLE_API_KEY found in environment variables.")
        print("   Please set your API key in the .env file or as an environment variable.")
        print("   Get your key from: https://aistudio.google.com/app/apikey")
        return
    
    print(f"✅ Using Google AI API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Create a trading agent
    agent = TradingAgent(
        name="advanced_trading_agent",
        model="gemini-2.0-flash",
        initial_cash=100000.0
    )
    
    # Setup session for conversation
    session_id = await agent.setup_session()
    print(f"Created session: {session_id}")
    
    # Example 1: Run a backtest
    print("\n=== Running Backtest ===")
    backtest_result = agent.run_backtest(
        strategy_name="sma",
        start_date="2022-01-01",
        end_date="2023-12-31",
        strategy_params={
            "short_period": 10,
            "long_period": 30
        }
    )
    print("Backtest Results:", backtest_result)
    
    # Example 2: Analyze strategy performance
    print("\n=== Analyzing Performance ===")
    analysis = agent.analyze_strategy_performance()
    print("Performance Analysis:", analysis)
    
    # Example 3: Generate market data
    print("\n=== Generating Market Data ===")
    data_result = agent.generate_market_data(
        start_date="2023-01-01",
        end_date="2023-06-30",
        initial_price=150,
        volatility=0.25
    )
    print("Data Generation:", data_result)
    
    # Example 4: Get trading decision
    print("\n=== Getting Trading Decision ===")
    market_data = {
        'close': 105.50,
        'open': 104.25,
        'high': 106.00,
        'low': 103.75,
        'volume': 1000000,
        'date': '2023-12-01',
        'portfolio_value': 110000,
        'cash': 50000,
        'position': 0,
        'previous_close': 103.25
    }
    decision = agent.get_trading_decision(market_data)
    print("Trading Decision:", decision)
    
    # Example 5: Chat with the agent
    print("\n=== Chatting with Agent ===")
    
    # Ask about strategy recommendations
    response1 = await agent.chat(
        "What's the best strategy for a volatile market?",
        user_id="trader_1",
        session_id=session_id
    )
    print("Agent:", response1)
    
    # Ask for risk management advice
    response2 = await agent.chat(
        "How should I manage risk when trading with $100,000 capital?",
        user_id="trader_1",
        session_id=session_id
    )
    print("Agent:", response2)
    
    # Ask to run a specific backtest
    response3 = await agent.chat(
        "Can you run a backtest using the RSI strategy with 14-day period from 2022 to 2023?",
        user_id="trader_1",
        session_id=session_id
    )
    print("Agent:", response3)


def synchronous_example():
    """
    Example of using the agent tools directly without conversation.
    """
    print("\n=== Synchronous Usage Example ===")
    
    # Create agent (without session setup for direct tool usage)
    agent = TradingAgent(
        name="sync_trading_agent",
        initial_cash=50000.0
    )
    
    # Direct tool usage
    print("\n1. Running backtest directly:")
    result = agent.run_backtest(
        strategy_name="bollinger",
        start_date="2023-01-01",
        end_date="2023-06-30",
        strategy_params={
            "period": 20,
            "devfactor": 2.0
        }
    )
    print(f"   Final Value: ${result.get('final_value', 0) or 0:,.2f}")
    print(f"   Total Return: {(result.get('total_return', 0) or 0):.2%}")
    print(f"   Sharpe Ratio: {result.get('sharpe_ratio', 0) or 0:.2f}")
    
    print("\n2. Analyzing performance:")
    analysis = agent.analyze_strategy_performance()
    if 'overall_rating' in analysis:
        print(f"   Overall Rating: {analysis['overall_rating']}")
        print(f"   Recommendations: {analysis.get('recommendations', [])}")
    
    print("\n3. Making trading decision:")
    market_data = {
        'close': 98.75,
        'previous_close': 100.25,
        'portfolio_value': 52000,
        'position': 100
    }
    decision = agent.get_trading_decision(market_data)
    print(f"   Action: {decision['action']}")
    print(f"   Confidence: {decision['confidence']:.2f}")
    print(f"   Reasoning: {decision['reasoning']}")


def strategy_integration_example():
    """
    Example of using TradingAgentStrategy in a traditional backtest.
    """
    print("\n=== Strategy Integration Example ===")
    
    from src.data import DataProvider
    from src.backtesting import BacktestEngine
    
    # Create components
    data_provider = DataProvider()
    agent = TradingAgent(name="strategy_agent")
    
    # Generate data
    data_feed = data_provider.generate_synthetic(
        start_date='2023-01-01',
        end_date='2023-12-31',
        initial_price=100
    )
    
    # Run backtest with agent-driven strategy
    engine = BacktestEngine(initial_cash=100000)
    results = engine.run_backtest(
        data_feed=data_feed,
        strategy_class=TradingAgentStrategy,
        strategy_params={
            'agent_enabled': True,
            'risk_tolerance': 0.02,
            'max_position_size': 0.1
        }
    )
    
    print(f"Agent-driven strategy results:")
    print(f"   Final Value: ${results.get('final_portfolio_value', 0):,.2f}")
    print(f"   Total Return: {results.get('total_return', 0):.2%}")


if __name__ == "__main__":
    # Run the main async example
    print("=== AI Trading Agent Example ===")
    print("Note: Make sure to set your GOOGLE_API_KEY environment variable")
    
    # Run synchronous examples first
    synchronous_example()
    strategy_integration_example()
    
    # Run async example (requires API key)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nAsync example failed (likely missing API key): {e}")
        print("Set GOOGLE_API_KEY environment variable to run the full example")
