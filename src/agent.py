"""
Root Agent for AI-Agentic-Bots Trading System
=============================================

This is the main entry point for the ADK framework. It exposes the backtest agent
as the root agent for the trading backtesting system.
"""

from .adk_agents.backtest_agent import backtest_agent

# Export the backtest agent as the root agent
root_agent = backtest_agent
