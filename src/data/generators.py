"""
Synthetic Data Generator Module
==============================

Generates synthetic trading data for testing and research purposes.
"""

import pandas as pd
import numpy as np
from typing import Optional
from .validators import DataValidator


class SyntheticDataGenerator:
    """Generates synthetic OHLCV trading data."""
    
    def generate(
        self,
        start_date: str = '2020-01-01',
        end_date: str = '2023-12-31',
        initial_price: float = 100.0,
        volatility: float = 0.02,
        drift: float = 0.0005,
        seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate synthetic OHLCV data using geometric Brownian motion.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            initial_price: Starting price
            volatility: Daily volatility (standard deviation of returns)
            drift: Daily drift (mean return)
            seed: Random seed for reproducibility
            
        Returns:
            DataFrame with synthetic OHLCV data
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Generate date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate price series using geometric Brownian motion
        returns = np.random.normal(drift, volatility, len(dates))
        prices = [initial_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 0.01))  # Prevent negative prices
        
        # Generate OHLCV data
        data = []
        for i, (date, close_price) in enumerate(zip(dates, prices)):
            # Generate intraday volatility
            intraday_vol = volatility * 0.3
            
            # Generate open price (based on previous close + gap)
            if i == 0:
                open_price = close_price
            else:
                gap = np.random.normal(0, intraday_vol * 0.5)
                open_price = max(prices[i-1] * (1 + gap), 0.01)
            
            # Generate high and low
            high_factor = 1 + abs(np.random.normal(0, intraday_vol))
            low_factor = 1 - abs(np.random.normal(0, intraday_vol))
            
            high_price = max(open_price, close_price) * high_factor
            low_price = min(open_price, close_price) * low_factor
            
            # Ensure OHLC relationships are valid
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Generate volume (log-normal distribution)
            volume = int(np.random.lognormal(mean=11, sigma=0.5))  # Around 100k average
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        
        # Validate the generated data
        DataValidator.validate_ohlcv_data(df)
        
        return df
    
    def generate_trending_data(
        self,
        start_date: str = '2020-01-01',
        end_date: str = '2023-12-31',
        initial_price: float = 100.0,
        trend_strength: float = 0.001,
        volatility: float = 0.02,
        seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate trending data with a specific directional bias.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            initial_price: Starting price
            trend_strength: Strength of the trend (positive for uptrend, negative for downtrend)
            volatility: Daily volatility
            seed: Random seed for reproducibility
            
        Returns:
            DataFrame with trending synthetic data
        """
        return self.generate(
            start_date=start_date,
            end_date=end_date,
            initial_price=initial_price,
            volatility=volatility,
            drift=trend_strength,
            seed=seed
        )
    
    def generate_volatile_data(
        self,
        start_date: str = '2020-01-01',
        end_date: str = '2023-12-31',
        initial_price: float = 100.0,
        volatility: float = 0.05,
        seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate highly volatile data for stress testing.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            initial_price: Starting price
            volatility: High volatility level
            seed: Random seed for reproducibility
            
        Returns:
            DataFrame with volatile synthetic data
        """
        return self.generate(
            start_date=start_date,
            end_date=end_date,
            initial_price=initial_price,
            volatility=volatility,
            drift=0.0,
            seed=seed
        )
    
    def generate_mean_reverting_data(
        self,
        start_date: str = '2020-01-01',
        end_date: str = '2023-12-31',
        initial_price: float = 100.0,
        mean_reversion_speed: float = 0.1,
        volatility: float = 0.02,
        seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate mean-reverting data using Ornstein-Uhlenbeck process.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            initial_price: Starting price
            mean_reversion_speed: Speed of mean reversion
            volatility: Daily volatility
            seed: Random seed for reproducibility
            
        Returns:
            DataFrame with mean-reverting synthetic data
        """
        if seed is not None:
            np.random.seed(seed)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate mean-reverting price series
        prices = [initial_price]
        long_term_mean = initial_price
        
        for i in range(1, len(dates)):
            # Ornstein-Uhlenbeck process
            dt = 1.0  # Daily timestep
            current_price = prices[-1]
            
            # Mean reversion component
            drift_component = mean_reversion_speed * (long_term_mean - current_price) * dt
            
            # Random component
            random_component = volatility * np.sqrt(dt) * np.random.normal()
            
            # Calculate new price
            new_price = current_price + drift_component + current_price * random_component
            new_price = max(new_price, 0.01)  # Prevent negative prices
            
            prices.append(new_price)
        
        # Generate OHLCV data using the same logic as the main generator
        return self._generate_ohlcv_from_closes(dates, prices, volatility)
    
    def generate_regime_switching_data(
        self,
        start_date: str = '2020-01-01',
        end_date: str = '2023-12-31',
        initial_price: float = 100.0,
        regimes: list = None,
        seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate data with regime switching (alternating bull/bear markets).
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            initial_price: Starting price
            regimes: List of regime parameters [(duration_days, drift, volatility), ...]
            seed: Random seed for reproducibility
            
        Returns:
            DataFrame with regime-switching synthetic data
        """
        if seed is not None:
            np.random.seed(seed)
        
        if regimes is None:
            # Default regime configuration
            regimes = [
                (250, 0.001, 0.015),   # Bull market: 1 year, positive drift, low volatility
                (120, -0.002, 0.035),  # Bear market: 4 months, negative drift, high volatility
                (180, 0.0005, 0.02),   # Sideways: 6 months, neutral drift, medium volatility
            ]
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        prices = [initial_price]
        
        current_regime = 0
        days_in_regime = 0
        
        for i in range(1, len(dates)):
            # Check if we need to switch regimes
            if days_in_regime >= regimes[current_regime][0]:
                current_regime = (current_regime + 1) % len(regimes)
                days_in_regime = 0
            
            # Get current regime parameters
            _, drift, volatility = regimes[current_regime]
            
            # Generate return for current regime
            ret = np.random.normal(drift, volatility)
            new_price = prices[-1] * (1 + ret)
            new_price = max(new_price, 0.01)
            
            prices.append(new_price)
            days_in_regime += 1
        
        return self._generate_ohlcv_from_closes(dates, prices, 0.02)
    
    def _generate_ohlcv_from_closes(
        self, 
        dates: pd.DatetimeIndex, 
        close_prices: list, 
        base_volatility: float = 0.02
    ) -> pd.DataFrame:
        """
        Generate OHLCV data from a series of close prices.
        
        Args:
            dates: Date index
            close_prices: List of close prices
            base_volatility: Base volatility for intraday movements
            
        Returns:
            DataFrame with OHLCV data
        """
        data = []
        
        for i, (date, close_price) in enumerate(zip(dates, close_prices)):
            intraday_vol = base_volatility * 0.3
            
            # Generate open price
            if i == 0:
                open_price = close_price
            else:
                gap = np.random.normal(0, intraday_vol * 0.5)
                open_price = max(close_prices[i-1] * (1 + gap), 0.01)
            
            # Generate high and low
            high_factor = 1 + abs(np.random.normal(0, intraday_vol))
            low_factor = 1 - abs(np.random.normal(0, intraday_vol))
            
            high_price = max(open_price, close_price) * high_factor
            low_price = min(open_price, close_price) * low_factor
            
            # Ensure OHLC relationships
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Generate volume
            volume = int(np.random.lognormal(mean=11, sigma=0.5))
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        DataValidator.validate_ohlcv_data(df)
        return df


# Backward compatibility functions
def generate_synthetic_data(
    start_date: str = '2020-01-01',
    end_date: str = '2023-12-31',
    initial_price: float = 100.0,
    volatility: float = 0.02,
    drift: float = 0.0005,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data for testing purposes (backward compatibility function).
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        initial_price: Starting price
        volatility: Daily volatility (standard deviation of returns)
        drift: Daily drift (mean return)
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with synthetic OHLCV data
    """
    generator = SyntheticDataGenerator()
    return generator.generate(
        start_date=start_date,
        end_date=end_date,
        initial_price=initial_price,
        volatility=volatility,
        drift=drift,
        seed=seed
    )


def generate_random_walk(
    start_date: str = '2020-01-01', 
    end_date: str = '2023-12-31',
    initial_price: float = 100.0,
    step_size: float = 1.0,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate random walk price data (backward compatibility function).
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        initial_price: Starting price
        step_size: Maximum step size for random walk
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with random walk OHLCV data
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate random walk prices
    prices = [initial_price]
    for _ in range(len(dates) - 1):
        step = np.random.uniform(-step_size, step_size)
        new_price = max(prices[-1] + step, 0.01)  # Prevent negative prices
        prices.append(new_price)
    
    # Create OHLCV data
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # Generate random OHLC around the close price
        noise = np.random.normal(0, 0.5, 3)
        high = price + abs(noise[0])
        low = price - abs(noise[1])
        open_price = price + noise[2]
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': np.random.randint(100000, 1000000)
        })
    
    df = pd.DataFrame(data)
    
    # Validate data
    validator = DataValidator()
    if not validator.validate_ohlcv(df):
        raise ValueError("Generated data failed validation")
    
    return df


# Example usage
if __name__ == "__main__":
    print("Testing synthetic data generator...")
    
    generator = SyntheticDataGenerator()
    
    # Test basic generation
    data = generator.generate(
        start_date='2023-01-01',
        end_date='2023-01-10',
        initial_price=100,
        seed=42
    )
    
    print(f"✓ Basic generation: {len(data)} rows")
    print(f"  Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
    
    # Test trending data
    trending_data = generator.generate_trending_data(
        start_date='2023-01-01',
        end_date='2023-01-10',
        trend_strength=0.01,
        seed=42
    )
    
    print(f"✓ Trending data: {len(trending_data)} rows")
    trend_return = (trending_data['close'].iloc[-1] / trending_data['close'].iloc[0] - 1) * 100
    print(f"  Total trend return: {trend_return:.2f}%")
    
    # Test volatile data
    volatile_data = generator.generate_volatile_data(
        start_date='2023-01-01',
        end_date='2023-01-10',
        volatility=0.05,
        seed=42
    )
    
    print(f"✓ Volatile data: {len(volatile_data)} rows")
    daily_returns = volatile_data['close'].pct_change().dropna()
    volatility = daily_returns.std() * 100
    print(f"  Daily volatility: {volatility:.2f}%")
    
    print("Synthetic data generator working correctly!")
