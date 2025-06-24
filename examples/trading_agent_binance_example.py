#!/usr/bin/env python3
"""
Trading Agent with Binance Data Example
======================================

This script demonstrates how to use the Binance data provider with trading agents
for real-time decision making and backtesting.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data.providers import DataProvider
from data.loaders import BinanceLoader


class SimpleTradingAgent:
    """A simple trading agent that uses Binance data."""
    
    def __init__(self, data_provider: DataProvider, symbol: str = 'BTCUSDT'):
        """
        Initialize the trading agent.
        
        Args:
            data_provider: DataProvider instance
            symbol: Trading pair symbol
        """
        self.data_provider = data_provider
        self.symbol = symbol
        self.position = 0  # 0 = no position, 1 = long, -1 = short
        self.cash = 10000.0
        self.portfolio_value = self.cash
        self.trades = []
        
    def get_current_data(self, lookback_days: int = 30) -> pd.DataFrame:
        """Get recent market data."""
        feed = self.data_provider.load_binance(
            symbol=self.symbol,
            interval='1d',
            limit=lookback_days
        )
        return feed.data

    def calculate_indicators(self, data: pd.DataFrame, filter: bool = False) -> pd.DataFrame:
        """Calculate technical indicators."""
        df = data.copy()
        
        # Simple Moving Averages
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_30'] = df['close'].rolling(window=30).mean()

        # Filtering out by rolling means
        if filter:
            N = 20
            df['rolling_mean'] = df['close'].rolling(window=N).mean()
            df = df[df['close'] > df['rolling_mean']]
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate trading signal based on indicators."""
        if len(data) < 30:
            return 'HOLD'
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        signals = []
        
        # SMA Crossover Signal
        if latest['sma_10'] > latest['sma_30'] and prev['sma_10'] <= prev['sma_30']:
            signals.append('BUY')
        elif latest['sma_10'] < latest['sma_30'] and prev['sma_10'] >= prev['sma_30']:
            signals.append('SELL')
        
        # RSI Signal
        if latest['rsi'] < 30:  # Oversold
            signals.append('BUY')
        elif latest['rsi'] > 70:  # Overbought
            signals.append('SELL')
        
        # Bollinger Bands Signal
        if latest['close'] < latest['bb_lower']:  # Below lower band
            signals.append('BUY')
        elif latest['close'] > latest['bb_upper']:  # Above upper band
            signals.append('SELL')
        
        # Volume confirmation
        volume_surge = latest['volume_ratio'] > 1.5
        
        # Combine signals
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        
        if buy_signals >= 2 and volume_surge:
            return 'BUY'
        elif sell_signals >= 2 and volume_surge:
            return 'SELL'
        else:
            return 'HOLD'
    
    def execute_trade(self, signal: str, price: float):
        """Execute trade based on signal."""
        if signal == 'BUY' and self.position <= 0:
            # Buy signal
            shares = self.cash / price
            self.cash = 0
            self.position = shares
            self.trades.append({
                'type': 'BUY',
                'price': price,
                'shares': shares,
                'timestamp': datetime.now()
            })
            return f"BOUGHT {shares:.6f} {self.symbol.replace('USDT', '')} at ${price:.2f}"
        
        elif signal == 'SELL' and self.position > 0:
            # Sell signal
            self.cash = self.position * price
            sell_shares = self.position
            self.position = 0
            self.trades.append({
                'type': 'SELL',
                'price': price,
                'shares': sell_shares,
                'timestamp': datetime.now()
            })
            return f"SOLD {sell_shares:.6f} {self.symbol.replace('USDT', '')} at ${price:.2f}"
        
        return "NO TRADE"
    
    def get_portfolio_value(self, current_price: float) -> float:
        """Calculate current portfolio value."""
        return self.cash + (self.position * current_price)
    
    def backtest(self, days: int = 90) -> dict:
        """Run a backtest over historical data."""
        print(f"Running backtest for {days} days...")
        
        # Get historical data
        feed = self.data_provider.load_binance(
            symbol=self.symbol,
            interval='1d',
            limit=days
        )
        data = feed.data
        
        # Reset portfolio
        self.cash = 10000.0
        self.position = 0
        self.trades = []
        
        portfolio_values = []
        
        for i in range(30, len(data)):  # Start after 30 days for indicators
            # Get data up to current point
            current_data = data.iloc[:i+1].copy()
            current_data = self.calculate_indicators(current_data)
            
            # Generate signal
            signal = self.generate_signal(current_data)
            current_price = current_data.iloc[-1]['close']
            
            # Execute trade
            trade_result = self.execute_trade(signal, current_price)
            
            # Track portfolio value
            portfolio_value = self.get_portfolio_value(current_price)
            portfolio_values.append({
                'date': current_data.iloc[-1]['date'],
                'price': current_price,
                'signal': signal,
                'portfolio_value': portfolio_value,
                'position': self.position,
                'cash': self.cash
            })
        
        # Final portfolio value
        final_price = data.iloc[-1]['close']
        final_value = self.get_portfolio_value(final_price)
        
        # Calculate performance metrics
        initial_value = 10000.0
        total_return = ((final_value - initial_value) / initial_value) * 100
        
        # Buy and hold return
        bh_return = ((final_price - data.iloc[30]['close']) / data.iloc[30]['close']) * 100
        
        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'buy_hold_return': bh_return,
            'num_trades': len(self.trades),
            'trades': self.trades,
            'portfolio_history': portfolio_values
        }


def main():
    """Main function to demonstrate the trading agent with Binance data."""
    print("🤖 Trading Agent with Binance Data Example")
    print("=" * 60)
    
    # Initialize data provider
    provider = DataProvider()
    
    # Test 1: Current market analysis
    print("1. Current Market Analysis...")
    
    try:
        # Get current data
        btc_feed = provider.load_binance('BTCUSDT', interval='1d', limit=30)
        
        # Initialize agent
        agent = SimpleTradingAgent(provider, 'BTCUSDT')
        
        # Calculate indicators
        data_with_indicators = agent.calculate_indicators(btc_feed.data)
        
        # Get current signal
        signal = agent.generate_signal(data_with_indicators)
        current_price = data_with_indicators.iloc[-1]['close']
        
        print(f"✓ Current BTC price: ${current_price:,.2f}")
        print(f"✓ Trading signal: {signal}")
        
        # Display key indicators
        latest = data_with_indicators.iloc[-1]
        print(f"✓ RSI: {latest['rsi']:.2f}")
        print(f"✓ SMA 10: ${latest['sma_10']:,.2f}")
        print(f"✓ SMA 30: ${latest['sma_30']:,.2f}")
        print(f"✓ Bollinger Upper: ${latest['bb_upper']:,.2f}")
        print(f"✓ Bollinger Lower: ${latest['bb_lower']:,.2f}")
        
    except Exception as e:
        print(f"✗ Current analysis failed: {e}")
    
    # Test 2: Backtesting
    print(f"\n2. Running Backtest...")
    
    try:
        results = agent.backtest(days=90)
        
        print(f"✓ Backtest completed!")
        print(f"✓ Initial value: ${results['initial_value']:,.2f}")
        print(f"✓ Final value: ${results['final_value']:,.2f}")
        print(f"✓ Total return: {results['total_return']:.2f}%")
        print(f"✓ Buy & Hold return: {results['buy_hold_return']:.2f}%")
        print(f"✓ Number of trades: {results['num_trades']}")
        
        # Show recent trades
        if results['trades']:
            print(f"\n   Recent trades:")
            for trade in results['trades'][-3:]:  # Last 3 trades
                print(f"   - {trade['type']}: {trade['shares']:.6f} @ ${trade['price']:.2f}")
        
    except Exception as e:
        print(f"✗ Backtest failed: {e}")
    
    # Test 3: Multi-asset analysis
    print(f"\n3. Multi-Asset Analysis...")
    
    assets = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    
    for asset in assets:
        try:
            print(f"\n   Analyzing {asset}...")
            
            # Create agent for this asset
            asset_agent = SimpleTradingAgent(provider, asset)
            
            # Get data and signal
            feed = provider.load_binance(asset, interval='1d', limit=30)
            data_with_indicators = asset_agent.calculate_indicators(feed.data)
            signal = asset_agent.generate_signal(data_with_indicators)
            current_price = data_with_indicators.iloc[-1]['close']
            
            print(f"   ✓ Price: ${current_price:,.2f}")
            print(f"   ✓ Signal: {signal}")
            print(f"   ✓ RSI: {data_with_indicators.iloc[-1]['rsi']:.2f}")
            
        except Exception as e:
            print(f"   ✗ {asset} analysis failed: {e}")
    
    # Test 4: Different timeframes
    print(f"\n4. Timeframe Analysis (BTC/USDT)...")
    
    timeframes = [
        ('1h', 'Hourly'),
        ('4h', '4-Hour'),
        ('1d', 'Daily'),
        ('1w', 'Weekly')
    ]
    
    for interval, name in timeframes:
        try:
            print(f"\n   {name} analysis...")
            
            # Get data for this timeframe
            feed = provider.load_binance('BTCUSDT', interval=interval, limit=50)
            
            # Quick signal calculation
            data = feed.data
            data['sma_10'] = data['close'].rolling(window=10).mean()
            data['sma_20'] = data['close'].rolling(window=20).mean()
            
            latest = data.iloc[-1]
            trend = "BULLISH" if latest['sma_10'] > latest['sma_20'] else "BEARISH"
            
            print(f"   ✓ Price: ${latest['close']:,.2f}")
            print(f"   ✓ Trend: {trend}")
            print(f"   ✓ SMA10: ${latest['sma_10']:,.2f}")
            print(f"   ✓ SMA20: ${latest['sma_20']:,.2f}")
            
        except Exception as e:
            print(f"   ✗ {name} analysis failed: {e}")
    
    print(f"\n🎉 Trading Agent Example Complete!")
    print("\nKey features demonstrated:")
    print("✓ Real-time data fetching from Binance")
    print("✓ Technical indicator calculation")
    print("✓ Signal generation")
    print("✓ Backtesting capabilities")
    print("✓ Multi-asset analysis")
    print("✓ Multi-timeframe analysis")
    
    print("\nNext steps:")
    print("- Implement more sophisticated strategies")
    print("- Add risk management rules")
    print("- Include transaction costs")
    print("- Add paper trading mode")
    print("- Implement real-time alerts")


if __name__ == "__main__":
    main()
