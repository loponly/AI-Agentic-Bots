"""
Trading Agent Implementation
===========================

This module implements an agent class that combines the BaseStrategy with ADK agent 
capabilities for intelligent trading strategy execution and analysis.
"""

import os
import asyncio
from typing import Dict, Any, Optional, Type, List, Union
from datetime import datetime, date
import json
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load .env from current directory and parent directories
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # Load from current working directory
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from ..strategies.base import BaseStrategy
from ..data.providers import DataProvider, DataFeed
from ..backtesting.engine import BacktestEngine


class TradingAgentStrategy(BaseStrategy):
    """
    A strategy class that can be controlled by an ADK agent.
    Inherits from BaseStrategy and adds agent-driven decision making.
    """
    
    params = (
        ('agent_enabled', True),
        ('risk_tolerance', 0.02),  # 2% risk per trade
        ('max_position_size', 0.1),  # 10% of portfolio
    )
    
    def __init__(self):
        super().__init__()
        self.agent = None
        self.position_size = 0
        self.current_signal = None
        # Initialize default attributes for testing purposes
        if not hasattr(self, 'datas'):
            self.datas = []
        if not hasattr(self, 'broker'):
            self.broker = None
        
    def set_agent(self, agent: 'TradingAgent'):
        """Set the controlling agent."""
        self.agent = agent
        
    def next(self):
        """
        Main strategy logic driven by agent decisions.
        """
        if not self.agent or not self.params.agent_enabled:
            return
            
        # Check if we have data and broker (skip if in test mode)
        if not self.datas or not self.broker:
            return
            
        # Get current market data
        current_data = {
            'close': self.datas[0].close[0],
            'open': self.datas[0].open[0],
            'high': self.datas[0].high[0],
            'low': self.datas[0].low[0],
            'volume': self.datas[0].volume[0],
            'date': self.datas[0].datetime.date(0).isoformat(),
            'portfolio_value': self.broker.getvalue(),
            'cash': self.broker.getcash(),
            'position': self.position.size if hasattr(self, 'position') and self.position else 0
        }
        
        # Get agent decision (this would be called asynchronously in real implementation)
        decision = self.agent.get_trading_decision(current_data)
        
        if decision['action'] == 'BUY' and not self.position:
            size = self._calculate_position_size(decision.get('confidence', 0.5))
            self.buy(size=size)
            self.log(f"BUY SIGNAL - Size: {size}, Confidence: {decision.get('confidence', 0.5)}")
            
        elif decision['action'] == 'SELL' and self.position:
            self.close()
            self.log(f"SELL SIGNAL - Confidence: {decision.get('confidence', 0.5)}")
            
    def _calculate_position_size(self, confidence: float) -> int:
        """Calculate position size based on confidence and risk parameters."""
        # Handle case where broker is None (testing mode)
        if not self.broker or not self.datas:
            return 1  # Default size for testing
            
        portfolio_value = self.broker.getvalue()
        risk_amount = portfolio_value * self.params.risk_tolerance
        current_price = self.datas[0].close[0]
        
        # Adjust by confidence
        adjusted_risk = risk_amount * confidence
        position_size = int(adjusted_risk / current_price)
        
        # Apply maximum position size constraint
        max_size = int(portfolio_value * self.params.max_position_size / current_price)
        
        return min(position_size, max_size)


class TradingAgent:
    """
    ADK-powered trading agent that can analyze market data, execute strategies,
    and provide intelligent trading insights.
    """
    
    def __init__(self, 
                 name: str = "trading_agent",
                 model: str = "gemini-2.0-flash",
                 initial_cash: float = 100000.0):
        """
        Initialize the Trading Agent.
        
        Args:
            name: Name of the agent
            model: LLM model to use
            initial_cash: Initial cash for backtesting
        """
        self.name = name
        self.model = model
        self.initial_cash = initial_cash
        self.session_service = None
        self.runner = None
        self.agent = None
        self.data_provider = DataProvider()
        self.backtest_engine = BacktestEngine(initial_cash=initial_cash)
        self.current_results = None
        
        # Initialize ADK agent
        self._setup_agent()
        
    def _setup_agent(self):
        """Set up the ADK agent with trading tools."""
        self.agent = Agent(
            name=self.name,
            model=self.model,
            description="AI-powered trading agent capable of analyzing market data, executing strategies, and providing trading insights.",
            instruction="""You are an expert trading agent with deep knowledge of financial markets and trading strategies.
            
Your capabilities include:
1. Analyzing market data and identifying trading opportunities
2. Running backtests on historical data with various strategies
3. Providing risk-adjusted position sizing recommendations
4. Generating comprehensive trading reports and insights
5. Adapting strategies based on market conditions

When making trading decisions:
- Always consider risk management principles
- Provide confidence levels for your recommendations
- Explain your reasoning clearly
- Consider market volatility and trends
- Never recommend risking more than 2% of portfolio on a single trade

You can execute the following actions:
- run_simple_backtest: Execute a backtest with specified parameters
- analyze_strategy_performance: Analyze the results of a strategy
- generate_market_data: Create synthetic data for testing
- get_trading_decision: Make a trading decision based on current market data
""",
            tools=[
                self.run_simple_backtest,
                self.analyze_strategy_performance,
                self.generate_market_data,
                self.get_trading_decision
            ]
        )
        
    async def setup_session(self, user_id: str = "trader_1", session_id: str = None):
        """Set up session for conversation with the agent."""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        self.session_service = InMemorySessionService()
        session = await self.session_service.create_session(
            app_name="trading_agent_app",
            session_id=session_id,
            user_id=user_id  # Add the required user_id parameter
        )
        
        self.runner = Runner(
            agent=self.agent,
            session_service=self.session_service,
            app_name="trading_agent_app"  # Add the required app_name parameter
        )
        
        # Store session_id for later use
        self.current_session_id = session_id
        
        return session_id
        
    def run_backtest(self, 
                    strategy_name: str,
                    start_date: str,
                    end_date: str,
                    strategy_params: Optional[Dict[str, Any]] = None,
                    data_feed: Optional[DataFeed] = None) -> Dict[str, Any]:
        """
        Run a backtest with the specified strategy and parameters.
        
        Args:
            strategy_name: Name of the strategy to test (e.g., 'sma', 'rsi', 'bollinger')
            start_date: Start date for backtest (YYYY-MM-DD format)
            end_date: End date for backtest (YYYY-MM-DD format)
            strategy_params: Strategy-specific parameters
            data_feed: Optional pre-loaded data feed (if None, synthetic data will be generated)
            
        Returns:
            Dictionary containing backtest results
        """
        try:
            # Set default values if not provided
            if not start_date:
                start_date = "2022-01-01"
            if not end_date:
                end_date = "2023-12-31"
                
            # Use provided data feed or generate synthetic data
            if data_feed is None:
                data_feed = self.data_provider.generate_synthetic(
                    start_date=start_date,
                    end_date=end_date,
                    initial_price=100
                )
            
            
            # Map strategy names to classes
            from ..strategies.sma import SimpleMovingAverageStrategy
            from ..strategies.rsi import RSIStrategy
            from ..strategies.bollinger import BollingerBandsStrategy
            
            strategy_map = {
                'sma': SimpleMovingAverageStrategy,
                'rsi': RSIStrategy,
                'bollinger': BollingerBandsStrategy
            }
            
            if strategy_name.lower() not in strategy_map:
                available_strategies = list(strategy_map.keys())
                return {
                    'error': f"Strategy '{strategy_name}' not found. Available strategies: {available_strategies}"
                }
                
            strategy_class = strategy_map[strategy_name.lower()]
            strategy_params = strategy_params or {}
            
            # Run backtest
            results = self.backtest_engine.run_backtest(
                data_feed=data_feed,
                strategy_class=strategy_class,
                strategy_params=strategy_params
            )
            
            self.current_results = results
            
            return {
                'success': True,
                'strategy': strategy_name,
                'parameters': strategy_params,
                'start_date': start_date,
                'end_date': end_date,
                'initial_cash': self.initial_cash,
                'final_value': results.get('final_portfolio_value', 0),
                'total_return': results.get('total_return', 0),
                'total_trades': results.get('total_trades', 0),
                'win_rate': results.get('win_rate', 0),
                'max_drawdown': results.get('max_drawdown', 0),
                'sharpe_ratio': results.get('sharpe_ratio', 0)
            }
            
        except Exception as e:
            return {
                'error': f"Backtest failed: {str(e)}",
                'success': False
            }
            
    def analyze_strategy_performance(self, results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze the performance of a strategy backtest.
        
        Args:
            results: Backtest results to analyze (uses current_results if None)
            
        Returns:
            Dictionary containing detailed performance analysis
        """
        if results is None:
            results = self.current_results
            
        if not results:
            return {'error': 'No backtest results available. Run a backtest first.'}
            
        try:
            analysis = {
                'performance_summary': {
                    'total_return': results.get('total_return', 0),
                    'annualized_return': results.get('annualized_return', 0),
                    'volatility': results.get('volatility', 0),
                    'sharpe_ratio': results.get('sharpe_ratio', 0),
                    'max_drawdown': results.get('max_drawdown', 0),
                    'calmar_ratio': results.get('calmar_ratio', 0)
                },
                'trading_metrics': {
                    'total_trades': results.get('total_trades', 0),
                    'winning_trades': results.get('winning_trades', 0),
                    'losing_trades': results.get('losing_trades', 0),
                    'win_rate': results.get('win_rate', 0),
                    'avg_win': results.get('avg_win', 0),
                    'avg_loss': results.get('avg_loss', 0),
                    'profit_factor': results.get('profit_factor', 0)
                },
                'risk_metrics': {
                    'value_at_risk': results.get('value_at_risk', 0),
                    'expected_shortfall': results.get('expected_shortfall', 0),
                    'beta': results.get('beta', 0),
                    'alpha': results.get('alpha', 0)
                }
            }
            
            # Performance rating
            sharpe_ratio = results.get('sharpe_ratio', 0)
            if sharpe_ratio > 2.0:
                rating = "Excellent"
            elif sharpe_ratio > 1.0:
                rating = "Good"
            elif sharpe_ratio > 0.5:
                rating = "Average"
            else:
                rating = "Poor"
                
            analysis['overall_rating'] = rating
            analysis['recommendations'] = self._generate_recommendations(results)
            
            return analysis
            
        except Exception as e:
            return {'error': f"Analysis failed: {str(e)}"}
            
    def generate_market_data(self,
                           start_date: str,
                           end_date: str,
                           initial_price: float,
                           volatility: float) -> Dict[str, Any]:
        """
        Generate synthetic market data for testing.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            initial_price: Starting price
            volatility: Price volatility (e.g., 0.2 = 20%)
            
        Returns:
            Dictionary containing data generation results
        """
        try:
            # Set default values if not provided
            if not start_date:
                start_date = "2022-01-01"
            if not end_date:
                end_date = "2023-12-31"
            if not initial_price:
                initial_price = 100
            if not volatility:
                volatility = 0.2
            data_feed = self.data_provider.generate_synthetic(
                start_date=start_date,
                end_date=end_date,
                initial_price=initial_price,
                volatility=volatility
            )
            
            return {
                'success': True,
                'start_date': start_date,
                'end_date': end_date,
                'initial_price': initial_price,
                'volatility': volatility,
                'data_points': len(data_feed.data),
                'sample_data': data_feed.data.head().to_dict('records')
            }
            
        except Exception as e:
            return {'error': f"Data generation failed: {str(e)}"}
            
    def get_trading_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a trading decision based on current market data.
        
        Args:
            market_data: Current market data including OHLCV and portfolio info
            
        Returns:
            Dictionary containing trading decision and reasoning
        """
        try:
            # Simple decision logic (in a real implementation, this could use ML models)
            close_price = market_data.get('close', 0)
            portfolio_value = market_data.get('portfolio_value', 0)
            current_position = market_data.get('position', 0)
            
            # Simple momentum-based decision
            if 'previous_close' in market_data:
                price_change = (close_price - market_data['previous_close']) / market_data['previous_close']
                
                if price_change > 0.02 and current_position == 0:  # 2% upward move
                    decision = {
                        'action': 'BUY',
                        'confidence': min(abs(price_change) * 10, 1.0),
                        'reasoning': f"Strong upward momentum ({price_change:.2%})",
                        'risk_level': 'Medium'
                    }
                elif price_change < -0.02 and current_position > 0:  # 2% downward move
                    decision = {
                        'action': 'SELL',
                        'confidence': min(abs(price_change) * 10, 1.0),
                        'reasoning': f"Downward momentum detected ({price_change:.2%})",
                        'risk_level': 'Medium'
                    }
                else:
                    decision = {
                        'action': 'HOLD',
                        'confidence': 0.5,
                        'reasoning': "No clear signal detected",
                        'risk_level': 'Low'
                    }
            else:
                decision = {
                    'action': 'HOLD',
                    'confidence': 0.5,
                    'reasoning': "Insufficient data for decision",
                    'risk_level': 'Low'
                }
                
            return decision
            
        except Exception as e:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reasoning': f"Error in decision making: {str(e)}",
                'risk_level': 'High'
            }
            
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate strategy improvement recommendations based on results."""
        recommendations = []
        
        sharpe_ratio = results.get('sharpe_ratio', 0)
        max_drawdown = results.get('max_drawdown', 0)
        win_rate = results.get('win_rate', 0)
        
        if sharpe_ratio < 1.0:
            recommendations.append("Consider improving risk-adjusted returns by optimizing position sizing")
            
        if max_drawdown > 0.2:
            recommendations.append("High drawdown detected - implement stronger risk management")
            
        if win_rate < 0.4:
            recommendations.append("Low win rate - consider refining entry/exit criteria")
            
        if not recommendations:
            recommendations.append("Strategy shows good performance - consider live testing")
            
        return recommendations
        
    async def chat(self, message: str, user_id: str = "trader_1", session_id: str = None) -> str:
        """
        Chat with the trading agent.
        
        Args:
            message: User message
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Agent's response
        """
        if not self.runner:
            if session_id is None:
                session_id = await self.setup_session(user_id)
            else:
                await self.setup_session(user_id, session_id)
                
        from google.genai import types
        
        # Create message content
        content = types.Content(parts=[types.Part(text=message)])
        
        # Run agent
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                # Extract text from the response
                if event.content and event.content.parts:
                    return event.content.parts[0].text
                return "No response received"
                
        return "No response received"
    
    def run_simple_backtest(self, 
                           strategy_name: str,
                           start_date: str,
                           end_date: str,
                           strategy_params: Optional[str] = None) -> Dict[str, Any]:
        """
        Simple wrapper for run_backtest with ADK-compatible signature.
        
        Args:
            strategy_name: Name of the strategy to test (e.g., 'sma', 'rsi', 'bollinger')
            start_date: Start date for backtest (YYYY-MM-DD format)
            end_date: End date for backtest (YYYY-MM-DD format)
            strategy_params: Strategy parameters as JSON string (optional)
            
        Returns:
            Dictionary containing backtest results
        """
        # Set default values if not provided
        if not start_date:
            start_date = "2022-01-01"
        if not end_date:
            end_date = "2023-12-31"
            
        # Parse strategy params if provided as string
        parsed_params = None
        if strategy_params:
            try:
                import json
                parsed_params = json.loads(strategy_params)
            except:
                parsed_params = {}
        
        # Call the original method with synthetic data
        return self.run_backtest(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            strategy_params=parsed_params,
            data_feed=None  # Always use synthetic data for agent calls
        )
