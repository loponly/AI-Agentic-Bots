#!/usr/bin/env python3
"""
ADK Agent Validation Script
===========================

This script validates that the root_agent is properly configured for the ADK framework.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_agent():
    """Validate that the root agent is properly configured."""
    
    print("🔍 Validating ADK Agent Configuration...")
    print("=" * 50)
    
    try:
        # Test 1: Import via src.agent
        print("1. Testing import via src.agent...")
        from src.agent import root_agent
        print(f"   ✅ Successfully imported root_agent: {root_agent.name}")
        
        # Test 2: Import via src module
        print("2. Testing import via src module...")
        import src
        assert hasattr(src, 'root_agent'), "src.root_agent not found"
        print(f"   ✅ Successfully accessed src.root_agent: {src.root_agent.name}")
        
        # Test 3: Validate agent configuration
        print("3. Validating agent configuration...")
        assert root_agent.name == "backtest_strategy_agent", f"Unexpected agent name: {root_agent.name}"
        assert len(root_agent.tools) == 4, f"Expected 4 tools, got {len(root_agent.tools)}"
        
        # Check if model is specified
        model = getattr(root_agent, 'model', None)
        if model:
            print(f"   ✅ Agent configured with model: {model}")
        else:
            print("   ⚠️  Agent using default model (no explicit model specified)")
        
        print(f"   ✅ Agent properly configured with {len(root_agent.tools)} tools")
        
        # Test 4: List available tools
        print("4. Available tools:")
        for tool in root_agent.tools:
            print(f"   - {tool.__name__}")
        
        # Test 5: Test tool function access
        print("5. Testing tool function access...")
        tool_names = [tool.__name__ for tool in root_agent.tools]
        expected_tools = [
            'create_strategy_backtest',
            'compare_strategies', 
            'optimize_strategy_parameters',
            'get_available_strategies'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing expected tool: {expected_tool}"
        print("   ✅ All expected tools are available")
        
        print("\n" + "=" * 50)
        print("🎉 All validations passed! ADK agent is ready to use.")
        print("\nTo use this agent with ADK:")
        print("1. Ensure your ADK server is configured to look in the 'src' directory")
        print("2. The agent will be available as 'src.agent.root_agent'")
        print("3. The agent provides comprehensive trading strategy backtesting capabilities")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_agent()
    sys.exit(0 if success else 1)
