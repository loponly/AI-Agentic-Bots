"""
Test Runner - Run All Tests
===========================

This script runs all tests in the tests directory to verify the system is working correctly.
"""

import sys
import os
import subprocess

def run_test_file(test_file):
    """Run a single test file and return success/failure."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {test_file}")
    print('='*60)
    
    try:
        # Get the directory of this script (tests folder)
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the project root (parent of tests folder)
        project_root = os.path.dirname(tests_dir)
        
        # Run the test from the project root directory
        result = subprocess.run(
            [sys.executable, os.path.join('tests', test_file)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"ERROR running {test_file}: {e}")
        return False

def main():
    """Run all tests in the tests directory."""
    print("Trading Backtesting System - Full Test Suite")
    print("="*60)
    
    # Get list of test files
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [f for f in os.listdir(tests_dir) 
                  if f.startswith('test_') and f.endswith('.py')]
    
    if not test_files:
        print("No test files found!")
        return False
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file}")
    
    # Run each test
    results = {}
    for test_file in test_files:
        success = run_test_file(test_file)
        results[test_file] = success
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_file:<30} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The trading backtesting system is fully functional!")
        print("\nYou can now:")
        print("  - Run examples: python examples/example_usage.py")
        print("  - Read documentation: TRADING_README.md")
        print("  - Start developing your own strategies!")
    else:
        print(f"\n❌ {total - passed} test(s) failed!")
        print("Please check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
