"""
Bollinger Bands Strategy
========================

This module implements a Bollinger Bands strategy.
"""

import backtrader as bt
from .base import BaseStrategy


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Strategy.
    
    Buy when price touches lower band.
    Sell when price touches upper band.
    """
    
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )
    
    def __init__(self):
        super().__init__()
        self.bbands = bt.indicators.BollingerBands(
            self.datas[0].close,
            period=self.params.period,
            devfactor=self.params.devfactor
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
            
        if not self.position:
            # Buy signal: price touches lower band
            if self.data.close[0] <= self.bbands.lines.bot[0]:
                size = int(self.broker.getvalue() * 0.95 / self.data.close[0])
                self.order = self.buy(size=size)
                
        else:
            current_price = self.data.close[0]
            
            # Stop loss
            if current_price <= self.buy_price * (1 - self.params.stop_loss):
                self.order = self.sell()
                
            # Take profit
            elif current_price >= self.buy_price * (1 + self.params.take_profit):
                self.order = self.sell()
                
            # Exit signal: price touches upper band
            elif self.data.close[0] >= self.bbands.lines.top[0]:
                self.order = self.sell()
