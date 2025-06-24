# File Organization Guidelines

## Directory Structure

### Tests Directory (`tests/`)
All test files should be placed in the `tests/` folder:
- `test_*.py` - Unit tests and integration tests
- Test files should use `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))` to import from src

### Examples Directory (`examples/`)
All example and demonstration files should be placed in the `examples/` folder:
- `*_example.py` - Demonstration scripts
- `demo_*.py` - Demo applications
- Example files should use `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))` to import from src

### Source Directory (`src/`)
Core implementation code:
- `agents/` - Trading agents
- `backtesting/` - Backtesting engine
- `data/` - Data providers and loaders
- `strategies/` - Trading strategies
- `database/` - Database management
- `analyzers/` - Performance analyzers

### Documentation Directory (`docs/`)
All documentation files:
- Implementation guides
- API references
- User manuals

## Import Pattern for Moved Files

When moving files from project root to subdirectories, update the import path:

```python
# From project root:
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# From tests/ or examples/ subdirectory:
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

## Running Tests and Examples

### From Project Root
```bash
# Run tests
python tests/test_binance_provider.py
python tests/test_binance_unit.py

# Run examples
python examples/trading_agent_binance_example.py
python examples/binance_backtest_example.py
```

### File Naming Conventions
- Tests: `test_*.py`
- Examples: `*_example.py` or `demo_*.py`
- Core modules: descriptive names without prefixes

## Benefits of This Organization
1. **Clear separation** between implementation, tests, and examples
2. **Easier navigation** of the codebase
3. **Better IDE support** with organized structure
4. **Standard Python project layout**
5. **Scalable** as the project grows

## Files Moved in Current Organization

### Tests Directory
- `test_binance_provider.py` → `tests/test_binance_provider.py`
- `test_binance_unit.py` → `tests/test_binance_unit.py`

### Examples Directory
- `trading_agent_binance_example.py` → `examples/trading_agent_binance_example.py`
- `binance_backtest_example.py` → `examples/binance_backtest_example.py`

All files have been updated with correct import paths and are fully functional in their new locations.
