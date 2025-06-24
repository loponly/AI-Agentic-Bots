# Tests Directory

This directory contains all test files for the AI-Agentic-Bots trading system.

## ADK Agent Tests

The following files are specifically for testing the ADK (Agent Development Kit) agent configuration:

### Test Files

- **`validate_adk_agent.py`** - Basic validation test for ADK agent configuration
- **`test_comprehensive_agent.py`** - Comprehensive test suite for ADK agent functionality
- **`run_adk_tests.py`** - Test runner for ADK agent tests

### Usage

#### Quick Validation
```bash
python tests/run_adk_tests.py validate
```

#### Comprehensive Testing
```bash
python tests/run_adk_tests.py comprehensive
```

#### All ADK Tests
```bash
python tests/run_adk_tests.py all
```

#### Individual Tests
```bash
# Basic validation
python tests/validate_adk_agent.py

# Comprehensive test
python tests/test_comprehensive_agent.py
```

### What These Tests Validate

1. **Root Agent Exposure** - Ensures the agent is properly exposed at `src.agent.root_agent`
2. **Model Configuration** - Verifies the agent has a valid model configuration
3. **Tool Signatures** - Checks all tool function signatures are ADK-compatible
4. **Import Paths** - Validates all import paths work correctly
5. **Module Structure** - Ensures core modules are importable

## Other Tests

The directory also contains various other test files for different components of the trading system:

- `test_binance_*.py` - Binance API integration tests
- `test_trading_agent.py` - Trading agent functionality tests
- `test_system*.py` - System integration tests
- `run_all_tests.py` - Runs all tests using pytest

## Running All Tests

To run all tests in the directory:
```bash
python tests/run_all_tests.py
```

Or using pytest directly:
```bash
pytest tests/ -v
```
