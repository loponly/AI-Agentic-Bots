"""
AI-Agentic-Bots Trading Backtesting System
==========================================

A comprehensive Python package for trading strategy backtesting using backtrader.
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .backtesting import BacktestEngine, print_performance_summary
from .data import DataProvider
from .strategies import (
    SimpleMovingAverageStrategy,
    RSIStrategy,
    BollingerBandsStrategy,
    BuyAndHoldStrategy,
    MeanReversionStrategy,
    MomentumStrategy
)
from .database import DatabaseManager
from .analyzers import PerformanceAnalyzer, TradeAnalyzer

# Conditional import for agents (requires google-adk)
try:
    from .agents import TradingAgent, TradingAgentStrategy
    _agents_available = True
except ImportError:
    _agents_available = False
    TradingAgent = None
    TradingAgentStrategy = None

__all__ = [
    'BacktestEngine',
    'print_performance_summary',
    'DataProvider',
    'DatabaseManager',
    'PerformanceAnalyzer',
    'TradeAnalyzer',
    'SimpleMovingAverageStrategy',
    'RSIStrategy',
    'BollingerBandsStrategy',
    'BuyAndHoldStrategy',
    'MeanReversionStrategy',
    'MomentumStrategy'
]

# Add agents to __all__ if available
if _agents_available:
    __all__.extend(['TradingAgent', 'TradingAgentStrategy'])
