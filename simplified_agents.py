#!/usr/bin/env python3
"""
Simplified ADK Agents for Trading System
========================================

This module contains simplified versions of the trading agents that can work
independently of the complex strategy infrastructure while still providing
valuable trading insights.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from google.adk.agents import Agent


def get_market_data_info(symbol: str = "BTCUSDT") -> dict:
    """
    Get basic market data information for a symbol.
    
    Args:
        symbol: Trading symbol (e.g., 'BTCUSDT', 'ETHUSDT')
    
    Returns:
        dict: Market data information
    """
    try:
        # For demo purposes, return mock market data info
        # In production, this would connect to real data sources
        
        mock_data = {
            "BTCUSDT": {"price": 43250.0, "24h_change": 2.45, "volume": 28450000000},
            "ETHUSDT": {"price": 2685.0, "24h_change": 1.85, "volume": 12350000000},
            "ADAUSDT": {"price": 0.485, "24h_change": -0.95, "volume": 450000000},
            "BNBUSDT": {"price": 315.0, "24h_change": 3.25, "volume": 890000000},
            "XRPUSDT": {"price": 0.625, "24h_change": 1.15, "volume": 1250000000}
        }
        
        data = mock_data.get(symbol, mock_data["BTCUSDT"])
        
        return {
            "success": True,
            "symbol": symbol,
            "current_price": data["price"],
            "price_change_24h": data["24h_change"],
            "volume_24h": data["volume"],
            "timestamp": datetime.now().isoformat(),
            "data_source": "Demo data - Replace with real API in production"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get market data for {symbol}: {str(e)}",
            "symbol": symbol
        }


def create_simple_strategy_analysis(
    strategy_type: str,
    symbol: str = "BTCUSDT",
    lookback_days: int = 30
) -> dict:
    """
    Create a simple strategy analysis without complex backtesting.
    
    Args:
        strategy_type: Type of strategy ('sma', 'rsi', 'momentum')
        symbol: Trading symbol
        lookback_days: Number of days to analyze
    
    Returns:
        dict: Strategy analysis results
    """
    try:
        # Generate mock analysis results
        # In production, this would run actual backtests
        
        strategies = {
            "sma": {
                "name": "Simple Moving Average Crossover",
                "description": "Uses 10-day and 30-day moving averages",
                "parameters": {"short_period": 10, "long_period": 30},
                "expected_return": 15.5,
                "risk_level": "Medium",
                "win_rate": 65.2
            },
            "rsi": {
                "name": "Relative Strength Index",
                "description": "Uses RSI with 70/30 thresholds",
                "parameters": {"period": 14, "overbought": 70, "oversold": 30},
                "expected_return": 12.8,
                "risk_level": "Medium-High",
                "win_rate": 58.7
            },
            "momentum": {
                "name": "Momentum Strategy",
                "description": "Uses price momentum and volume",
                "parameters": {"lookback": 14, "volume_threshold": 1.5},
                "expected_return": 18.2,
                "risk_level": "High",
                "win_rate": 62.1
            }
        }
        
        strategy_info = strategies.get(strategy_type.lower())
        if not strategy_info:
            return {
                "error": f"Unknown strategy type: {strategy_type}",
                "available_strategies": list(strategies.keys())
            }
        
        # Simulate some market analysis
        market_data = get_market_data_info(symbol)
        
        return {
            "success": True,
            "strategy": strategy_type,
            "symbol": symbol,
            "analysis_period": f"{lookback_days} days",
            "strategy_info": strategy_info,
            "market_conditions": {
                "current_price": market_data.get("current_price", 0),
                "trend": "Bullish" if market_data.get("price_change_24h", 0) > 0 else "Bearish",
                "volatility": "Normal"
            },
            "recommendations": {
                "strategy_fit": "Good" if strategy_info["expected_return"] > 15 else "Moderate",
                "risk_warning": f"This is a {strategy_info['risk_level']} risk strategy",
                "next_steps": [
                    "Consider paper trading first",
                    "Set appropriate position sizes",
                    "Monitor market conditions"
                ]
            },
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Strategy analysis failed: {str(e)}",
            "strategy": strategy_type,
            "symbol": symbol
        }


def analyze_multiple_assets(
    assets: List[str] = None,
    analysis_type: str = "trend"
) -> dict:
    """
    Analyze multiple cryptocurrency assets.
    
    Args:
        assets: List of asset symbols to analyze
        analysis_type: Type of analysis ('trend', 'performance', 'risk')
    
    Returns:
        dict: Multi-asset analysis results
    """
    try:
        assets = assets or ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT"]
        
        results = {}
        
        for asset in assets:
            market_data = get_market_data_info(asset)
            
            if market_data.get("success"):
                price_change = market_data["price_change_24h"]
                
                if analysis_type == "trend":
                    trend = "Bullish" if price_change > 1 else "Bearish" if price_change < -1 else "Neutral"
                    strength = "Strong" if abs(price_change) > 3 else "Moderate" if abs(price_change) > 1 else "Weak"
                    
                    results[asset] = {
                        "trend": trend,
                        "strength": strength,
                        "price_change": price_change,
                        "price": market_data["current_price"]
                    }
                
                elif analysis_type == "performance":
                    performance_score = min(100, max(0, 50 + (price_change * 2)))
                    
                    results[asset] = {
                        "performance_score": round(performance_score, 1),
                        "price_change": price_change,
                        "volume": market_data["volume_24h"],
                        "price": market_data["current_price"]
                    }
                
                elif analysis_type == "risk":
                    # Simple risk assessment based on volatility proxy
                    volatility = abs(price_change)
                    risk_level = "High" if volatility > 5 else "Medium" if volatility > 2 else "Low"
                    
                    results[asset] = {
                        "risk_level": risk_level,
                        "volatility_proxy": round(volatility, 2),
                        "price_change": price_change,
                        "price": market_data["current_price"]
                    }
            else:
                results[asset] = {"error": "Failed to fetch data"}
        
        # Summary statistics
        successful_analyses = [r for r in results.values() if "error" not in r]
        
        if successful_analyses and analysis_type == "trend":
            bullish_count = len([r for r in successful_analyses if r.get("trend") == "Bullish"])
            bearish_count = len([r for r in successful_analyses if r.get("trend") == "Bearish"])
            market_sentiment = "Bullish" if bullish_count > bearish_count else "Bearish" if bearish_count > bullish_count else "Mixed"
        else:
            market_sentiment = "Unknown"
        
        return {
            "success": True,
            "analysis_type": analysis_type,
            "analyzed_assets": assets,
            "results": results,
            "summary": {
                "market_sentiment": market_sentiment,
                "total_assets": len(assets),
                "successful_analyses": len(successful_analyses)
            },
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Multi-asset analysis failed: {str(e)}",
            "assets": assets
        }


def get_trading_signals(symbol: str = "BTCUSDT") -> dict:
    """
    Generate simple trading signals for an asset.
    
    Args:
        symbol: Trading symbol
    
    Returns:
        dict: Trading signals and recommendations
    """
    try:
        market_data = get_market_data_info(symbol)
        
        if not market_data.get("success"):
            return market_data
        
        price_change = market_data["price_change_24h"]
        
        # Simple signal generation logic
        signals = []
        
        if price_change > 3:
            signals.append({
                "type": "MOMENTUM",
                "signal": "BUY",
                "strength": "Strong",
                "reason": "Strong bullish momentum (+3%)"
            })
        elif price_change < -3:
            signals.append({
                "type": "REVERSAL",
                "signal": "BUY",
                "strength": "Moderate",
                "reason": "Potential oversold condition (-3%)"
            })
        elif -1 < price_change < 1:
            signals.append({
                "type": "CONSOLIDATION",
                "signal": "HOLD",
                "strength": "Weak",
                "reason": "Price consolidating, wait for breakout"
            })
        
        # Overall recommendation
        if any(s["signal"] == "BUY" for s in signals):
            overall_recommendation = "BUY"
        else:
            overall_recommendation = "HOLD"
        
        return {
            "success": True,
            "symbol": symbol,
            "current_price": market_data["current_price"],
            "price_change_24h": price_change,
            "overall_recommendation": overall_recommendation,
            "signals": signals,
            "confidence": "Medium",
            "risk_warning": "These are simplified signals for demonstration. Always do thorough analysis before trading.",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Signal generation failed for {symbol}: {str(e)}",
            "symbol": symbol
        }


def get_available_tools() -> dict:
    """
    Get information about available trading tools and capabilities.
    
    Returns:
        dict: Available tools and their descriptions
    """
    return {
        "available_tools": {
            "market_data": {
                "function": "get_market_data_info",
                "description": "Get current market data for any supported cryptocurrency",
                "parameters": ["symbol"],
                "example": "Get market data for BTCUSDT"
            },
            "strategy_analysis": {
                "function": "create_simple_strategy_analysis", 
                "description": "Analyze trading strategies and their potential performance",
                "parameters": ["strategy_type", "symbol", "lookback_days"],
                "example": "Analyze RSI strategy for ETHUSDT"
            },
            "multi_asset_analysis": {
                "function": "analyze_multiple_assets",
                "description": "Compare multiple cryptocurrencies across different metrics",
                "parameters": ["assets", "analysis_type"],
                "example": "Compare trend analysis for BTC, ETH, ADA"
            },
            "trading_signals": {
                "function": "get_trading_signals",
                "description": "Generate trading signals and recommendations",
                "parameters": ["symbol"],
                "example": "Get trading signals for BTCUSDT"
            }
        },
        "supported_strategies": ["sma", "rsi", "momentum"],
        "supported_assets": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"],
        "analysis_types": ["trend", "performance", "risk"],
        "note": "This is a simplified demo version. Full backtesting capabilities available in production mode."
    }


# Create the simplified agents
simplified_backtest_agent = Agent(
    name="simplified_backtest_agent",
    description="Simplified trading strategy analysis and development agent",
    instruction="""You are a trading strategy analyst specializing in cryptocurrency markets.

Your capabilities include:
- Analyzing various trading strategies (SMA, RSI, Momentum)
- Providing strategy recommendations based on market conditions
- Explaining strategy parameters and expected performance
- Offering risk assessments and implementation guidance

When users ask about strategies:
1. Explain the strategy concept clearly
2. Analyze its fit for current market conditions
3. Provide realistic performance expectations
4. Include appropriate risk warnings
5. Suggest next steps for implementation

Always emphasize that this is educational content and users should do their own research before trading.""",
    
    tools=[
        create_simple_strategy_analysis,
        get_market_data_info,
        get_available_tools
    ]
)

simplified_market_agent = Agent(
    name="simplified_market_research_agent", 
    description="Simplified market research and analysis agent for cryptocurrencies",
    instruction="""You are a cryptocurrency market analyst providing research and insights.

Your capabilities include:
- Analyzing market trends across multiple cryptocurrencies
- Generating trading signals based on price action
- Comparing asset performance and risk profiles
- Providing market sentiment analysis

When conducting market analysis:
1. Present data clearly with context
2. Explain what the numbers mean in simple terms
3. Highlight significant trends or patterns
4. Provide balanced perspectives
5. Include appropriate disclaimers about market risks

Always remind users that cryptocurrency markets are highly volatile and past performance doesn't guarantee future results.""",
    
    tools=[
        analyze_multiple_assets,
        get_trading_signals,
        get_market_data_info,
        get_available_tools
    ]
)
