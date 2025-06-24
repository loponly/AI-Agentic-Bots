#!/usr/bin/env python3
"""
Simple Trading Agent Demo
========================

A standalone demo showcasing the TradingAgent capabilities without requiring API keys.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'  # Go up one more level since we're in examples/
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Environment variables loaded from .env file")
    else:
        load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

from src.agents.trading_agent import TradingAgent


def main():
    """
    Demonstrate the TradingAgent functionality.
    """
    print("🤖 AI Trading Agent Demo")
    print("=" * 50)
    
    # Create a trading agent
    agent = TradingAgent(
        name="demo_trading_agent",
        initial_cash=100000.0
    )
    
    print(f"✅ Created agent: {agent.name}")
    print(f"💰 Initial cash: ${agent.initial_cash:,.2f}")
    
    # Demo 1: Invalid strategy handling
    print("\n📊 Demo 1: Strategy Validation")
    print("-" * 30)
    
    result = agent.run_backtest(
        strategy_name="invalid_strategy",
        start_date="2022-01-01",
        end_date="2023-12-31"
    )
    
    if 'error' in result:
        print(f"❌ Expected error for invalid strategy: {result['error']}")
    
    # Demo 2: Valid strategy backtest
    print("\n📈 Demo 2: SMA Strategy Backtest")
    print("-" * 30)
    
    result = agent.run_backtest(
        strategy_name="sma",
        start_date="2023-01-01",
        end_date="2023-06-30",
        strategy_params={
            "short_period": 10,
            "long_period": 20
        }
    )
    
    if result.get('success'):
        print(f"✅ Backtest completed successfully")
        print(f"📅 Period: {result['start_date']} to {result['end_date']}")
        print(f"💵 Initial Cash: ${result['initial_cash']:,.2f}")
        print(f"💰 Final Value: ${result.get('final_value', 0):,.2f}")
        print(f"📊 Total Trades: {result.get('total_trades', 0)}")
        print(f"🎯 Win Rate: {(result.get('win_rate', 0) * 100):.1f}%")
    else:
        print(f"❌ Backtest failed: {result.get('error', 'Unknown error')}")
    
    # Demo 3: Market data generation
    print("\n📈 Demo 3: Market Data Generation")
    print("-" * 30)
    
    data_result = agent.generate_market_data(
        start_date="2023-01-01",
        end_date="2023-03-31",
        initial_price=100,
        volatility=0.15
    )
    
    if data_result.get('success'):
        print(f"✅ Generated {data_result['data_points']} data points")
        print(f"📅 Period: {data_result['start_date']} to {data_result['end_date']}")
        print(f"💲 Initial Price: ${data_result['initial_price']}")
        print(f"📊 Volatility: {data_result['volatility']:.1%}")
        
        if 'sample_data' in data_result and data_result['sample_data']:
            print("📋 Sample Data (first few rows):")
            for i, row in enumerate(data_result['sample_data'][:3]):
                print(f"   {i+1}. Date: {row.get('date', 'N/A')}, Close: ${row.get('close', 0):.2f}")
    else:
        print(f"❌ Data generation failed: {data_result.get('error', 'Unknown error')}")
    
    # Demo 4: Trading decisions
    print("\n🎯 Demo 4: Trading Decision Making")
    print("-" * 30)
    
    # Test different market scenarios
    scenarios = [
        {
            "name": "Bullish Signal",
            "data": {
                'close': 105.50,
                'previous_close': 100.25,
                'portfolio_value': 110000,
                'position': 0
            }
        },
        {
            "name": "Bearish Signal",
            "data": {
                'close': 95.50,
                'previous_close': 100.25,
                'portfolio_value': 110000,
                'position': 100
            }
        },
        {
            "name": "Neutral Market",
            "data": {
                'close': 100.75,
                'previous_close': 100.25,
                'portfolio_value': 110000,
                'position': 0
            }
        }
    ]
    
    for scenario in scenarios:
        decision = agent.get_trading_decision(scenario["data"])
        print(f"📊 {scenario['name']}:")
        print(f"   Action: {decision['action']}")
        print(f"   Confidence: {decision['confidence']:.2f}")
        print(f"   Reasoning: {decision['reasoning']}")
        print(f"   Risk Level: {decision['risk_level']}")
        print()
    
    # Demo 5: Performance analysis
    print("📊 Demo 5: Performance Analysis")
    print("-" * 30)
    
    analysis = agent.analyze_strategy_performance()
    
    if 'error' not in analysis:
        print("✅ Analysis completed")
        if 'overall_rating' in analysis:
            print(f"🏆 Overall Rating: {analysis['overall_rating']}")
        if 'recommendations' in analysis:
            print("💡 Recommendations:")
            for rec in analysis.get('recommendations', []):
                print(f"   • {rec}")
    else:
        print(f"ℹ️  {analysis['error']}")
    
    print("\n🎉 Demo completed!")
    
    # Check API key status
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key and api_key != "your-google-api-key-here":
        print(f"\n✅ Google AI API key detected: {api_key[:10]}...{api_key[-4:]}")
        print("You can now use the full conversational AI features!")
        print("Run: python examples/trading_agent_example.py")
    else:
        print("\nTo use the full conversational AI features:")
        print("1. Get a Google AI API key from: https://aistudio.google.com/app/apikey")
        print("2. Add to .env file: GOOGLE_API_KEY=your-key-here")
        print("3. Run the full example: python examples/trading_agent_example.py")


if __name__ == "__main__":
    main()
