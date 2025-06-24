"""
Mean Reversion Strategy
======================

This module implements a mean reversion strategy.
"""

import backtrader as bt
from .base import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy.
    
    Buy when price is below moving average by a threshold.
    Sell when price returns to or above moving average.
    """
    
    params = (
        ('period', 20),
        ('threshold', 0.02),  # 2% deviation threshold
        ('stop_loss', 0.05),
        ('take_profit', 0.08),
    )
    
    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.period
        )
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
        sma_value = self.sma[0]
        
        if not self.position:
            # Buy signal: price is below SMA by threshold
            deviation = (sma_value - current_price) / sma_value
            if deviation >= self.params.threshold:
                size = int(self.broker.getvalue() * 0.95 / current_price)
                self.order = self.buy(size=size)
                
        else:
            # Stop loss
            if current_price <= self.buy_price * (1 - self.params.stop_loss):
                self.order = self.sell()
                
            # Take profit
            elif current_price >= self.buy_price * (1 + self.params.take_profit):
                self.order = self.sell()
                
            # Exit signal: price returns to or above SMA
            elif current_price >= sma_value:
                self.order = self.sell()
