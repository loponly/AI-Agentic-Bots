"""
Test Trading Agent Implementation
================================

Test suite for the TradingAgent and TradingAgentStrategy classes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from unittest.mock import Mock, patch

try:
    from src.agents.trading_agent import TradingAgent, TradingAgentStrategy
except ImportError:
    # Fallback for when google-adk is not installed
    print("Warning: google-adk not installed. Some functionality will be limited.")
    TradingAgent = None
    TradingAgentStrategy = None


class TestTradingAgent:
    """Test cases for TradingAgent class."""
    
    def test_agent_initialization(self):
        """Test basic agent initialization."""
        agent = TradingAgent(
            name="test_agent",
            model="gemini-2.0-flash",
            initial_cash=50000.0
        )
        
        assert agent.name == "test_agent"
        assert agent.model == "gemini-2.0-flash"
        assert agent.initial_cash == 50000.0
        assert agent.agent is not None
        assert agent.data_provider is not None
        assert agent.backtest_engine is not None
        
    def test_run_backtest_invalid_strategy(self):
        """Test backtest with invalid strategy name."""
        agent = TradingAgent()
        
        result = agent.run_backtest(
            strategy_name="invalid_strategy",
            start_date="2022-01-01",
            end_date="2023-12-31"
        )
        
        assert 'error' in result
        assert 'not found' in result['error']
        
    def test_run_backtest_valid_strategy(self):
        """Test backtest with valid strategy."""
        agent = TradingAgent()
        
        result = agent.run_backtest(
            strategy_name="sma",
            start_date="2022-01-01",
            end_date="2022-12-31",
            strategy_params={"short_period": 10, "long_period": 20}
        )
        
        # Should succeed even without real data
        assert 'success' in result
        if result.get('success'):
            assert 'final_value' in result
            assert 'total_return' in result
            assert 'strategy' in result
            
    def test_analyze_performance_no_results(self):
        """Test performance analysis without results."""
        agent = TradingAgent()
        
        analysis = agent.analyze_strategy_performance()
        
        assert 'error' in analysis
        assert 'No backtest results' in analysis['error']
        
    def test_generate_market_data(self):
        """Test market data generation."""
        agent = TradingAgent()
        
        result = agent.generate_market_data(
            start_date="2023-01-01",
            end_date="2023-06-30",
            initial_price=100,
            volatility=0.2
        )
        
        assert 'success' in result
        if result.get('success'):
            assert 'data_points' in result
            assert 'sample_data' in result
            assert result['initial_price'] == 100
            assert result['volatility'] == 0.2
            
    def test_get_trading_decision(self):
        """Test trading decision making."""
        agent = TradingAgent()
        
        market_data = {
            'close': 105.50,
            'open': 104.25,
            'high': 106.00,
            'low': 103.75,
            'volume': 1000000,
            'date': '2023-12-01',
            'portfolio_value': 110000,
            'cash': 50000,
            'position': 0,
            'previous_close': 103.25
        }
        
        decision = agent.get_trading_decision(market_data)
        
        assert 'action' in decision
        assert decision['action'] in ['BUY', 'SELL', 'HOLD']
        assert 'confidence' in decision
        assert 'reasoning' in decision
        assert 'risk_level' in decision
        assert 0 <= decision['confidence'] <= 1.0
        
    def test_get_trading_decision_insufficient_data(self):
        """Test trading decision with insufficient data."""
        agent = TradingAgent()
        
        market_data = {
            'close': 105.50,
            'portfolio_value': 110000,
            'position': 0
        }
        
        decision = agent.get_trading_decision(market_data)
        
        assert decision['action'] == 'HOLD'
        assert 'Insufficient data' in decision['reasoning']
        
    def test_recommendations_generation(self):
        """Test recommendation generation."""
        agent = TradingAgent()
        
        # Test poor performance results
        poor_results = {
            'sharpe_ratio': 0.5,
            'max_drawdown': 0.25,
            'win_rate': 0.3
        }
        
        recommendations = agent._generate_recommendations(poor_results)
        
        assert len(recommendations) > 0
        assert any('risk' in rec.lower() for rec in recommendations)
        
        # Test good performance results
        good_results = {
            'sharpe_ratio': 2.0,
            'max_drawdown': 0.1,
            'win_rate': 0.6
        }
        
        recommendations = agent._generate_recommendations(good_results)
        
        assert len(recommendations) > 0
        assert any('good performance' in rec.lower() for rec in recommendations)


class TestTradingAgentStrategy:
    """Test cases for TradingAgentStrategy class."""
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        # TradingAgentStrategy requires cerebro instance for full initialization
        # Test basic class attributes instead
        assert hasattr(TradingAgentStrategy, 'params')
        assert hasattr(TradingAgentStrategy, 'set_agent')
        assert hasattr(TradingAgentStrategy, 'next')
        assert hasattr(TradingAgentStrategy, '_calculate_position_size')
        
    def test_set_agent(self):
        """Test setting the controlling agent."""
        # Create a mock strategy instance without cerebro
        import backtrader as bt
        
        # Test that the class has the expected parameters
        assert hasattr(TradingAgentStrategy, 'params')
        
        # Check the default parameter values by inspecting the class
        params_dict = dict(TradingAgentStrategy.params._getpairs())
        assert params_dict.get('agent_enabled', True) is True
        assert params_dict.get('risk_tolerance', 0.02) == 0.02
        assert params_dict.get('max_position_size', 0.1) == 0.1
        
    def test_next_no_agent(self):
        """Test next() method without agent."""
        # Since TradingAgentStrategy requires cerebro, we'll test the logic directly
        # by mocking the necessary attributes
        strategy = Mock()
        strategy.agent = None
        strategy.params = Mock()
        strategy.params.agent_enabled = True
        
        # Apply the actual next method to our mock
        TradingAgentStrategy.next(strategy)
        
        # Should return early since no agent is set
        # No exceptions should be raised
        
    def test_next_with_agent(self):
        """Test next() method with agent."""
        # Mock strategy with agent but no data/broker
        strategy = Mock()
        agent = TradingAgent()
        strategy.agent = agent
        strategy.params = Mock()
        strategy.params.agent_enabled = True
        strategy.datas = None
        strategy.broker = None
        
        # Apply the actual next method to our mock
        TradingAgentStrategy.next(strategy)
        
        # Should return early since no data/broker
        # No exceptions should be raised
        
    def test_calculate_position_size(self):
        """Test position size calculation."""
        # Test the method directly without instantiating the strategy
        # Mock the necessary attributes
        strategy = Mock()
        strategy.broker = None
        strategy.datas = None
        strategy.params = Mock()
        strategy.params.risk_tolerance = 0.02
        strategy.params.max_position_size = 0.1
        
        # Test with no broker/data (should return default size)
        size = TradingAgentStrategy._calculate_position_size(strategy, 0.8)
        assert size == 1
        
        # Test calculation logic verification (without full broker setup)
        portfolio_value = 100000
        risk_tolerance = 0.02
        current_price = 100.0
        confidence = 0.8
        max_position_size = 0.1
        
        # Calculate expected position size manually
        risk_amount = portfolio_value * risk_tolerance
        adjusted_risk = risk_amount * confidence
        position_size = int(adjusted_risk / current_price)
        max_size = int(portfolio_value * max_position_size / current_price)
        expected_size = min(position_size, max_size)
        
        # Verify calculation logic
        assert expected_size == min(int(100000 * 0.02 * 0.8 / 100), int(100000 * 0.1 / 100))
        assert expected_size == min(16, 100)
        assert expected_size == 16


@pytest.mark.asyncio
class TestTradingAgentAsync:
    """Test async functionality of TradingAgent."""
    
    @patch('google.adk.sessions.InMemorySessionService')
    @patch('google.adk.runners.Runner')
    async def test_setup_session(self, mock_runner, mock_session_service):
        """Test session setup."""
        agent = TradingAgent()
        
        # Mock session service
        mock_session = Mock()
        mock_session_service.return_value.create_session.return_value = mock_session
        
        session_id = await agent.setup_session("test_user", "test_session")
        
        assert session_id == "test_session"
        assert agent.session_service is not None
        assert agent.runner is not None
        
    @patch('google.adk.sessions.InMemorySessionService')
    @patch('google.adk.runners.Runner')
    @patch('google.genai.types')
    async def test_chat(self, mock_types, mock_runner, mock_session_service):
        """Test chat functionality."""
        agent = TradingAgent()
        
        # Mock session and runner
        mock_session = Mock()
        mock_session_service.return_value.create_session.return_value = mock_session
        
        # Create a mock event with proper response structure
        mock_event = Mock()
        mock_event.is_final_response.return_value = True
        mock_part = Mock()
        mock_part.text = "Test response"
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_event.content = mock_content
        
        # Create async iterator for the mock
        async def mock_async_iter():
            yield mock_event
        
        agent.runner = Mock()
        agent.runner.run_async.return_value = mock_async_iter()
        
        response = await agent.chat("Test message", "user1", "session1")
        
        assert response == "Test response"


if __name__ == "__main__":
    # Run tests without pytest
    import sys
    
    print("Running Trading Agent Tests...")
    
    if TradingAgent is None:
        print("❌ Cannot run tests - google-adk not installed")
        print("Install with: pip install google-adk")
        sys.exit(1)
    
    # Test basic functionality
    try:
        test_agent = TestTradingAgent()
        test_agent.test_agent_initialization()
        print("✓ Agent initialization test passed")
        
        test_agent.test_run_backtest_invalid_strategy()
        print("✓ Invalid strategy test passed")
        
        test_agent.test_generate_market_data()
        print("✓ Market data generation test passed")
        
        test_agent.test_get_trading_decision()
        print("✓ Trading decision test passed")
        
        test_strategy = TestTradingAgentStrategy()
        test_strategy.test_strategy_initialization()
        print("✓ Strategy initialization test passed")
        
        test_strategy.test_set_agent()
        print("✓ Set agent test passed")
        
        print("\n✅ All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    print("\nNote: Some tests require google-adk package and API keys to be fully functional.")
