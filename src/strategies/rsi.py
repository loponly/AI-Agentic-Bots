"""
RSI Strategy
============

This module implements a Relative Strength Index (RSI) strategy.
"""

import backtrader as bt
from .base import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Strategy.
    
    Buy when RSI < 30 (oversold)
    Sell when RSI > 70 (overbought)
    """
    
    params = (
        ('rsi_period', 14),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )
    
    def __init__(self):
        super().__init__()
        self.rsi = bt.indicators.RSI(self.datas[0].close, period=self.params.rsi_period)
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
            # Buy signal: RSI < oversold threshold
            if self.rsi < self.params.rsi_oversold:
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
                
            # Exit signal: RSI > overbought threshold
            elif self.rsi > self.params.rsi_overbought:
                self.order = self.sell()
