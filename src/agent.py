"""
Root Agent for AI-Agentic-Bots Trading System
=============================================

This is the main entry point for the ADK framework. It exposes the backtest agent
as the root agent for the trading backtesting system.
"""

from google.adk.agents import Agent
from .adk_agents.backtest_agent import backtest_agent
from .adk_agents.market_research_agent import market_research_agent

# Export the backtest agent as the root agent
root_agent = None
__all__ = [
    'root_agent',
    'backtest_agent',
    'market_research_agent'
]


try:
    # Try different model options in case some aren't available
    trading_agent_team = Agent(
        name="trading_agent_team",
        model="gemini-1.5-pro",  # Primary model choice
        description="A team of trading agents for comprehensive market analysis and strategy development. Includes backtesting, market research, and strategy optimization.",
        instruction="""
        You are a team of trading agents working together to analyze the market and develop trading strategies.
        Each agent has a specific role:
        - backtest_agent: Responsible for backtesting trading strategies using historical data.
        - market_research_agent: Conducts market research and provides insights on market trends.
        You will collaborate to provide comprehensive trading solutions.
        Any agent can be called by the user to perform specific tasks.
        You will work together to ensure the best trading strategies are developed and tested.
        Also you will provide the summary of the results and insights from your analysis.
        """,
        sub_agents=[
            backtest_agent,
            market_research_agent
        ]
    )
    print("Root agent initialized successfully with gemini-1.5-pro.")
    root_agent = trading_agent_team
except Exception as e:
    print(f"Warning: Could not create trading team with gemini-1.5-pro: {e}")
    # Fallback to other common models
    try:
        trading_agent_team = Agent(
            name="trading_agent_team",
            model="gpt-4",  # Fallback model
            description="A team of trading agents for comprehensive market analysis and strategy development. Includes backtesting, market research, and strategy optimization.",
            instruction="""
            You are a team of trading agents working together to analyze the market and develop trading strategies.
            Each agent has a specific role:
            - backtest_agent: Responsible for backtesting trading strategies using historical data.
            - market_research_agent: Conducts market research and provides insights on market trends.
            You will collaborate to provide comprehensive trading solutions.
            Any agent can be called by the user to perform specific tasks.
            You will work together to ensure the best trading strategies are developed and tested.
            Also you will provide the summary of the results and insights from your analysis.
            """,
            sub_agents=[
                backtest_agent,
                market_research_agent
            ]
        )
        print("Root agent initialized successfully with gpt-4.")
        root_agent = trading_agent_team
    except Exception as e2:
        print(f"Warning: Could not create trading team with gpt-4: {e2}")
        # Last fallback - create without explicit model (use default)
        try:
            trading_agent_team = Agent(
                name="trading_agent_team",
                description="A team of trading agents for comprehensive market analysis and strategy development. Includes backtesting, market research, and strategy optimization.",
                instruction="""
                You are a team of trading agents working together to analyze the market and develop trading strategies.
                Each agent has a specific role:
                - backtest_agent: Responsible for backtesting trading strategies using historical data.
                - market_research_agent: Conducts market research and provides insights on market trends.
                You will collaborate to provide comprehensive trading solutions.
                Any agent can be called by the user to perform specific tasks.
                You will work together to ensure the best trading strategies are developed and tested.
                Also you will provide the summary of the results and insights from your analysis.
                """,
                sub_agents=[
                    backtest_agent,
                    market_research_agent
                ]
            )
            print("Root agent initialized successfully with default model.")
            root_agent = trading_agent_team
        except Exception as e3:
            print(f"Error initializing root agent: {e3}")
            root_agent = None