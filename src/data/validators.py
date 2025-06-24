"""
Data Validation Module
=====================

Provides data validation and statistical analysis for trading data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any


class DataValidator:
    """Data validation utilities for trading data."""
    
    @staticmethod
    def validate_ohlcv_data(df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame contains required OHLCV columns and data integrity.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # Check required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for numeric columns
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column '{col}' must be numeric")
        
        # Check for NaN values
        if df[required_columns].isnull().any().any():
            raise ValueError("Data contains NaN values")
        
        # Check OHLC relationships
        invalid_ohlc = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )
        
        if invalid_ohlc.any():
            raise ValueError("Invalid OHLC relationships found (High < Low, etc.)")
        
        # Check for negative values
        if (df[['open', 'high', 'low', 'close', 'volume']] < 0).any().any():
            raise ValueError("Negative values found in price or volume data")
        
        return True
    
    @staticmethod
    def validate_date_format(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """
        Validate and standardize date format.
        
        Args:
            df: DataFrame with date column
            date_column: Name of the date column
            
        Returns:
            DataFrame with standardized date column
        """
        df = df.copy()
        
        if date_column not in df.columns:
            raise ValueError(f"Date column '{date_column}' not found")
        
        # Convert to datetime
        try:
            df[date_column] = pd.to_datetime(df[date_column])
        except Exception as e:
            raise ValueError(f"Cannot convert '{date_column}' to datetime: {e}")
        
        # Check for duplicate dates
        if df[date_column].duplicated().any():
            raise ValueError("Duplicate dates found in data")
        
        # Sort by date
        df = df.sort_values(date_column).reset_index(drop=True)
        
        return df
    
    @staticmethod
    def check_data_completeness(df: pd.DataFrame, date_column: str = 'date') -> Dict[str, Any]:
        """
        Check data completeness and identify gaps.
        
        Args:
            df: DataFrame with date column
            date_column: Name of the date column
            
        Returns:
            Dictionary with completeness information
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)
        
        start_date = df[date_column].min()
        end_date = df[date_column].max()
        total_days = (end_date - start_date).days + 1
        actual_rows = len(df)
        
        # Find gaps (assuming daily data)
        expected_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        missing_dates = expected_dates.difference(df[date_column])
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_expected_days': total_days,
            'actual_rows': actual_rows,
            'missing_dates': missing_dates.tolist(),
            'completeness_ratio': actual_rows / total_days,
            'gaps_count': len(missing_dates)
        }
    
    @staticmethod
    def get_data_statistics(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the trading data.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with data statistics
        """
        DataValidator.validate_ohlcv_data(df)
        
        # Calculate returns
        df = df.copy()
        df['returns'] = df['close'].pct_change()
        
        # Date range
        start_date = df['date'].min() if 'date' in df.columns else df.index.min()
        end_date = df['date'].max() if 'date' in df.columns else df.index.max()
        
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
            
        duration = (end_date - start_date).days
        
        # Price statistics
        price_stats = {
            'start_price': float(df['close'].iloc[0]),
            'end_price': float(df['close'].iloc[-1]),
            'min_price': float(df['low'].min()),
            'max_price': float(df['high'].max()),
            'avg_price': float(df['close'].mean()),
            'price_change': float(df['close'].iloc[-1] - df['close'].iloc[0]),
            'price_change_pct': float(((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100)
        }
        
        # Return statistics
        return_stats = {
            'avg_daily_return': float(df['returns'].mean() * 100),
            'daily_volatility': float(df['returns'].std() * 100),
            'annualized_return': float(df['returns'].mean() * 252 * 100),
            'annualized_volatility': float(df['returns'].std() * np.sqrt(252) * 100),
            'sharpe_ratio': float((df['returns'].mean() / df['returns'].std()) * np.sqrt(252)) if df['returns'].std() > 0 else 0,
            'max_daily_gain': float(df['returns'].max() * 100),
            'max_daily_loss': float(df['returns'].min() * 100)
        }
        
        # Volume statistics
        volume_stats = {
            'avg_volume': float(df['volume'].mean()),
            'min_volume': float(df['volume'].min()),
            'max_volume': float(df['volume'].max()),
            'volume_std': float(df['volume'].std())
        }
        
        return {
            'data_info': {
                'rows': len(df),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'duration_days': duration
            },
            'price_stats': price_stats,
            'return_stats': return_stats,
            'volume_stats': volume_stats
        }
    
    @staticmethod
    def detect_outliers(df: pd.DataFrame, method: str = 'iqr', threshold: float = 1.5) -> Dict[str, Any]:
        """
        Detect outliers in price and volume data.
        
        Args:
            df: DataFrame with OHLCV data
            method: Method to use ('iqr', 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Dictionary with outlier information
        """
        outliers = {}
        
        price_columns = ['open', 'high', 'low', 'close']
        
        for col in price_columns + ['volume']:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_mask = z_scores > threshold
            
            else:
                raise ValueError(f"Unknown method: {method}")
            
            outliers[col] = {
                'count': outlier_mask.sum(),
                'percentage': (outlier_mask.sum() / len(df)) * 100,
                'indices': df.index[outlier_mask].tolist()
            }
        
        return outliers
    
    @staticmethod
    def validate_price_continuity(df: pd.DataFrame, max_gap_pct: float = 10.0) -> Dict[str, Any]:
        """
        Check for unusual price gaps that might indicate data issues.
        
        Args:
            df: DataFrame with OHLCV data
            max_gap_pct: Maximum allowed price gap percentage
            
        Returns:
            Dictionary with gap analysis
        """
        df = df.copy()
        df = df.sort_values('date' if 'date' in df.columns else df.index)
        
        # Calculate price gaps
        df['prev_close'] = df['close'].shift(1)
        df['gap_pct'] = ((df['open'] - df['prev_close']) / df['prev_close'] * 100).abs()
        
        # Find large gaps
        large_gaps = df[df['gap_pct'] > max_gap_pct]
        
        return {
            'total_gaps': len(large_gaps),
            'max_gap_pct': float(df['gap_pct'].max()) if not df['gap_pct'].isna().all() else 0,
            'avg_gap_pct': float(df['gap_pct'].mean()) if not df['gap_pct'].isna().all() else 0,
            'large_gaps': large_gaps[['date', 'open', 'prev_close', 'gap_pct']].to_dict('records') if 'date' in df.columns else large_gaps[['open', 'prev_close', 'gap_pct']].to_dict('records')
        }


# Backward compatibility functions
def validate_ohlcv_data(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame contains required OHLCV columns and data integrity (backward compatibility).
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    return DataValidator.validate_ohlcv_data(df)


def is_trading_day(date: datetime) -> bool:
    """
    Check if a given date is a trading day (backward compatibility).
    
    Args:
        date: Date to check
        
    Returns:
        True if trading day, False otherwise
    """
    return DataValidator.is_trading_day(date)


def get_data_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get comprehensive statistics for trading data (backward compatibility).
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Dictionary with data statistics
    """
    return DataValidator.get_data_statistics(df)


# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    import numpy as np
    
    dates = pd.date_range('2023-01-01', '2023-01-10', freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(len(dates)) * 2,
        'high': 102 + np.random.randn(len(dates)) * 2,
        'low': 98 + np.random.randn(len(dates)) * 2,
        'close': 100 + np.random.randn(len(dates)) * 2,
        'volume': np.random.randint(10000, 100000, len(dates))
    })
    
    # Ensure OHLC relationships are valid
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    print("Testing data validation...")
    
    # Validate data
    try:
        DataValidator.validate_ohlcv_data(data)
        print("✓ Data validation passed")
    except ValueError as e:
        print(f"✗ Data validation failed: {e}")
    
    # Get statistics
    stats = DataValidator.get_data_statistics(data)
    print(f"✓ Data statistics: {stats['data_info']['rows']} rows")
    print(f"✓ Price change: {stats['price_stats']['price_change_pct']:.2f}%")
    
    # Check completeness
    completeness = DataValidator.check_data_completeness(data)
    print(f"✓ Data completeness: {completeness['completeness_ratio']:.2%}")
    
    print("Data validation module working correctly!")
