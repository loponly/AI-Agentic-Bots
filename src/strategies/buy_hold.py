"""
Buy and Hold Strategy
====================

This module implements a simple buy and hold strategy.
"""

import backtrader as bt
from .base import BaseStrategy


class BuyAndHoldStrategy(BaseStrategy):
    """
    Buy and Hold Strategy.
    
    Buy at the beginning and hold until the end.
    """
    
    params = ()
    
    def __init__(self):
        super().__init__()
        self.order = None
        self.bought = False
        
    def notify_order(self, order):
        """Handle order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.bought = True
                
        self.order = None
        
    def next(self):
        """Main strategy logic executed on each bar."""
        if self.order:
            return
            
        # Buy once at the beginning if we haven't bought yet
        if not self.position and not self.bought:
            # Use 95% of available cash
            size = int(self.broker.getvalue() * 0.95 / self.data.close[0])
            self.order = self.buy(size=size)
