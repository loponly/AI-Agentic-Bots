"""
Backtest Strategy Agent
======================

This agent creates trading strategies and runs backtests using the ADK framework.
It can generate custom strategies, configure backtests, and analyze results.
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

from google.adk.agents import Agent

# Import our trading components
try:
    from ..data.providers import DataProvider
    from ..backtesting.engine import BacktestEngine
    from ..strategies.sma import SimpleMovingAverageStrategy
    from ..strategies.rsi import RSIStrategy
    from ..strategies.bollinger import BollingerBandsStrategy
    from ..strategies.momentum import MomentumStrategy
except ImportError:
    # Fallback to absolute imports if relative imports fail
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    from data.providers import DataProvider
    from backtesting.engine import BacktestEngine
    from strategies.sma import SimpleMovingAverageStrategy
    from strategies.rsi import RSIStrategy
    from strategies.bollinger import BollingerBandsStrategy
    from strategies.momentum import MomentumStrategy


def create_strategy_backtest(
    strategy_type: str,
    symbol: str = "BTCUSDT",
    timeframe: str = "1d",
    lookback_days: int = 365,
    initial_cash: float = 100000.0,
    **strategy_params
) -> dict:
    """
    Creates a trading strategy and runs a backtest on it.
    
    Args:
        strategy_type: Type of strategy ('sma', 'rsi', 'bollinger', 'momentum')
        symbol: Trading symbol (e.g., 'BTCUSDT', 'ETHUSDT')
        timeframe: Data timeframe ('1h', '4h', '1d', '1w')
        lookback_days: Number of days of historical data
        initial_cash: Starting cash for backtest
        **strategy_params: Additional strategy-specific parameters
    
    Returns:
        dict: Backtest results including performance metrics
    """
    try:
        print(f"🚀 Creating {strategy_type} strategy for {symbol}...")
        
        # Initialize data provider
        data_provider = DataProvider()
        
        # Load data
        print(f"📊 Loading {lookback_days} days of {symbol} data...")
        data_feed = data_provider.load_binance(
            symbol=symbol,
            interval=timeframe,
            limit=lookback_days
        )
        
        # Strategy mapping
        strategy_map = {
            'sma': SimpleMovingAverageStrategy,
            'rsi': RSIStrategy,
            'bollinger': BollingerBandsStrategy,
            'momentum': MomentumStrategy
        }
        
        if strategy_type.lower() not in strategy_map:
            return {
                "error": f"Unknown strategy type: {strategy_type}",
                "available_strategies": list(strategy_map.keys())
            }
        
        strategy_class = strategy_map[strategy_type.lower()]
        
        # Initialize backtest engine
        engine = BacktestEngine(initial_cash=initial_cash, commission=0.001)
        
        print(f"⚙️ Running backtest with {strategy_class.__name__}...")
        
        # Run backtest
        results = engine.run_backtest(
            strategy_class=strategy_class,
            data_feed=data_feed,
            strategy_params=strategy_params
        )
        
        # Format results
        final_value = results['final_portfolio_value']
        total_return = ((final_value - initial_cash) / initial_cash) * 100
        
        # Calculate buy and hold return for comparison
        first_price = data_feed.data.iloc[0]['close']
        last_price = data_feed.data.iloc[-1]['close']
        buy_hold_return = ((last_price - first_price) / first_price) * 100
        
        return {
            "success": True,
            "strategy": strategy_type,
            "symbol": symbol,
            "timeframe": timeframe,
            "data_points": len(data_feed.data),
            "initial_cash": initial_cash,
            "final_value": final_value,
            "total_return_pct": round(total_return, 2),
            "buy_hold_return_pct": round(buy_hold_return, 2),
            "alpha": round(total_return - buy_hold_return, 2),
            "total_trades": results.get('total_trades', 0),
            "win_rate": results.get('win_rate', 0),
            "max_drawdown": results.get('max_drawdown', 0),
            "sharpe_ratio": results.get('sharpe_ratio', 0),
            "strategy_params": strategy_params,
            "backtest_period": f"{data_feed.data.iloc[0]['date']} to {data_feed.data.iloc[-1]['date']}"
        }
        
    except Exception as e:
        return {
            "error": f"Backtest failed: {str(e)}",
            "strategy": strategy_type,
            "symbol": symbol
        }


def compare_strategies(
    strategies: List[str],
    symbol: str = "BTCUSDT",
    timeframe: str = "1d",
    lookback_days: int = 365
) -> dict:
    """
    Compare multiple trading strategies on the same dataset.
    
    Args:
        strategies: List of strategy types to compare
        symbol: Trading symbol
        timeframe: Data timeframe
        lookback_days: Number of days of historical data
    
    Returns:
        dict: Comparison results for all strategies
    """
    try:
        print(f"📊 Comparing {len(strategies)} strategies on {symbol}...")
        
        results = {}
        
        for strategy in strategies:
            result = create_strategy_backtest(
                strategy_type=strategy,
                symbol=symbol,
                timeframe=timeframe,
                lookback_days=lookback_days
            )
            results[strategy] = result
        
        # Find best performing strategy
        best_strategy = None
        best_return = float('-inf')
        
        for strategy, result in results.items():
            if result.get('success') and result.get('total_return_pct', float('-inf')) > best_return:
                best_return = result['total_return_pct']
                best_strategy = strategy
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "comparison_results": results,
            "best_strategy": best_strategy,
            "best_return": best_return,
            "comparison_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Strategy comparison failed: {str(e)}",
            "symbol": symbol,
            "strategies": strategies
        }


def optimize_strategy_parameters(
    strategy_type: str,
    symbol: str = "BTCUSDT",
    param_ranges: Optional[Dict[str, List]] = None
) -> dict:
    """
    Optimize strategy parameters using grid search.
    
    Args:
        strategy_type: Type of strategy to optimize
        symbol: Trading symbol
        param_ranges: Dictionary of parameter ranges to test
    
    Returns:
        dict: Optimization results with best parameters
    """
    try:
        print(f"🔧 Optimizing {strategy_type} strategy parameters...")
        
        # Default parameter ranges for different strategies
        default_ranges = {
            'sma': {
                'short_period': [5, 10, 15, 20],
                'long_period': [30, 50, 100, 200]
            },
            'rsi': {
                'period': [10, 14, 21, 28],
                'oversold': [20, 25, 30],
                'overbought': [70, 75, 80]
            },
            'bollinger': {
                'period': [10, 20, 30],
                'std_dev': [1.5, 2.0, 2.5]
            }
        }
        
        param_ranges = param_ranges or default_ranges.get(strategy_type.lower(), {})
        
        if not param_ranges:
            return {
                "error": f"No parameter ranges defined for {strategy_type}",
                "strategy": strategy_type
            }
        
        best_result = None
        best_return = float('-inf')
        best_params = None
        
        # Generate all parameter combinations
        import itertools
        
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        total_combinations = 1
        for values in param_values:
            total_combinations *= len(values)
        
        print(f"🔍 Testing {total_combinations} parameter combinations...")
        
        for i, combination in enumerate(itertools.product(*param_values)):
            params = dict(zip(param_names, combination))
            
            # Skip invalid combinations (e.g., short_period >= long_period for SMA)
            if strategy_type.lower() == 'sma' and params.get('short_period', 0) >= params.get('long_period', 1):
                continue
            
            result = create_strategy_backtest(
                strategy_type=strategy_type,
                symbol=symbol,
                **params
            )
            
            if result.get('success') and result.get('total_return_pct', float('-inf')) > best_return:
                best_return = result['total_return_pct']
                best_result = result
                best_params = params
            
            if (i + 1) % 10 == 0:
                print(f"  Tested {i + 1}/{total_combinations} combinations...")
        
        return {
            "success": True,
            "strategy": strategy_type,
            "symbol": symbol,
            "best_parameters": best_params,
            "best_return": best_return,
            "best_result": best_result,
            "total_combinations_tested": total_combinations,
            "optimization_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Parameter optimization failed: {str(e)}",
            "strategy": strategy_type,
            "symbol": symbol
        }


def get_available_strategies() -> dict:
    """
    Get list of available trading strategies.
    
    Returns:
        dict: Available strategies and their descriptions
    """
    return {
        "available_strategies": {
            "sma": {
                "name": "Simple Moving Average Crossover",
                "description": "Uses short and long period moving averages to generate signals",
                "parameters": ["short_period", "long_period"]
            },
            "rsi": {
                "name": "Relative Strength Index",
                "description": "Uses RSI indicator to identify overbought/oversold conditions",
                "parameters": ["period", "oversold", "overbought"]
            },
            "bollinger": {
                "name": "Bollinger Bands",
                "description": "Uses price bands to identify potential reversal points",
                "parameters": ["period", "std_dev"]
            },
            "momentum": {
                "name": "Momentum Strategy",
                "description": "Uses price momentum and volume to generate signals",
                "parameters": ["lookback_period", "volume_threshold"]
            }
        },
        "supported_symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"],
        "supported_timeframes": ["1h", "4h", "1d", "1w"]
    }


# Create the ADK agent
# Try different model options in case some aren't available
try:
    backtest_agent = Agent(
        name="backtest_strategy_agent",
        model="gemini-1.5-pro",  # Primary model choice
        description="Creates and backtests trading strategies with comprehensive analysis and optimization capabilities",
        instruction="""You are a professional algorithmic trading strategy developer and backtesting expert. 

Your role is to:
1. Create and configure various trading strategies (SMA, RSI, Bollinger Bands, Momentum)
2. Run comprehensive backtests with historical data
3. Analyze performance metrics and provide insights
4. Compare multiple strategies to find the best performing ones
5. Optimize strategy parameters for maximum performance
6. Provide detailed reports with actionable recommendations

When a user requests strategy creation or backtesting:
- Always ask for clarification on strategy type, symbol, and timeframe if not specified
- Provide clear explanations of the strategy logic and parameters
- Include performance metrics like total return, Sharpe ratio, win rate, and maximum drawdown
- Compare strategy performance against buy-and-hold baseline
- Suggest parameter optimizations when appropriate
- Explain the risks and limitations of backtesting

Be thorough, analytical, and always consider real-world trading constraints.""",
        
        tools=[
            create_strategy_backtest,
            compare_strategies,
            optimize_strategy_parameters,
            get_available_strategies
        ]
    )
except Exception as e:
    print(f"Warning: Could not create agent with gemini-1.5-pro: {e}")
    # Fallback to other common models
    try:
        backtest_agent = Agent(
            name="backtest_strategy_agent",
            model="gpt-4",  # Fallback model
            description="Creates and backtests trading strategies with comprehensive analysis and optimization capabilities",
            instruction="""You are a professional algorithmic trading strategy developer and backtesting expert. 

Your role is to:
1. Create and configure various trading strategies (SMA, RSI, Bollinger Bands, Momentum)
2. Run comprehensive backtests with historical data
3. Analyze performance metrics and provide insights
4. Compare multiple strategies to find the best performing ones
5. Optimize strategy parameters for maximum performance
6. Provide detailed reports with actionable recommendations

When a user requests strategy creation or backtesting:
- Always ask for clarification on strategy type, symbol, and timeframe if not specified
- Provide clear explanations of the strategy logic and parameters
- Include performance metrics like total return, Sharpe ratio, win rate, and maximum drawdown
- Compare strategy performance against buy-and-hold baseline
- Suggest parameter optimizations when appropriate
- Explain the risks and limitations of backtesting

Be thorough, analytical, and always consider real-world trading constraints.""",
            
            tools=[
                create_strategy_backtest,
                compare_strategies,
                optimize_strategy_parameters,
                get_available_strategies
            ]
        )
    except Exception as e2:
        print(f"Warning: Could not create agent with gpt-4: {e2}")
        # Last fallback - create without explicit model (use default)
        backtest_agent = Agent(
            name="backtest_strategy_agent",
            description="Creates and backtests trading strategies with comprehensive analysis and optimization capabilities",
            instruction="""You are a professional algorithmic trading strategy developer and backtesting expert. 

Your role is to:
1. Create and configure various trading strategies (SMA, RSI, Bollinger Bands, Momentum)
2. Run comprehensive backtests with historical data
3. Analyze performance metrics and provide insights
4. Compare multiple strategies to find the best performing ones
5. Optimize strategy parameters for maximum performance
6. Provide detailed reports with actionable recommendations

When a user requests strategy creation or backtesting:
- Always ask for clarification on strategy type, symbol, and timeframe if not specified
- Provide clear explanations of the strategy logic and parameters
- Include performance metrics like total return, Sharpe ratio, win rate, and maximum drawdown
- Compare strategy performance against buy-and-hold baseline
- Suggest parameter optimizations when appropriate
- Explain the risks and limitations of backtesting

Be thorough, analytical, and always consider real-world trading constraints.""",
            
            tools=[
                create_strategy_backtest,
                compare_strategies,
                optimize_strategy_parameters,
                get_available_strategies
            ]
        )
