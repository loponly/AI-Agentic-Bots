"""
Momentum Strategy
================

This module implements a momentum strategy.
"""

import backtrader as bt
from .base import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy.
    
    Buy when price momentum is positive (price > price N periods ago).
    Sell when momentum turns negative.
    """
    
    params = (
        ('period', 10),
        ('momentum_threshold', 0.02),  # 2% momentum threshold
        ('stop_loss', 0.05),
        ('take_profit', 0.12),
    )
    
    def __init__(self):
        super().__init__()
        self.momentum = self.data.close / self.data.close(-self.params.period) - 1.0
        self.order = None
        self.buy_price = None
        
    def notify_order(self, order):
        """Handle order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                
        self.order = None
        
    def next(self):
        """Main strategy logic executed on each bar."""
        if self.order:
            return
            
        current_price = self.data.close[0]
        momentum_value = self.momentum[0]
        
        if not self.position:
            # Buy signal: positive momentum above threshold
            if momentum_value > self.params.momentum_threshold:
                size = int(self.broker.getvalue() * 0.95 / current_price)
                self.order = self.buy(size=size)
                
        else:
            # Stop loss
            if current_price <= self.buy_price * (1 - self.params.stop_loss):
                self.order = self.sell()
                
            # Take profit
            elif current_price >= self.buy_price * (1 + self.params.take_profit):
                self.order = self.sell()
                
            # Exit signal: momentum turns negative
            elif momentum_value < 0:
                self.order = self.sell()
