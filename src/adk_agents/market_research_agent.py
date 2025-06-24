"""
Market Research & Analysis Agent
===============================

This agent performs comprehensive market research and analysis using the ADK framework.
It can analyze market trends, perform technical analysis, and provide market insights.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

from google.adk.agents import Agent

# Import our trading components
try:
    from data.providers import DataProvider
except ImportError:
    # Fallback to relative imports if absolute imports fail
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    from data.providers import DataProvider


def analyze_market_trends(
    symbols: Optional[List[str]] = None,
    timeframe: str = "1d",
    lookback_days: int = 30
) -> dict:
    """
    Analyze market trends for multiple cryptocurrencies.
    
    Args:
        symbols: List of trading symbols to analyze
        timeframe: Data timeframe ('1h', '4h', '1d', '1w')
        lookback_days: Number of days to analyze
    
    Returns:
        dict: Market trend analysis results
    """
    try:
        symbols = symbols or ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"]
        
        print(f"📈 Analyzing market trends for {len(symbols)} assets...")
        
        data_provider = DataProvider()
        analysis_results = {}
        
        for symbol in symbols:
            try:
                # Get market data
                feed = data_provider.load_binance(
                    symbol=symbol,
                    interval=timeframe,
                    limit=lookback_days
                )
                
                data = feed.data
                
                # Calculate trend indicators
                current_price = data.iloc[-1]['close']
                price_change_1d = ((current_price - data.iloc[-2]['close']) / data.iloc[-2]['close']) * 100
                price_change_7d = ((current_price - data.iloc[-8]['close']) / data.iloc[-8]['close']) * 100 if len(data) >= 8 else 0
                price_change_30d = ((current_price - data.iloc[0]['close']) / data.iloc[0]['close']) * 100
                
                # Moving averages
                data['sma_10'] = data['close'].rolling(window=10).mean()
                data['sma_20'] = data['close'].rolling(window=20).mean()
                data['ema_12'] = data['close'].ewm(span=12).mean()
                data['ema_26'] = data['close'].ewm(span=26).mean()
                
                # RSI
                delta = data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                data['rsi'] = 100 - (100 / (1 + rs))
                
                # MACD
                data['macd'] = data['ema_12'] - data['ema_26']
                data['macd_signal'] = data['macd'].ewm(span=9).mean()
                data['macd_histogram'] = data['macd'] - data['macd_signal']
                
                # Volume analysis
                avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
                current_volume = data.iloc[-1]['volume']
                volume_ratio = current_volume / avg_volume
                
                # Volatility (20-day)
                data['returns'] = data['close'].pct_change()
                volatility = data['returns'].rolling(window=20).std() * np.sqrt(365) * 100  # Annualized
                
                # Support and resistance levels
                high_20 = data['high'].rolling(window=20).max().iloc[-1]
                low_20 = data['low'].rolling(window=20).min().iloc[-1]
                
                # Trend determination
                latest = data.iloc[-1]
                trend = "NEUTRAL"
                
                if (latest['close'] > latest['sma_10'] > latest['sma_20'] and 
                    latest['macd'] > latest['macd_signal'] and 
                    latest['rsi'] > 50):
                    trend = "BULLISH"
                elif (latest['close'] < latest['sma_10'] < latest['sma_20'] and 
                      latest['macd'] < latest['macd_signal'] and 
                      latest['rsi'] < 50):
                    trend = "BEARISH"
                
                analysis_results[symbol] = {
                    "current_price": round(current_price, 2),
                    "price_changes": {
                        "1d": round(price_change_1d, 2),
                        "7d": round(price_change_7d, 2),
                        "30d": round(price_change_30d, 2)
                    },
                    "trend": trend,
                    "technical_indicators": {
                        "rsi": round(latest['rsi'], 2),
                        "macd": round(latest['macd'], 4),
                        "macd_signal": round(latest['macd_signal'], 4),
                        "sma_10": round(latest['sma_10'], 2),
                        "sma_20": round(latest['sma_20'], 2)
                    },
                    "volume_analysis": {
                        "current_volume": int(current_volume),
                        "avg_volume_20d": int(avg_volume),
                        "volume_ratio": round(volume_ratio, 2),
                        "volume_surge": volume_ratio > 1.5
                    },
                    "volatility_20d": round(volatility.iloc[-1], 2),
                    "support_resistance": {
                        "resistance_20d": round(high_20, 2),
                        "support_20d": round(low_20, 2)
                    }
                }
                
            except Exception as e:
                analysis_results[symbol] = {"error": f"Analysis failed: {str(e)}"}
        
        # Market overview
        successful_analyses = [r for r in analysis_results.values() if "error" not in r]
        
        if successful_analyses:
            bullish_count = len([r for r in successful_analyses if r["trend"] == "BULLISH"])
            bearish_count = len([r for r in successful_analyses if r["trend"] == "BEARISH"])
            neutral_count = len([r for r in successful_analyses if r["trend"] == "NEUTRAL"])
            
            avg_30d_change = np.mean([r["price_changes"]["30d"] for r in successful_analyses])
            
            market_sentiment = "BULLISH" if bullish_count > bearish_count else "BEARISH" if bearish_count > bullish_count else "MIXED"
        else:
            bullish_count = bearish_count = neutral_count = 0
            avg_30d_change = 0
            market_sentiment = "UNKNOWN"
        
        return {
            "success": True,
            "analysis_date": datetime.now().isoformat(),
            "timeframe": timeframe,
            "lookback_days": lookback_days,
            "market_overview": {
                "sentiment": market_sentiment,
                "bullish_assets": bullish_count,
                "bearish_assets": bearish_count,
                "neutral_assets": neutral_count,
                "avg_30d_performance": round(avg_30d_change, 2)
            },
            "asset_analysis": analysis_results
        }
        
    except Exception as e:
        return {
            "error": f"Market trend analysis failed: {str(e)}",
            "symbols": symbols
        }


def perform_technical_analysis(
    symbol: str = "BTCUSDT",
    timeframe: str = "1d",
    lookback_days: int = 100
) -> dict:
    """
    Perform comprehensive technical analysis on a single asset.
    
    Args:
        symbol: Trading symbol to analyze
        timeframe: Data timeframe
        lookback_days: Number of days for analysis
    
    Returns:
        dict: Detailed technical analysis results
    """
    try:
        print(f"🔍 Performing technical analysis on {symbol}...")
        
        data_provider = DataProvider()
        feed = data_provider.load_binance(
            symbol=symbol,
            interval=timeframe,
            limit=lookback_days
        )
        
        data = feed.data.copy()
        
        # Calculate comprehensive technical indicators
        
        # Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            if len(data) >= period:
                data[f'sma_{period}'] = data['close'].rolling(window=period).mean()
                data[f'ema_{period}'] = data['close'].ewm(span=period).mean()
        
        # RSI (14-period)
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        data['ema_12'] = data['close'].ewm(span=12).mean()
        data['ema_26'] = data['close'].ewm(span=26).mean()
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # Bollinger Bands
        data['bb_middle'] = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        data['bb_width'] = data['bb_upper'] - data['bb_lower']
        data['bb_position'] = (data['close'] - data['bb_lower']) / data['bb_width']
        
        # Stochastic Oscillator
        low_14 = data['low'].rolling(window=14).min()
        high_14 = data['high'].rolling(window=14).max()
        data['stoch_k'] = 100 * ((data['close'] - low_14) / (high_14 - low_14))
        data['stoch_d'] = data['stoch_k'].rolling(window=3).mean()
        
        # Average True Range (ATR)
        data['tr1'] = data['high'] - data['low']
        data['tr2'] = abs(data['high'] - data['close'].shift(1))
        data['tr3'] = abs(data['low'] - data['close'].shift(1))
        data['true_range'] = data[['tr1', 'tr2', 'tr3']].max(axis=1)
        data['atr'] = data['true_range'].rolling(window=14).mean()
        
        # Volume indicators
        data['volume_sma'] = data['volume'].rolling(window=20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        # On-Balance Volume (OBV)
        data['obv'] = (np.sign(data['close'].diff()) * data['volume']).fillna(0).cumsum()
        
        # Current values
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Pattern recognition
        patterns = detect_chart_patterns(data)
        
        # Support and resistance levels
        support_resistance = find_support_resistance_levels(data)
        
        # Generate signals
        signals = generate_technical_signals(data)
        
        return {
            "success": True,
            "symbol": symbol,
            "analysis_date": datetime.now().isoformat(),
            "current_price": round(latest['close'], 2),
            "price_action": {
                "daily_change": round(((latest['close'] - previous['close']) / previous['close']) * 100, 2),
                "high_24h": round(latest['high'], 2),
                "low_24h": round(latest['low'], 2),
                "volume_24h": int(latest['volume'])
            },
            "technical_indicators": {
                "trend": {
                    "sma_10": round(latest['sma_10'], 2) if 'sma_10' in latest and pd.notna(latest['sma_10']) else None,
                    "sma_20": round(latest['sma_20'], 2) if 'sma_20' in latest and pd.notna(latest['sma_20']) else None,
                    "sma_50": round(latest['sma_50'], 2) if 'sma_50' in latest and pd.notna(latest['sma_50']) else None,
                    "ema_10": round(latest['ema_10'], 2) if 'ema_10' in latest and pd.notna(latest['ema_10']) else None,
                    "ema_20": round(latest['ema_20'], 2) if 'ema_20' in latest and pd.notna(latest['ema_20']) else None
                },
                "momentum": {
                    "rsi": round(latest['rsi'], 2) if pd.notna(latest['rsi']) else None,
                    "macd": round(latest['macd'], 4) if pd.notna(latest['macd']) else None,
                    "macd_signal": round(latest['macd_signal'], 4) if pd.notna(latest['macd_signal']) else None,
                    "stoch_k": round(latest['stoch_k'], 2) if pd.notna(latest['stoch_k']) else None,
                    "stoch_d": round(latest['stoch_d'], 2) if pd.notna(latest['stoch_d']) else None
                },
                "volatility": {
                    "bb_upper": round(latest['bb_upper'], 2) if pd.notna(latest['bb_upper']) else None,
                    "bb_middle": round(latest['bb_middle'], 2) if pd.notna(latest['bb_middle']) else None,
                    "bb_lower": round(latest['bb_lower'], 2) if pd.notna(latest['bb_lower']) else None,
                    "bb_position": round(latest['bb_position'], 2) if pd.notna(latest['bb_position']) else None,
                    "atr": round(latest['atr'], 4) if pd.notna(latest['atr']) else None
                },
                "volume": {
                    "volume_ratio": round(latest['volume_ratio'], 2) if pd.notna(latest['volume_ratio']) else None,
                    "obv": int(latest['obv']) if pd.notna(latest['obv']) else None
                }
            },
            "chart_patterns": patterns,
            "support_resistance": support_resistance,
            "signals": signals,
            "data_points": len(data)
        }
        
    except Exception as e:
        return {
            "error": f"Technical analysis failed: {str(e)}",
            "symbol": symbol
        }


def detect_chart_patterns(data: pd.DataFrame) -> dict:
    """Detect common chart patterns."""
    patterns = {
        "doji": False,
        "hammer": False,
        "shooting_star": False,
        "engulfing_bullish": False,
        "engulfing_bearish": False
    }
    
    if len(data) < 2:
        return patterns
    
    latest = data.iloc[-1]
    previous = data.iloc[-2]
    
    # Doji pattern
    body_size = abs(latest['close'] - latest['open'])
    candle_range = latest['high'] - latest['low']
    if candle_range > 0 and body_size / candle_range < 0.1:
        patterns["doji"] = True
    
    # Hammer pattern
    lower_shadow = latest['open'] - latest['low'] if latest['close'] > latest['open'] else latest['close'] - latest['low']
    upper_shadow = latest['high'] - latest['close'] if latest['close'] > latest['open'] else latest['high'] - latest['open']
    if candle_range > 0 and lower_shadow > 2 * body_size and upper_shadow < body_size:
        patterns["hammer"] = True
    
    # Shooting star pattern
    if candle_range > 0 and upper_shadow > 2 * body_size and lower_shadow < body_size:
        patterns["shooting_star"] = True
    
    # Engulfing patterns
    prev_body = abs(previous['close'] - previous['open'])
    curr_body = abs(latest['close'] - latest['open'])
    
    if (previous['close'] < previous['open'] and latest['close'] > latest['open'] and
        latest['open'] < previous['close'] and latest['close'] > previous['open']):
        patterns["engulfing_bullish"] = True
    
    if (previous['close'] > previous['open'] and latest['close'] < latest['open'] and
        latest['open'] > previous['close'] and latest['close'] < previous['open']):
        patterns["engulfing_bearish"] = True
    
    return patterns


def find_support_resistance_levels(data: pd.DataFrame, lookback: int = 20) -> dict:
    """Find key support and resistance levels."""
    if len(data) < lookback:
        return {"support_levels": [], "resistance_levels": []}
    
    # Find local maxima and minima
    highs = data['high'].rolling(window=lookback).max()
    lows = data['low'].rolling(window=lookback).min()
    
    # Get recent levels
    recent_data = data.tail(lookback)
    resistance_levels = recent_data['high'].nlargest(3).tolist()
    support_levels = recent_data['low'].nsmallest(3).tolist()
    
    return {
        "support_levels": [round(level, 2) for level in support_levels],
        "resistance_levels": [round(level, 2) for level in resistance_levels],
        "current_support": round(lows.iloc[-1], 2) if pd.notna(lows.iloc[-1]) else None,
        "current_resistance": round(highs.iloc[-1], 2) if pd.notna(highs.iloc[-1]) else None
    }


def generate_technical_signals(data: pd.DataFrame) -> dict:
    """Generate trading signals based on technical indicators."""
    if len(data) < 2:
        return {"overall_signal": "HOLD", "signals": []}
    
    latest = data.iloc[-1]
    previous = data.iloc[-2]
    signals = []
    
    # RSI signals
    if pd.notna(latest['rsi']):
        if latest['rsi'] < 30:
            signals.append({"indicator": "RSI", "signal": "BUY", "reason": "Oversold condition"})
        elif latest['rsi'] > 70:
            signals.append({"indicator": "RSI", "signal": "SELL", "reason": "Overbought condition"})
    
    # MACD signals
    if pd.notna(latest['macd']) and pd.notna(previous['macd']):
        if (latest['macd'] > latest['macd_signal'] and 
            previous['macd'] <= previous['macd_signal']):
            signals.append({"indicator": "MACD", "signal": "BUY", "reason": "Bullish crossover"})
        elif (latest['macd'] < latest['macd_signal'] and 
              previous['macd'] >= previous['macd_signal']):
            signals.append({"indicator": "MACD", "signal": "SELL", "reason": "Bearish crossover"})
    
    # Moving average signals
    if (pd.notna(latest['sma_10']) and pd.notna(latest['sma_20'])):
        if (latest['sma_10'] > latest['sma_20'] and 
            previous['sma_10'] <= previous['sma_20']):
            signals.append({"indicator": "SMA", "signal": "BUY", "reason": "Golden cross"})
        elif (latest['sma_10'] < latest['sma_20'] and 
              previous['sma_10'] >= previous['sma_20']):
            signals.append({"indicator": "SMA", "signal": "SELL", "reason": "Death cross"})
    
    # Bollinger Bands signals
    if pd.notna(latest['bb_position']):
        if latest['bb_position'] < 0.1:
            signals.append({"indicator": "Bollinger", "signal": "BUY", "reason": "Near lower band"})
        elif latest['bb_position'] > 0.9:
            signals.append({"indicator": "Bollinger", "signal": "SELL", "reason": "Near upper band"})
    
    # Determine overall signal
    buy_signals = len([s for s in signals if s["signal"] == "BUY"])
    sell_signals = len([s for s in signals if s["signal"] == "SELL"])
    
    if buy_signals > sell_signals:
        overall_signal = "BUY"
    elif sell_signals > buy_signals:
        overall_signal = "SELL"
    else:
        overall_signal = "HOLD"
    
    return {
        "overall_signal": overall_signal,
        "signal_strength": max(buy_signals, sell_signals),
        "total_signals": len(signals),
        "signals": signals
    }


def compare_market_performance(
    symbols: Optional[List[str]] = None,
    timeframe: str = "1d",
    comparison_periods: Optional[List[int]] = None
) -> dict:
    """
    Compare performance of multiple assets across different time periods.
    
    Args:
        symbols: List of symbols to compare
        timeframe: Data timeframe
        comparison_periods: List of days to compare (e.g., [7, 30, 90])
    
    Returns:
        dict: Performance comparison results
    """
    try:
        symbols = symbols or ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"]
        comparison_periods = comparison_periods or [1, 7, 30, 90]
        
        print(f"📊 Comparing performance of {len(symbols)} assets...")
        
        data_provider = DataProvider()
        performance_data = {}
        
        max_period = max(comparison_periods)
        
        for symbol in symbols:
            try:
                feed = data_provider.load_binance(
                    symbol=symbol,
                    interval=timeframe,
                    limit=max_period + 5  # Buffer for calculations
                )
                
                data = feed.data
                current_price = data.iloc[-1]['close']
                
                performance = {"current_price": round(current_price, 2)}
                
                for period in comparison_periods:
                    if len(data) > period:
                        past_price = data.iloc[-(period + 1)]['close']
                        change_pct = ((current_price - past_price) / past_price) * 100
                        performance[f"{period}d_change"] = round(change_pct, 2)
                    else:
                        performance[f"{period}d_change"] = None
                
                # Calculate volatility
                returns = data['close'].pct_change().dropna()
                if len(returns) > 10:
                    volatility = returns.std() * np.sqrt(365) * 100  # Annualized
                    performance["volatility"] = round(volatility, 2)
                else:
                    performance["volatility"] = None
                
                performance_data[symbol] = performance
                
            except Exception as e:
                performance_data[symbol] = {"error": f"Failed to analyze {symbol}: {str(e)}"}
        
        # Rank assets by performance
        rankings = {}
        for period in comparison_periods:
            period_key = f"{period}d_change"
            valid_data = {
                symbol: data[period_key] 
                for symbol, data in performance_data.items() 
                if period_key in data and data[period_key] is not None
            }
            
            if valid_data:
                sorted_assets = sorted(valid_data.items(), key=lambda x: x[1], reverse=True)
                rankings[f"{period}d_ranking"] = [
                    {"symbol": symbol, "change_pct": change}
                    for symbol, change in sorted_assets
                ]
        
        return {
            "success": True,
            "comparison_date": datetime.now().isoformat(),
            "timeframe": timeframe,
            "comparison_periods": comparison_periods,
            "performance_data": performance_data,
            "rankings": rankings
        }
        
    except Exception as e:
        return {
            "error": f"Performance comparison failed: {str(e)}",
            "symbols": symbols
        }

# @title Market Sentiment Analysis
# @markdown This function analyzes the overall market sentiment using various indicators.
def get_market_sentiment() -> dict:
    """
    Analyze overall market sentiment using various indicators.
    
    Returns:
        dict: Market sentiment analysis
    """
    try:
        print("🌡️ Analyzing market sentiment...")
        
        # Major crypto symbols for sentiment analysis
        major_cryptos = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
        
        data_provider = DataProvider()
        sentiment_data = {}
        
        for symbol in major_cryptos:
            try:
                feed = data_provider.load_binance(symbol=symbol, interval="1d", limit=30)
                data = feed.data
                
                # Calculate sentiment indicators
                recent_returns = data['close'].pct_change().tail(7)
                positive_days = (recent_returns > 0).sum()
                negative_days = (recent_returns < 0).sum()
                
                # Volume trend
                volume_trend = data['volume'].tail(7).mean() / data['volume'].head(7).mean()
                
                sentiment_data[symbol] = {
                    "positive_days_7d": int(positive_days),
                    "negative_days_7d": int(negative_days),
                    "volume_trend": round(volume_trend, 2),
                    "price_momentum": round(recent_returns.mean() * 100, 2)
                }
                
            except Exception as e:
                sentiment_data[symbol] = {"error": str(e)}
        
        # Calculate overall sentiment
        valid_data = [data for data in sentiment_data.values() if "error" not in data]
        
        if valid_data:
            avg_positive_days = np.mean([data["positive_days_7d"] for data in valid_data])
            avg_momentum = np.mean([data["price_momentum"] for data in valid_data])
            avg_volume_trend = np.mean([data["volume_trend"] for data in valid_data])
            
            # Determine sentiment
            if avg_positive_days >= 4 and avg_momentum > 1:
                overall_sentiment = "BULLISH"
            elif avg_positive_days <= 3 and avg_momentum < -1:
                overall_sentiment = "BEARISH"
            else:
                overall_sentiment = "NEUTRAL"
                
            sentiment_score = round((avg_positive_days / 7) * 100, 1)
        else:
            overall_sentiment = "UNKNOWN"
            sentiment_score = 50
            avg_momentum = 0
            avg_volume_trend = 1
        
        return {
            "success": True,
            "analysis_date": datetime.now().isoformat(),
            "overall_sentiment": overall_sentiment,
            "sentiment_score": sentiment_score,
            "market_indicators": {
                "avg_positive_days_7d": round(avg_positive_days, 1) if valid_data else 0,
                "avg_price_momentum": round(avg_momentum, 2),
                "avg_volume_trend": round(avg_volume_trend, 2)
            },
            "asset_sentiment": sentiment_data
        }
        
    except Exception as e:
        return {
            "error": f"Sentiment analysis failed: {str(e)}"
        }


# Create the ADK agent
# Try different model options in case some aren't available
try:
    market_research_agent = Agent(
        name="market_research_agent",
        model="gemini-1.5-pro",  # Primary model choice
        description="Comprehensive market research and technical analysis agent for cryptocurrency markets",
        instruction="""You are a professional cryptocurrency market analyst and researcher.

Your role is to:
1. Analyze market trends across multiple cryptocurrencies
2. Perform detailed technical analysis using various indicators
3. Identify chart patterns and support/resistance levels
4. Compare asset performance across different timeframes
5. Assess market sentiment and provide insights
6. Generate trading signals based on technical analysis
7. Provide comprehensive market reports with actionable insights

When conducting market research:
- Always provide context for your analysis (timeframe, data period)
- Explain technical indicators in simple terms
- Highlight significant patterns or anomalies
- Compare current conditions to historical norms
- Consider multiple timeframes for comprehensive analysis
- Explain the limitations and risks of technical analysis
- Provide balanced views considering both bullish and bearish scenarios

Be thorough, objective, and always emphasize that past performance doesn't guarantee future results.""",
        
        tools=[
            analyze_market_trends,
            perform_technical_analysis,
            compare_market_performance,
            get_market_sentiment
        ]
    )
except Exception as e:
    print(f"Warning: Could not create market research agent with gemini-1.5-pro: {e}")
    # Fallback to other common models
    try:
        market_research_agent = Agent(
            name="market_research_agent",
            model="gpt-4",  # Fallback model
            description="Comprehensive market research and technical analysis agent for cryptocurrency markets",
            instruction="""You are a professional cryptocurrency market analyst and researcher.

Your role is to:
1. Analyze market trends across multiple cryptocurrencies
2. Perform detailed technical analysis using various indicators
3. Identify chart patterns and support/resistance levels
4. Compare asset performance across different timeframes
5. Assess market sentiment and provide insights
6. Generate trading signals based on technical analysis
7. Provide comprehensive market reports with actionable insights

When conducting market research:
- Always provide context for your analysis (timeframe, data period)
- Explain technical indicators in simple terms
- Highlight significant patterns or anomalies
- Compare current conditions to historical norms
- Consider multiple timeframes for comprehensive analysis
- Explain the limitations and risks of technical analysis
- Provide balanced views considering both bullish and bearish scenarios

Be thorough, objective, and always emphasize that past performance doesn't guarantee future results.""",
            
            tools=[
                analyze_market_trends,
                perform_technical_analysis,
                compare_market_performance,
                get_market_sentiment
            ]
        )
    except Exception as e2:
        print(f"Warning: Could not create market research agent with gpt-4: {e2}")
        # Last fallback - create without explicit model (use default)
        market_research_agent = Agent(
            name="market_research_agent",
            description="Comprehensive market research and technical analysis agent for cryptocurrency markets",
            instruction="""You are a professional cryptocurrency market analyst and researcher.

Your role is to:
1. Analyze market trends across multiple cryptocurrencies
2. Perform detailed technical analysis using various indicators
3. Identify chart patterns and support/resistance levels
4. Compare asset performance across different timeframes
5. Assess market sentiment and provide insights
6. Generate trading signals based on technical analysis
7. Provide comprehensive market reports with actionable insights

When conducting market research:
- Always provide context for your analysis (timeframe, data period)
- Explain technical indicators in simple terms
- Highlight significant patterns or anomalies
- Compare current conditions to historical norms
- Consider multiple timeframes for comprehensive analysis
- Explain the limitations and risks of technical analysis
- Provide balanced views considering both bullish and bearish scenarios

Be thorough, objective, and always emphasize that past performance doesn't guarantee future results.""",
            
            tools=[
                analyze_market_trends,
                perform_technical_analysis,
                compare_market_performance,
                get_market_sentiment
            ]
        )
