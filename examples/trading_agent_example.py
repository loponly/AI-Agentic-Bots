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


def binance_data_example():
    """
    Example of loading and using Binance cryptocurrency data.
    """
    print("\n=== Binance Data Integration Example ===")
    
    from src.data import DataProvider
    from src.data.providers import get_popular_binance_pairs, get_binance_pair_info
    from src.backtesting import BacktestEngine
    
    # Create data provider
    data_provider = DataProvider()
    
    # Get popular cryptocurrency trading pairs
    binance_pairs = get_popular_binance_pairs()
    pair_info = get_binance_pair_info()
    
    print("Loading cryptocurrency data from Binance...")
    print(f"Available pairs: {', '.join(binance_pairs[:10])}")  # Show first 10 pairs
    
    # Load multiple cryptocurrency pairs (with synthetic fallback)
    crypto_feeds = data_provider.load_binance_pairs(
        pairs=binance_pairs[:10],  # Use first 10 pairs
        interval='1d',
        start_time='2023-01-01',
        end_time='2023-12-31',
        use_synthetic_fallback=True
    )
    
    print(f"\n📊 Successfully loaded data for {len(crypto_feeds)} cryptocurrency pairs:")
    for pair, feed in crypto_feeds.items():
        info = pair_info.get(pair, {})
        pair_name = info.get('name', pair)
        category = info.get('category', 'crypto')
        
        price_range = f"${feed.data['low'].min():.2f} - ${feed.data['high'].max():.2f}"
        print(f"  🪙 {pair:<10} ({pair_name:<12}) | {category:<8} | {len(feed.data)} days | Range: {price_range}")
    
    # Run backtests on different cryptocurrency pairs
    if crypto_feeds:
        print(f"\n� Running backtests on cryptocurrency pairs...")
        
        agent = TradingAgent(name="crypto_trading_agent")
        results_summary = []
        
        # Test different strategies on different pairs
        strategies_to_test = [
            ('sma', {'short_period': 10, 'long_period': 30}),
            ('rsi', {'period': 14, 'oversold': 30, 'overbought': 70}),
            ('bollinger', {'period': 20, 'devfactor': 2.0})
        ]
        
        for pair, feed in list(crypto_feeds.items())[:3]:  # Test first 3 pairs
            print(f"\n--- Testing {pair} ({pair_info.get(pair, {}).get('name', pair)}) ---")
            
            for strategy_name, strategy_params in strategies_to_test:
                try:
                    backtest_result = agent.run_backtest(
                        strategy_name=strategy_name,
                        start_date="2023-01-01",
                        end_date="2023-12-31",
                        strategy_params=strategy_params,
                        data_feed=feed
                    )
                    
                    final_value = backtest_result.get('final_value', 0) or 0
                    total_return = backtest_result.get('total_return', 0) or 0
                    
                    results_summary.append({
                        'pair': pair,
                        'strategy': strategy_name.upper(),
                        'final_value': final_value,
                        'total_return': total_return
                    })
                    
                    print(f"  � {strategy_name.upper():<10} | Return: {total_return:>8.2%} | Value: ${final_value:>10,.2f}")
                    
                except Exception as e:
                    print(f"  ❌ {strategy_name.upper():<10} | Failed: {e}")
        
        # Summary
        if results_summary:
            print(f"\n📋 Cryptocurrency Trading Results Summary:")
            print("=" * 80)
            
            # Group by strategy
            by_strategy = {}
            for result in results_summary:
                strategy = result['strategy']
                if strategy not in by_strategy:
                    by_strategy[strategy] = []
                by_strategy[strategy].append(result)
            
            for strategy, results in by_strategy.items():
                print(f"\n{strategy} Strategy:")
                print("-" * 40)
                
                for result in results:
                    pair_name = pair_info.get(result['pair'], {}).get('name', result['pair'])
                    print(f"  {result['pair']:<10} ({pair_name:<12}) | {result['total_return']:>8.2%} | ${result['final_value']:>10,.2f}")
                
                # Strategy stats
                avg_return = sum(r['total_return'] for r in results) / len(results)
                best_result = max(results, key=lambda x: x['total_return'])
                print(f"  Average Return: {avg_return:8.2%} | Best: {best_result['pair']} ({best_result['total_return']:.2%})")
            
            print("=" * 80)
            
            # Overall best performer
            best_overall = max(results_summary, key=lambda x: x['total_return'])
            worst_overall = min(results_summary, key=lambda x: x['total_return'])
            
            print(f"🏆 Best Overall:  {best_overall['pair']} with {best_overall['strategy']} ({best_overall['total_return']:.2%})")
            print(f"📉 Worst Overall: {worst_overall['pair']} with {worst_overall['strategy']} ({worst_overall['total_return']:.2%})")
    
    else:
        print("❌ No cryptocurrency data could be loaded or generated.")
    
    print(f"\n💡 Available pairs for trading: {', '.join(binance_pairs)}")
    print("   📡 To use real-time data, configure Binance API credentials in the DataProvider.")
    print("   🔧 Current implementation uses synthetic data with realistic crypto characteristics.")


if __name__ == "__main__":
    # Run the main async example
    print("=== AI Trading Agent Example ===")
    print("Note: Make sure to set your GOOGLE_API_KEY environment variable")
    
    # Run synchronous examples first
    synchronous_example()
    strategy_integration_example()
    binance_data_example()  # New cryptocurrency data example
    
    # Run async example (requires API key)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nAsync example failed (likely missing API key): {e}")
        print("Set GOOGLE_API_KEY environment variable to run the full example")
