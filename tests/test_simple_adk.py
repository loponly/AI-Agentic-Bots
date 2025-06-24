#!/usr/bin/env python3
"""
Simple ADK Agent Test
====================

Test basic ADK functionality without complex imports.
"""

import os
import sys
from pathlib import Path

# Add src to path (from tests/ subdirectory)
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed")

from google.adk.agents import Agent


def simple_market_info() -> dict:
    """
    Get basic market information without complex imports.
    
    Returns:
        dict: Basic market info
    """
    return {
        "supported_assets": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"],
        "supported_timeframes": ["1h", "4h", "1d", "1w"],
        "available_strategies": ["SMA", "RSI", "Bollinger Bands", "Momentum"],
        "default_settings": {
            "initial_cash": 100000,
            "commission": 0.001,
            "lookback_days": 365
        },
        "status": "ADK system is operational"
    }


def get_trading_help() -> dict:
    """
    Get help information for using the trading system.
    
    Returns:
        dict: Help information
    """
    return {
        "agent_types": {
            "backtest_agent": "Creates and tests trading strategies",
            "market_research_agent": "Analyzes markets and trends"
        },
        "example_queries": {
            "strategy_development": [
                "Create an SMA strategy for BTCUSDT",
                "Compare RSI and Bollinger Bands strategies",
                "Optimize momentum strategy parameters"
            ],
            "market_analysis": [
                "Analyze market trends for major cryptocurrencies",
                "Perform technical analysis on ETHUSDT",
                "What's the current market sentiment?"
            ]
        },
        "web_interface_commands": [
            "adk web - Launch web interface",
            "adk run - Terminal interface", 
            "adk api_server - Start API server"
        ]
    }


# Create a simple test agent
simple_trading_agent = Agent(
    name="simple_trading_helper",
    description="Basic trading system helper and information provider",
    instruction="""You are a helpful trading system assistant. 

You can provide information about:
- Available trading strategies and assets
- How to use the trading system
- Basic market information
- Help with getting started

When users ask for help, provide clear, actionable guidance about using the trading agents and their capabilities.""",
    
    tools=[
        simple_market_info,
        get_trading_help
    ]
)


def test_simple_agent():
    """Test the simple agent setup."""
    print("🧪 Testing Simple ADK Agent Setup")
    print("=" * 40)
    
    try:
        # Test that agent was created successfully
        print(f"✓ Agent created: {simple_trading_agent.name}")
        print(f"✓ Agent description: {simple_trading_agent.description}")
        print(f"✓ Number of tools: {len(simple_trading_agent.tools)}")
        
        # Test the tools directly
        print("\n📊 Testing tools...")
        
        market_info = simple_market_info()
        print(f"✓ Market info tool: {market_info['status']}")
        
        help_info = get_trading_help()
        print(f"✓ Help tool: Found {len(help_info['agent_types'])} agent types")
        
        print("\n🎉 Simple agent test passed!")
        print("\nNext steps:")
        print("1. Set GOOGLE_API_KEY in .env file")
        print("2. Run: adk web")
        print("3. Start chatting with the agents!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_simple_agent()
    sys.exit(0 if success else 1)
