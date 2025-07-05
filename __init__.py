"""
AI Agentic Trading Bots
=======================

A multi-agent trading system built with ADK (Agent Development Kit) that provides:
- Strategy development and backtesting capabilities
- Comprehensive market research and analysis
- Technical indicator analysis and signal generation
- Performance optimization and comparison tools
"""

# Import core components
try:
    # Try absolute import first
    import agent
except ImportError:
    # If that fails, try to import without any path modifications
    # This allows the module to work both as a package and standalone
    pass

__version__ = "1.0.0"
__author__ = "AI Trading System"
__description__ = "Multi-agent trading system with ADK"
