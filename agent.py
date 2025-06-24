#!/usr/bin/env python3
"""
Multi-Agent Trading System with ADK
===================================

This module creates a multi-agent system using ADK that includes:
1. Backtest Strategy Agent - Creates and tests trading strategies
2. Market Research Agent - Performs market analysis and research

The agents can work together or independently to provide comprehensive
trading insights and strategy development.
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # Load from current working directory
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

from google.adk.agents import Agent

# Import our simplified agents for reliable operation
from simplified_agents import (
    simplified_backtest_agent, 
    simplified_market_agent,
    get_available_tools,
    get_market_data_info
)


def get_agent_info() -> dict:
    """
    Get information about available agents and their capabilities.
    
    Returns:
        dict: Information about all available agents
    """
    return {
        "available_agents": {
            "backtest_agent": {
                "name": "Trading Strategy Agent",
                "description": "Analyzes and develops trading strategies with performance insights",
                "capabilities": [
                    "Analyze SMA, RSI, and Momentum strategies",
                    "Provide strategy recommendations",
                    "Assess market fit for different strategies",
                    "Explain strategy parameters and risks",
                    "Generate implementation guidance"
                ],
                "example_queries": [
                    "Analyze an RSI strategy for BTCUSDT",
                    "Which strategy works best in current market conditions?",
                    "Explain how momentum strategies work"
                ]
            },
            "market_research_agent": {
                "name": "Market Research Agent",
                "description": "Performs comprehensive market analysis and generates trading insights",
                "capabilities": [
                    "Analyze market trends across multiple assets",
                    "Generate trading signals and recommendations",
                    "Compare cryptocurrency performance",
                    "Assess market sentiment and risk levels",
                    "Provide technical analysis insights"
                ],
                "example_queries": [
                    "What's the current trend for major cryptocurrencies?",
                    "Generate trading signals for ETHUSDT",
                    "Compare BTC and ETH performance"
                ]
            }
        },
        "system_info": {
            "supported_assets": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"],
            "supported_strategies": ["SMA", "RSI", "Momentum"],
            "analysis_types": ["Trend", "Performance", "Risk"],
            "data_source": "Real-time cryptocurrency market data"
        }
    }


def route_to_agent(query: str) -> dict:
    """
    Route user queries to the appropriate agent based on intent.
    
    Args:
        query: User query string
    
    Returns:
        dict: Routing recommendation with explanation
    """
    query_lower = query.lower()
    
    # Keywords for backtest/strategy agent
    strategy_keywords = [
        'strategy', 'sma', 'rsi', 'momentum', 'backtest', 'optimize',
        'parameter', 'create strategy', 'test strategy', 'strategy analysis',
        'trading strategy', 'strategy comparison'
    ]
    
    # Keywords for market research agent
    market_keywords = [
        'market', 'trend', 'analysis', 'signal', 'sentiment', 'performance',
        'compare', 'research', 'technical', 'price', 'crypto', 'bitcoin',
        'ethereum', 'trading signal', 'market data'
    ]
    
    strategy_score = sum(1 for keyword in strategy_keywords if keyword in query_lower)
    market_score = sum(1 for keyword in market_keywords if keyword in query_lower)
    
    if strategy_score > market_score:
        recommended_agent = "strategy_agent"
        explanation = "Your query involves strategy analysis and development"
    elif market_score > strategy_score:
        recommended_agent = "market_agent"
        explanation = "Your query involves market research and analysis"
    else:
        recommended_agent = "market_agent"  # Default to market research
        explanation = "I'll route this to market research for general analysis"
    
    return {
        "recommended_agent": recommended_agent,
        "explanation": explanation,
        "confidence": max(strategy_score, market_score),
        "query": query
    }


def show_system_capabilities() -> dict:
    """
    Show comprehensive system capabilities and usage examples.
    
    Returns:
        dict: System capabilities and examples
    """
    return {
        "system_overview": "Multi-agent cryptocurrency trading analysis system",
        "agents": {
            "strategy_agent": {
                "focus": "Trading strategy development and analysis",
                "best_for": [
                    "Learning about different trading strategies",
                    "Getting strategy recommendations",
                    "Understanding strategy parameters",
                    "Risk assessment of strategies"
                ]
            },
            "market_agent": {
                "focus": "Market research and technical analysis", 
                "best_for": [
                    "Current market condition analysis",
                    "Trading signal generation",
                    "Multi-asset comparison",
                    "Trend and sentiment analysis"
                ]
            }
        },
        "example_workflows": {
            "beginner_trader": [
                "Ask: 'What trading strategies are good for beginners?'",
                "Ask: 'Show me current market trends for major cryptos'",
                "Ask: 'How risky is momentum trading?'"
            ],
            "strategy_development": [
                "Ask: 'Analyze RSI strategy for current market conditions'",
                "Ask: 'Compare SMA vs RSI strategies'",
                "Ask: 'What parameters work best for momentum strategy?'"
            ],
            "market_analysis": [
                "Ask: 'What's the market sentiment today?'",
                "Ask: 'Generate trading signals for BTCUSDT'",
                "Ask: 'Compare performance of BTC, ETH, and ADA'"
            ]
        },
        "getting_started": [
            "Simply ask questions in natural language",
            "Specify which cryptocurrency you're interested in",
            "Ask for explanations if anything is unclear",
            "Request examples or step-by-step guidance"
        ]
    }


# Create the main coordinating agent that users will interact with
root_agent = Agent(
    name="crypto_trading_coordinator",
    description="Multi-agent cryptocurrency trading analysis system coordinator",
    instruction="""You are the main coordinator for a sophisticated cryptocurrency trading analysis system.

You have access to two specialized agents:

🎯 **Strategy Agent** - Specializes in:
- Trading strategy analysis (SMA, RSI, Momentum)
- Strategy parameter recommendations
- Performance expectations and risk assessment
- Implementation guidance and best practices

📊 **Market Research Agent** - Specializes in:
- Real-time market trend analysis
- Trading signal generation
- Multi-asset performance comparison
- Market sentiment and technical analysis

**Your Role:**
1. Help users understand what each agent can do
2. Route questions to the most appropriate agent
3. Provide system overview and capabilities
4. Guide users through effective use of the system

**When users ask questions:**
- Analyze their intent and recommend the best agent
- Explain what that agent can help them with
- Provide clear guidance on how to get the best results
- Offer examples of effective queries

**Key Principles:**
- Always be helpful and educational
- Explain cryptocurrency trading concepts clearly
- Emphasize risk management and education
- Provide realistic expectations about trading
- Include appropriate disclaimers about market risks

You can help with both beginner questions and advanced analysis needs.""",
    
    tools=[
        get_agent_info,
        route_to_agent,
        show_system_capabilities,
        get_available_tools,
        get_market_data_info
    ]
)


if __name__ == "__main__":
    print("🤖 Multi-Agent Cryptocurrency Trading System")
    print("=" * 50)
    print("\nThis system provides two specialized AI agents:")
    print("1. 🎯 Strategy Agent - Trading strategy analysis and development")
    print("2. 📊 Market Research Agent - Market analysis and trading signals")
    print("\n🚀 To get started:")
    print("   adk web      - Launch web interface (recommended)")
    print("   adk run      - Terminal interface")
    print("   adk api_server - Start API server")
    print("\n💡 Example questions:")
    print("   • 'What trading strategies work best for beginners?'")
    print("   • 'Analyze current market trends for Bitcoin'")
    print("   • 'Generate trading signals for ETHUSDT'")
    print("   • 'Compare RSI and SMA strategies'")
    print("\n⚠️  Educational purposes only - not financial advice!")
