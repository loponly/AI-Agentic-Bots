#!/usr/bin/env python3
"""
ADK Agents Demo
==============

This script demonstrates how to interact with the ADK trading agents
both programmatically and through the web interface.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path (from examples/ subdirectory)
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed")

async def demo_agents():
    """Demo the ADK agents functionality."""
    
    print("🤖 ADK Trading Agents Demo")
    print("=" * 40)
    
    # Import ADK components
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai import types
    
    # Import our agents
    # Add parent directory to path first
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    
    from src.adk_agents.backtest_agent import backtest_agent
    from src.adk_agents.market_research_agent import market_research_agent
    
    # Setup session service
    session_service = InMemorySessionService()
    
    # Create session
    session = await session_service.create_session(
        app_name="trading_demo",
        session_id="demo_session"
    )
    
    print("✓ Session created")
    
    # Demo Market Research Agent
    print("\n1. Testing Market Research Agent...")
    print("-" * 35)
    
    research_runner = Runner(
        agent=market_research_agent,
        session_service=session_service
    )
    
    # Test market trends analysis
    query = "Analyze current market trends for BTC, ETH, and ADA"
    print(f"Query: {query}")
    
    async for event in research_runner.run_async(
        user_id="demo_user",
        session_id="demo_session",
        new_messages=[types.Content(parts=[types.Part(text=query)])]
    ):
        if event.is_final_response():
            print(f"Response: {event.response.text[:200]}...")
            break
    
    # Demo Backtest Agent
    print("\n2. Testing Backtest Strategy Agent...")
    print("-" * 40)
    
    backtest_runner = Runner(
        agent=backtest_agent,
        session_service=session_service
    )
    
    # Test strategy creation
    query = "Create and run a backtest for RSI strategy on BTCUSDT"
    print(f"Query: {query}")
    
    async for event in backtest_runner.run_async(
        user_id="demo_user",
        session_id="demo_session",
        new_messages=[types.Content(parts=[types.Part(text=query)])]
    ):
        if event.is_final_response():
            print(f"Response: {event.response.text[:200]}...")
            break
    
    print("\n✓ Demo completed!")
    print("\nTo run the full web interface:")
    print("  adk web")
    print("\nTo run in terminal mode:")
    print("  adk run")


def print_usage():
    """Print usage instructions."""
    print("🤖 ADK Trading Agents")
    print("=" * 30)
    print("\nAvailable Commands:")
    print("1. adk web        - Launch web interface")
    print("2. adk run        - Run in terminal")
    print("3. adk api_server - Start API server")
    print("4. python examples/demo_adk.py demo - Run this demo")
    print("\nAvailable Agents:")
    print("• Backtest Strategy Agent - Create and test trading strategies")
    print("• Market Research Agent   - Analyze markets and trends")
    print("\nExample Queries:")
    print("• 'Create an SMA strategy backtest for BTCUSDT'")
    print("• 'Analyze market trends for major cryptocurrencies'")
    print("• 'Compare RSI and Bollinger Bands strategies'")
    print("• 'What's the current market sentiment?'")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        try:
            asyncio.run(demo_agents())
        except Exception as e:
            print(f"Demo failed: {e}")
            print("Make sure you have set GOOGLE_API_KEY in .env file")
    else:
        print_usage()
