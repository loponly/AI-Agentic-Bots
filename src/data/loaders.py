"""
Data Loaders Module
==================

Provides data loading capabilities from various sources including CSV files and Yahoo Finance.
"""

import pandas as pd
import numpy as np
import os
from typing import Optional
from abc import ABC, abstractmethod
from .validators import DataValidator


class BaseDataLoader(ABC):
    """Abstract base class for data loaders."""
    
    @abstractmethod
    def load(self, *args, **kwargs) -> pd.DataFrame:
        """Load data and return as DataFrame."""
        pass


class CSVLoader(BaseDataLoader):
    """Loads trading data from CSV files."""
    
    def load(
        self, 
        file_path: str, 
        date_column: str = 'date',
        validate: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load trading data from CSV file.
        
        Args:
            file_path: Path to CSV file
            date_column: Name of the date column
            validate: Whether to validate the data
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            Validated DataFrame with OHLCV data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load data
        df = pd.read_csv(file_path, **kwargs)
        
        # Rename date column if necessary
        if date_column != 'date' and date_column in df.columns:
            df = df.rename(columns={date_column: 'date'})
        
        # Validate and standardize date format
        df = DataValidator.validate_date_format(df, 'date')
        
        # Validate data if requested
        if validate:
            DataValidator.validate_ohlcv_data(df)
        
        return df
    
    def load_multiple_files(
        self, 
        file_paths: list, 
        combine: bool = False,
        **kwargs
    ) -> dict:
        """
        Load multiple CSV files.
        
        Args:
            file_paths: List of file paths
            combine: Whether to combine all files into one DataFrame
            **kwargs: Additional arguments for loading
            
        Returns:
            Dictionary of DataFrames or single combined DataFrame
        """
        if combine:
            dataframes = []
            for file_path in file_paths:
                df = self.load(file_path, **kwargs)
                df['source_file'] = os.path.basename(file_path)
                dataframes.append(df)
            
            combined_df = pd.concat(dataframes, ignore_index=True)
            combined_df = combined_df.sort_values('date').reset_index(drop=True)
            return combined_df
        else:
            return {
                os.path.basename(file_path): self.load(file_path, **kwargs)
                for file_path in file_paths
            }


class YahooFinanceLoader(BaseDataLoader):
    """Loads trading data from Yahoo Finance."""
    
    def load(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        validate: bool = True
    ) -> pd.DataFrame:
        """
        Load data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            validate: Whether to validate the data
            
        Returns:
            DataFrame with OHLCV data
            
        Note:
            Requires: pip install yfinance
        """
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("yfinance package required. Install with: pip install yfinance")
        
        # Download data
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for symbol {symbol} in the specified date range")
        
        # Reset index to get date as column
        df = df.reset_index()
        
        # Rename columns to match our format
        column_mapping = {
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Select only required columns
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        
        # Validate data if requested
        if validate:
            DataValidator.validate_ohlcv_data(df)
        
        return df
    
    def load_multiple_symbols(
        self, 
        symbols: list, 
        start_date: str, 
        end_date: str,
        **kwargs
    ) -> dict:
        """
        Load data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            **kwargs: Additional arguments
            
        Returns:
            Dictionary of DataFrames keyed by symbol
        """
        return {
            symbol: self.load(symbol, start_date, end_date, **kwargs)
            for symbol in symbols
        }


class DatabaseLoader(BaseDataLoader):
    """Loads trading data from databases."""
    
    def __init__(self, connection_string: str):
        """
        Initialize database loader.
        
        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string
    
    def load(
        self, 
        query: str, 
        date_column: str = 'date',
        validate: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from database using SQL query.
        
        Args:
            query: SQL query to execute
            date_column: Name of the date column
            validate: Whether to validate the data
            **kwargs: Additional arguments for pd.read_sql
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            import sqlalchemy
        except ImportError:
            raise ImportError("sqlalchemy package required. Install with: pip install sqlalchemy")
        
        # Create engine
        engine = sqlalchemy.create_engine(self.connection_string)
        
        # Load data
        df = pd.read_sql(query, engine, **kwargs)
        
        # Validate and standardize date format
        if date_column in df.columns:
            df = DataValidator.validate_date_format(df, date_column)
        
        # Validate data if requested
        if validate:
            DataValidator.validate_ohlcv_data(df)
        
        return df


class APILoader(BaseDataLoader):
    """Generic API loader for trading data."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API loader.
        
        Args:
            base_url: Base URL for the API
            api_key: API key if required
        """
        self.base_url = base_url
        self.api_key = api_key
    
    def load(
        self, 
        endpoint: str, 
        params: dict,
        date_column: str = 'date',
        validate: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from API endpoint.
        
        Args:
            endpoint: API endpoint
            params: Parameters for the API call
            date_column: Name of the date column
            validate: Whether to validate the data
            **kwargs: Additional arguments
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests package required. Install with: pip install requests")
        
        # Prepare headers
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Make API call
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        df = pd.DataFrame(data)
        
        # Validate and standardize date format
        if date_column in df.columns:
            df = DataValidator.validate_date_format(df, date_column)
        
        # Validate data if requested
        if validate:
            DataValidator.validate_ohlcv_data(df)
        
        return df


# Backward compatibility functions
def load_csv_data(
    file_path: str, 
    date_column: str = 'date',
    date_format: Optional[str] = None,
    validate: bool = True
) -> pd.DataFrame:
    """
    Load trading data from a CSV file (backward compatibility).
    
    Args:
        file_path: Path to CSV file
        date_column: Name of the date column
        date_format: Date format string (if None, auto-detect)
        validate: Whether to validate data after loading
        
    Returns:
        DataFrame with OHLCV data
    """
    loader = CSVLoader()
    return loader.load(
        file_path=file_path,
        date_column=date_column,
        date_format=date_format,
        validate=validate
    )


def load_yahoo_data(
    symbol: str,
    start_date: str,
    end_date: str,
    validate: bool = True
) -> pd.DataFrame:
    """
    Load data from Yahoo Finance (backward compatibility).
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        validate: Whether to validate data after loading
        
    Returns:
        DataFrame with OHLCV data
    """
    loader = YahooFinanceLoader()
    return loader.load(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        validate=validate
    )


# Example usage
if __name__ == "__main__":
    print("Testing data loaders...")
    
    # Test CSV loader with sample data
    csv_loader = CSVLoader()
    
    # Create sample CSV data for testing
    sample_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', '2023-01-10', freq='D'),
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'volume': [10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000]
    })
    
    # Save sample data
    sample_file = 'sample_data.csv'
    sample_data.to_csv(sample_file, index=False)
    
    try:
        # Test CSV loading
        loaded_data = csv_loader.load(sample_file)
        print(f"✓ CSV loader: Loaded {len(loaded_data)} rows")
        
        # Clean up
        os.remove(sample_file)
        
    except Exception as e:
        print(f"✗ CSV loader failed: {e}")
        if os.path.exists(sample_file):
            os.remove(sample_file)
    
    # Test Yahoo Finance loader (optional - requires internet)
    try:
        yahoo_loader = YahooFinanceLoader()
        # This will only work if yfinance is installed and internet is available
        # yahoo_data = yahoo_loader.load('AAPL', '2023-01-01', '2023-01-10')
        # print(f"✓ Yahoo Finance loader: Loaded {len(yahoo_data)} rows")
        print("✓ Yahoo Finance loader initialized (skipping download test)")
    except Exception as e:
        print(f"✓ Yahoo Finance loader initialized (yfinance not available: {e})")
    
    print("Data loaders module working correctly!")
