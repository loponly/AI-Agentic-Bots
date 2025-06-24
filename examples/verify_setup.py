#!/usr/bin/env python3
"""
ADK Setup Verification
=====================

This script verifies that the ADK trading agents are properly configured
and ready to run.
"""

import os
import sys
from pathlib import Path

def check_adk_setup():
    """Check ADK setup and provide status report."""
    
    print("🔍 ADK Trading Agents Setup Verification")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 6
    
    # Check 1: Google API Key
    print("\n1. Checking Google API Key...")
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key and api_key != 'YOUR_GOOGLE_API_KEY_HERE':
        print("   ✅ Google API Key is configured")
        checks_passed += 1
    else:
        print("   ❌ Google API Key not set or using placeholder")
        print("      → Set GOOGLE_API_KEY in .env file")
        print("      → Get key from: https://aistudio.google.com/app/apikey")
    
    # Check 2: ADK Installation
    print("\n2. Checking ADK installation...")
    try:
        import google.adk.agents
        print("   ✅ ADK library is installed")
        checks_passed += 1
    except ImportError:
        print("   ❌ ADK library not installed")
        print("      → Run: pip install google-adk")
    
    # Check 3: Main Agent Import
    print("\n3. Checking main agent...")
    try:
        # Add parent directory to path to import agent module
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        from agent import root_agent
        print(f"   ✅ Main agent '{root_agent.name}' imported successfully")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to import main agent: {e}")
    
    # Check 4: Simplified Agents
    print("\n4. Checking simplified agents...")
    try:
        # Import from parent directory
        from simplified_agents import simplified_backtest_agent, simplified_market_agent
        print("   ✅ Simplified agents imported successfully")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to import simplified agents: {e}")
    
    # Check 5: Environment File
    print("\n5. Checking environment configuration...")
    env_file = Path(__file__).parent.parent / '.env'  # Look in parent directory
    if env_file.exists():
        print("   ✅ .env file exists")
        checks_passed += 1
    else:
        print("   ❌ .env file not found")
        print("      → Create .env file with GOOGLE_API_KEY")
    
    # Check 6: Dependencies
    print("\n6. Checking dependencies...")
    required_packages = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'), 
        ('python-dotenv', 'dotenv')
    ]
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if not missing_packages:
        print("   ✅ All required dependencies installed")
        checks_passed += 1
    else:
        print(f"   ❌ Missing packages: {', '.join(missing_packages)}")
        print("      → Run: pip install -r requirements.txt")
    
    # Summary
    print(f"\n📊 Setup Status: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("\n🎉 Setup Complete! Ready to launch ADK agents")
        print("\n🚀 Next Steps:")
        print("   1. Run: adk web")
        print("   2. Open the web interface in your browser")
        print("   3. Start chatting with the trading agents!")
        print("\n💡 Example questions to try:")
        print("   • 'What trading strategies do you recommend for beginners?'")
        print("   • 'Analyze current market trends for Bitcoin'")
        print("   • 'Generate trading signals for ETHUSDT'")
        return True
    else:
        print(f"\n⚠️  Setup incomplete: {total_checks - checks_passed} issues to fix")
        print("\n🔧 Please address the issues above and run this check again")
        return False


def show_usage_guide():
    """Show comprehensive usage guide."""
    
    print("\n" + "="*60)
    print("📚 ADK Trading Agents Usage Guide")
    print("="*60)
    
    print("\n🎯 Available Agents:")
    print("   1. Strategy Agent - Trading strategy analysis and development")
    print("   2. Market Research Agent - Market analysis and trading signals")
    
    print("\n🖥️  Launch Options:")
    print("   adk web        - Web interface (recommended)")
    print("   adk run        - Terminal interface")
    print("   adk api_server - REST API server")
    
    print("\n💬 Example Conversations:")
    print("\n   Strategy Development:")
    print("   User: 'Explain how RSI strategy works'")
    print("   Agent: Provides detailed RSI explanation, parameters, and use cases")
    print()
    print("   User: 'Which strategy is best for volatile markets?'")
    print("   Agent: Compares strategies and recommends based on volatility")
    
    print("\n   Market Analysis:")
    print("   User: 'What's the current trend for major cryptocurrencies?'")
    print("   Agent: Analyzes BTC, ETH, ADA trends with data and insights")
    print()
    print("   User: 'Generate trading signals for BTCUSDT'")
    print("   Agent: Provides buy/sell/hold signals with reasoning")
    
    print("\n🛡️  Safety Features:")
    print("   • Educational content only - not financial advice")
    print("   • Risk warnings included in all responses")
    print("   • Emphasis on paper trading and learning")
    print("   • Clear disclaimers about market volatility")
    
    print("\n🔧 Troubleshooting:")
    print("   • If agents don't respond: Check GOOGLE_API_KEY in .env")
    print("   • If imports fail: Run from project root directory")
    print("   • If web UI doesn't start: Install google-adk library")


if __name__ == "__main__":
    if check_adk_setup():
        if len(sys.argv) > 1 and sys.argv[1] == '--guide':
            show_usage_guide()
    else:
        sys.exit(1)
