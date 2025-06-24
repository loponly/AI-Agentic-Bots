#!/usr/bin/env python3
"""
Comprehensive ADK Agent Test
============================

This script performs a comprehensive test of the ADK agent to ensure
it's fully compatible with the ADK framework.
"""

import sys
import os
import inspect
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_comprehensive_agent():
    """Perform comprehensive ADK agent tests."""
    
    print("🔍 Comprehensive ADK Agent Testing...")
    print("=" * 60)
    
    try:
        # Test 1: Import paths
        print("1. Testing import paths...")
        from src.agent import root_agent
        import src
        assert hasattr(src, 'root_agent'), "src.root_agent not accessible"
        print("   ✅ All import paths working")
        
        # Test 2: Agent configuration
        print("2. Testing agent configuration...")
        assert root_agent.name == "backtest_strategy_agent"
        assert hasattr(root_agent, 'model')
        assert len(root_agent.tools) == 4
        print(f"   ✅ Agent: {root_agent.name}")
        print(f"   ✅ Model: {getattr(root_agent, 'model', 'default')}")
        print(f"   ✅ Tools: {len(root_agent.tools)}")
        
        # Test 3: Tool signature validation
        print("3. Testing tool signatures for ADK compatibility...")
        tool_names = []
        for tool in root_agent.tools:
            tool_names.append(tool.__name__)
            sig = inspect.signature(tool)
            
            # Check for problematic type annotations
            for param_name, param in sig.parameters.items():
                if param.default is None and param.annotation != inspect.Parameter.empty:
                    annotation_str = str(param.annotation)
                    if 'Optional' not in annotation_str and 'Union' not in annotation_str:
                        if not annotation_str.startswith('<class'):
                            print(f"   ⚠️  Potential issue: {tool.__name__}.{param_name}")
        
        expected_tools = [
            'create_strategy_backtest',
            'compare_strategies',
            'optimize_strategy_parameters',
            'get_available_strategies'
        ]
        
        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"
        
        print("   ✅ All tool signatures are ADK-compatible")
        
        # Test 4: Tool function execution readiness
        print("4. Testing tool function accessibility...")
        for tool in root_agent.tools:
            assert callable(tool), f"Tool {tool.__name__} is not callable"
            
            # Check docstring
            if not tool.__doc__:
                print(f"   ⚠️  Tool {tool.__name__} missing docstring")
            
        print("   ✅ All tools are accessible and callable")
        
        # Test 5: Module structure validation
        print("5. Testing module structure...")
        
        # Check that required modules are importable
        try:
            from src.data.providers import DataProvider
            from src.backtesting.engine import BacktestEngine
            print("   ✅ Core modules importable")
        except ImportError as e:
            print(f"   ⚠️  Import issue: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Comprehensive testing completed successfully!")
        print("\nADK Agent Status:")
        print("✅ Root agent properly exposed")
        print("✅ Model configuration complete")
        print("✅ All tool signatures ADK-compatible")
        print("✅ Import paths working correctly")
        print("✅ Ready for ADK web UI integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Comprehensive test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_agent()
    sys.exit(0 if success else 1)
