"""
Data Utilities - Backward Compatibility Layer
=============================================

This module provides backward compatibility for the old data utilities API.
"""

import sys
import os

# Add current directory to path to enable imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Re-export everything from the new modular structure
    from src.data.validators import validate_ohlcv_data, is_trading_day
    from src.data.loaders import load_csv_data, load_yahoo_data  
    from src.data.generators import generate_synthetic_data, generate_random_walk
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Warning: Some data utilities imports failed: {e}")
    IMPORTS_SUCCESSFUL = False

if IMPORTS_SUCCESSFUL:
    __all__ = [
        'validate_ohlcv_data',
        'is_trading_day', 
        'load_csv_data',
        'load_yahoo_data',
        'generate_synthetic_data',
        'generate_random_walk'
    ]
else:
    __all__ = []
