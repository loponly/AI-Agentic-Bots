"""
Test Runner - Run All Tests with pytest
=======================================

This script runs all tests in the tests directory using pytest.
"""

import sys
import os
import subprocess


def main():
    """Run all tests using pytest."""
    print("Trading Backtesting System - Full Test Suite (pytest)")
    print("="*60)
    
    # Get the project root directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(tests_dir)
    
    # Change to project root directory
    os.chdir(project_root)
    
    try:
        # Run pytest on the tests directory
        print("Running pytest on tests/ directory...")
        print()
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v",  # verbose output
            "--tb=short",  # short traceback format
            "-x"  # stop on first failure
        ], text=True)
        
        print()
        print("="*60)
        
        if result.returncode == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ The trading backtesting system is fully functional!")
            print("\nNext steps:")
            print("  - Run examples: python examples/example_usage.py")
            print("  - Read documentation: TRADING_README.md")
            print("  - Start developing your own strategies!")
        else:
            print("❌ Some tests failed!")
            print("Please check the output above for details.")
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ pytest not found!")
        print("Please install pytest: pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
