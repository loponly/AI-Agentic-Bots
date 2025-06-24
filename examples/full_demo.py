#!/usr/bin/env python3
"""
Full TradingAgent Demo with Conversational AI
============================================

A comprehensive demo showcasing both the direct tool usage and 
conversational AI capabilities of the TradingAgent.
"""

import sys
import os
from pathlib import Path
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'  # Go up one more level since we're in examples/
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Environment variables loaded from .env file")
except ImportError:
    pass

from src.agents.trading_agent import TradingAgent


async def conversational_demo():
    """Demonstrate the conversational AI capabilities."""
    print("\n🤖 === Conversational AI Demo ===")
    print("=" * 50)
    
    # Check API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key == "your-google-api-key-here":
        print("⚠️  No valid GOOGLE_API_KEY found.")
        print("   This demo requires a Google AI API key for conversational features.")
        return
    
    print(f"✅ Using Google AI API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Create agent
    agent = TradingAgent(
        name="conversational_trading_agent",
        model="gemini-2.0-flash",
        initial_cash=100000.0
    )
    
    # Setup session
    session_id = await agent.setup_session()
    print(f"📱 Created session: {session_id}")
    
    # List of questions to ask the agent
    questions = [
        "What's the best trading strategy for a beginner with $10,000 to invest?",
        "Can you run a backtest using the SMA strategy from 2022 to 2023 with 10 and 30 day periods?",
        "How should I manage risk when trading volatile stocks?",
        "Generate some market data for backtesting - use 6 months of data starting from 2023-01-01 with high volatility",
        "Based on current market conditions with a 3% upward movement, should I buy or sell?"
    ]
    
    print("\n🗣️  Starting conversation with AI Trading Agent...")
    print("-" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n👤 User: {question}")
        print("🤖 Agent: ", end="")
        
        try:
            response = await agent.chat(
                message=question,
                user_id="demo_user",
                session_id=session_id
            )
            print(response)
            
            # Add a small delay between questions
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Conversational demo completed!")


def direct_tools_demo():
    """Demonstrate direct tool usage without conversation."""
    print("\n🔧 === Direct Tools Demo ===")
    print("=" * 40)
    
    agent = TradingAgent(
        name="tools_demo_agent",
        initial_cash=50000.0
    )
    
    print("✅ Created agent for direct tool usage")
    
    # Demo 1: Valid backtest
    print("\n📊 Running SMA Strategy Backtest:")
    result = agent.run_backtest(
        strategy_name="sma",
        start_date="2023-01-01",
        end_date="2023-06-30",
        strategy_params={"short_period": 5, "long_period": 15}
    )
    
    if result.get('success'):
        print(f"   ✅ Strategy: {result['strategy']}")
        print(f"   📈 Total Return: {(result.get('total_return', 0) or 0):.2%}")
        print(f"   📊 Sharpe Ratio: {result.get('sharpe_ratio', 0) or 0:.2f}")
        print(f"   🎯 Max Drawdown: {(result.get('max_drawdown', 0) or 0):.2f}")
    else:
        print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    
    # Demo 2: Performance analysis
    print("\n📈 Performance Analysis:")
    analysis = agent.analyze_strategy_performance()
    
    if 'overall_rating' in analysis:
        print(f"   🏆 Rating: {analysis['overall_rating']}")
        if 'recommendations' in analysis:
            print("   💡 Top Recommendations:")
            for rec in analysis['recommendations'][:2]:
                print(f"      • {rec}")
    else:
        print(f"   ℹ️  {analysis.get('error', 'No analysis available')}")
    
    # Demo 3: Market data generation
    print("\n📊 Market Data Generation:")
    data = agent.generate_market_data(
        start_date="2023-01-01",
        end_date="2023-03-31",
        initial_price=120,
        volatility=0.18
    )
    
    if data.get('success'):
        print(f"   ✅ Generated {data['data_points']} data points")
        print(f"   📅 Period: {data['start_date']} to {data['end_date']}")
        print(f"   💲 Starting Price: ${data['initial_price']}")
        print(f"   📊 Volatility: {data['volatility']:.1%}")
    else:
        print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
    
    # Demo 4: Trading decisions
    print("\n🎯 Trading Decision Examples:")
    
    scenarios = [
        ("Strong Bull Signal", {'close': 115, 'previous_close': 108, 'position': 0}),
        ("Bear Market", {'close': 92, 'previous_close': 98, 'position': 50}),
        ("Sideways Market", {'close': 100.5, 'previous_close': 100.2, 'position': 0})
    ]
    
    for scenario_name, market_data in scenarios:
        decision = agent.get_trading_decision({
            **market_data,
            'portfolio_value': 55000,
            'cash': 25000
        })
        
        print(f"   📊 {scenario_name}:")
        print(f"      Action: {decision['action']} (Confidence: {decision['confidence']:.2f})")
        print(f"      Reason: {decision['reasoning']}")


async def main():
    """Run the comprehensive demo."""
    print("🚀 TradingAgent Comprehensive Demo")
    print("=" * 60)
    
    # Run direct tools demo first (no API key required)
    direct_tools_demo()
    
    # Then run conversational demo (requires API key)
    await conversational_demo()
    
    print("\n🎯 Demo Summary:")
    print("✅ Direct tool usage - Works without API key")
    print("✅ Conversational AI - Requires Google AI API key")
    print("✅ Strategy backtesting - SMA, RSI, Bollinger Bands")
    print("✅ Performance analysis - Comprehensive metrics")
    print("✅ Market data generation - Synthetic data for testing")
    print("✅ Trading decisions - AI-powered recommendations")
    
    print("\n📚 Next Steps:")
    print("• Integrate with real market data feeds")
    print("• Add more sophisticated trading strategies")
    print("• Implement portfolio optimization")
    print("• Connect to live trading platforms")


if __name__ == "__main__":
    asyncio.run(main())
