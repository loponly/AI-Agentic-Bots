"""
pytest configuration for Trading Backtesting System tests
=========================================================

This file contains shared pytest configuration and fixtures.
"""

import pytest
import sys
import os

# Add project root to path for all tests
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def project_root_path():
    """Fixture that provides the project root path."""
    return os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope="function")
def temp_db_file(tmp_path):
    """Fixture that provides a temporary database file path."""
    return tmp_path / "test_db.db"
