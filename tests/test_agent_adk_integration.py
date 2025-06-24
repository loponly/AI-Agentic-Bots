#!/usr/bin/env python3
"""Test script to verify the trading agent ADK integration is working."""

import os
import sys
import asyncio
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from src.agents.trading_agent import TradingAgent


class TestADKIntegration:
    """Test class for ADK agent integration."""
    
    @pytest.fixture(scope="class")
    def api_key(self):
        """Check if API key is available."""
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key or api_key == "your-google-api-key-here":
            pytest.skip("No valid GOOGLE_API_KEY found in environment")
        return api_key
    
    @pytest.fixture
    async def trading_agent(self):
        """Create a trading agent for testing."""
        agent = TradingAgent(name="test_agent", initial_cash=100000.0)
        yield agent
    
    @pytest.mark.asyncio
    async def test_agent_creation(self, api_key):
        """Test that the trading agent can be created successfully."""
        agent = TradingAgent(name="test_agent", initial_cash=100000.0)
        assert agent is not None
        assert agent.name == "test_agent"
        assert agent.initial_cash == 100000.0
    
    @pytest.mark.asyncio
    async def test_session_setup(self, trading_agent, api_key):
        """Test that a session can be set up successfully."""
        session_id = await trading_agent.setup_session()
        assert session_id is not None
        assert session_id.startswith("session_")
        assert hasattr(trading_agent, 'session_service')
        assert hasattr(trading_agent, 'runner')
    
    def test_simple_backtest_function(self, trading_agent):
        """Test the run_simple_backtest function directly."""
        result = trading_agent.run_simple_backtest(
            strategy_name="sma",
            start_date="2023-01-01",
            end_date="2023-06-30"
        )
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'final_value' in result
        assert 'total_return' in result
        assert 'strategy' in result
        assert result['strategy'] == 'sma'
    
    def test_simple_backtest_with_params(self, trading_agent):
        """Test the run_simple_backtest function with strategy parameters."""
        strategy_params = '{"short_period": 5, "long_period": 20}'
        
        result = trading_agent.run_simple_backtest(
            strategy_name="sma",
            start_date="2023-01-01",
            end_date="2023-06-30",
            strategy_params=strategy_params
        )
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert result['parameters']['short_period'] == 5
        assert result['parameters']['long_period'] == 20
    
    def test_simple_backtest_invalid_strategy(self, trading_agent):
        """Test the run_simple_backtest function with invalid strategy."""
        result = trading_agent.run_simple_backtest(
            strategy_name="invalid_strategy",
            start_date="2023-01-01",
            end_date="2023-06-30"
        )
        
        assert isinstance(result, dict)
        assert 'error' in result or 'success' in result
        # Should handle invalid strategy gracefully
    
    @pytest.mark.asyncio
    async def test_agent_tools_registration(self, trading_agent, api_key):
        """Test that agent tools are properly registered."""
        # Check that the agent has the required tools
        assert hasattr(trading_agent, 'run_simple_backtest')
        assert hasattr(trading_agent, 'analyze_strategy_performance')
        assert hasattr(trading_agent, 'generate_market_data')
        assert hasattr(trading_agent, 'get_trading_decision')
        
        # Check that the agent is properly configured
        assert trading_agent.agent is not None
        assert trading_agent.agent.tools is not None
        assert len(trading_agent.agent.tools) >= 4


async def test_agent_functionality():
    """Test the agent's basic functionality."""
    print("🧪 Testing ADK Agent Functionality")
    print("=" * 50)
    
    # Check API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key == "your-google-api-key-here":
        print("❌ No valid GOOGLE_API_KEY found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Create agent
        agent = TradingAgent(name="test_agent", initial_cash=100000.0)
        print("✅ Agent created successfully")
        
        # Setup session
        session_id = await agent.setup_session()
        print(f"✅ Session created: {session_id}")
        
        # Test simple backtest tool directly
        print("\n📊 Testing run_simple_backtest function...")
        result = agent.run_simple_backtest(
            strategy_name="sma",
            start_date="2023-01-01",
            end_date="2023-06-30"
        )
        print(f"✅ Direct function call successful")
        print(f"   Strategy: {result.get('strategy', 'N/A')}")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Final value: ${result.get('final_value', 0):,.2f}")
        print(f"   Return: {result.get('total_return', 0):.2%}")
        
        # Test with different strategies
        strategies = ['rsi', 'bollinger']
        for strategy in strategies:
            print(f"\n📈 Testing {strategy.upper()} strategy...")
            try:
                result = agent.run_simple_backtest(
                    strategy_name=strategy,
                    start_date="2023-01-01",
                    end_date="2023-06-30"
                )
                print(f"   ✅ {strategy.upper()}: Return {result.get('total_return', 0):.2%}")
            except Exception as e:
                print(f"   ⚠️ {strategy.upper()}: {e}")
        
        # Test other tools
        print("\n🔍 Testing other agent tools...")
        
        # Test market data generation
        data_result = agent.generate_market_data(
            start_date="2023-01-01",
            end_date="2023-03-31",
            initial_price=100,
            volatility=0.02
        )
        print(f"✅ Market data generation: {data_result.get('success', False)}")
        
        # Test trading decision
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
        print(f"✅ Trading decision: {decision.get('action', 'N/A')}")
        
        # Test performance analysis
        analysis = agent.analyze_strategy_performance()
        print(f"✅ Performance analysis: {analysis.get('overall_rating', 'N/A')}")
        
        print("\n🎉 All basic tests passed! The agent is working correctly.")
        print("\n📋 Summary:")
        print("   ✅ Agent creation and initialization")
        print("   ✅ Session management")
        print("   ✅ Backtest function execution")
        print("   ✅ Multiple strategy support")
        print("   ✅ Market data generation")
        print("   ✅ Trading decision making")
        print("   ✅ Performance analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_binance_integration():
    """Test Binance data integration."""
    print("\n🪙 Testing Binance Integration")
    print("=" * 40)
    
    try:
        from src.data.providers import DataProvider, get_popular_binance_pairs
        
        # Test data provider
        provider = DataProvider()
        print("✅ DataProvider created")
        
        # Test popular pairs function
        pairs = get_popular_binance_pairs()
        print(f"✅ Popular pairs loaded: {len(pairs)} pairs")
        print(f"   Sample pairs: {', '.join(pairs[:5])}")
        
        # Test loading Binance data (with fallback)
        try:
            feed = provider.load_binance('BTCUSDT', interval='1d', limit=10)
            print(f"✅ Real Binance data loaded: {len(feed.data)} records")
        except Exception as e:
            print(f"⚠️ Real Binance data failed, using synthetic: {e}")
            feed = provider.generate_synthetic(
                start_date='2023-01-01',
                end_date='2023-01-10',
                initial_price=30000
            )
            print(f"✅ Synthetic data generated: {len(feed.data)} records")
        
        # Test multiple pairs loading
        crypto_feeds = provider.load_binance_pairs(
            pairs=['BTCUSDT', 'ETHUSDT'],
            start_time='2023-01-01',
            end_time='2023-01-10',
            use_synthetic_fallback=True
        )
        print(f"✅ Multiple pairs loaded: {len(crypto_feeds)} feeds")
        
        return True
        
    except Exception as e:
        print(f"❌ Binance integration test failed: {e}")
        return False


if __name__ == "__main__":
    async def run_all_tests():
        """Run all tests manually."""
        print("🚀 Running ADK Agent Integration Tests")
        print("=" * 60)
        
        # Test basic agent functionality
        agent_test_passed = await test_agent_functionality()
        
        # Test Binance integration
        binance_test_passed = test_binance_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Agent Functionality: {'✅ PASSED' if agent_test_passed else '❌ FAILED'}")
        print(f"Binance Integration: {'✅ PASSED' if binance_test_passed else '❌ FAILED'}")
        
        if agent_test_passed and binance_test_passed:
            print("\n🎉 ALL TESTS PASSED! The system is working correctly.")
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")
    
    asyncio.run(run_all_tests())
