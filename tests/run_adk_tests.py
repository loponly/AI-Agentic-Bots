#!/usr/bin/env python3
"""
ADK Agent Test Runner
====================

This script runs specific ADK agent tests for validation and comprehensive testing.
"""

import sys
import os
import subprocess
from pathlib import Path


def run_adk_validation():
    """Run the ADK agent validation test."""
    print("🔍 Running ADK Agent Validation...")
    print("=" * 50)
    
    result = subprocess.run([
        sys.executable, "tests/validate_adk_agent.py"
    ], cwd=Path(__file__).parent.parent)
    
    return result.returncode == 0


def run_comprehensive_test():
    """Run the comprehensive ADK agent test."""
    print("🔍 Running Comprehensive ADK Agent Test...")
    print("=" * 50)
    
    result = subprocess.run([
        sys.executable, "tests/test_comprehensive_agent.py"
    ], cwd=Path(__file__).parent.parent)
    
    return result.returncode == 0


def main():
    """Run ADK agent tests."""
    print("ADK Agent Test Runner")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "validate":
            success = run_adk_validation()
        elif test_type == "comprehensive":
            success = run_comprehensive_test()
        elif test_type == "all":
            print("Running all ADK agent tests...\n")
            success1 = run_adk_validation()
            print("\n")
            success2 = run_comprehensive_test()
            success = success1 and success2
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python tests/run_adk_tests.py [validate|comprehensive|all]")
            return False
    else:
        # Default: run all tests
        print("Running all ADK agent tests...\n")
        success1 = run_adk_validation()
        print("\n")
        success2 = run_comprehensive_test()
        success = success1 and success2
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All ADK agent tests passed!")
        print("✅ The ADK agent is ready for use!")
    else:
        print("❌ Some ADK agent tests failed!")
        print("Please check the output above for details.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
