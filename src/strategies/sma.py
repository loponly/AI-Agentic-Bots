"""
Simple Moving Average Strategy
=============================

This module implements a Simple Moving Average crossover strategy.
"""

import backtrader as bt
from .base import BaseStrategy


class SimpleMovingAverageStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
    Buy when short MA crosses above long MA.
    Sell when short MA crosses below long MA.
    """
    
    params = (
        ('short_period', 10),
        ('long_period', 30),
        ('stop_loss', 0.05),  # 5% stop loss
        ('take_profit', 0.10),  # 10% take profit
    )
    
    def __init__(self):
        super().__init__()
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.long_period
        )
        
        # Crossover signal
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)
        
        # Order tracking
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        
    def notify_order(self, order):
        """Handle order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                
        self.order = None
        
    def next(self):
        """Main strategy logic executed on each bar."""
        if self.order:
            return
            
        if not self.position:
            # Buy signal: short MA crosses above long MA
            if self.crossover > 0:
                size = int(self.broker.getvalue() * 0.95 / self.data.close[0])
                self.order = self.buy(size=size)
                
        else:
            # Sell signals
            current_price = self.data.close[0]
            
            # Stop loss
            if current_price <= self.buy_price * (1 - self.params.stop_loss):
                self.order = self.sell()
                
            # Take profit
            elif current_price >= self.buy_price * (1 + self.params.take_profit):
                self.order = self.sell()
                
            # Exit signal: short MA crosses below long MA
            elif self.crossover < 0:
                self.order = self.sell()
