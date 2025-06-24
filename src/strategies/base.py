"""
Base Strategy Class
==================

This module provides the base strategy class for all trading strategies.
"""

import backtrader as bt


class BaseStrategy(bt.Strategy):
    """
    Base class for all trading strategies.
    
    This class provides common functionality and enforces interface consistency
    across all strategy implementations.
    """
    
    params = ()
    
    def __init__(self):
        """Initialize the strategy."""
        super().__init__()
        self.trades = []
        self.trade_count = 0
        
    def log(self, txt, dt=None):
        """Logging function for this strategy."""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')
        
    def notify_trade(self, trade):
        """
        Receives trade notifications.
        
        Args:
            trade: Trade object containing trade information
        """
        if trade.isclosed:
            self.trade_count += 1
            self.trades.append({
                'date': self.datas[0].datetime.date(0),
                'price': trade.price,
                'pnl': trade.pnl,
                'pnlcomm': trade.pnlcomm,
                'size': trade.size
            })
            
    def next(self):
        """
        Define the main strategy logic.
        
        This method should be implemented by all concrete strategy classes.
        """
        raise NotImplementedError("Subclasses must implement the next() method")
        
    def get_trade_summary(self):
        """
        Returns a summary of all trades executed by the strategy.
        
        Returns:
            dict: Trade summary statistics
        """
        if not self.trades:
            return {'total_trades': 0, 'total_pnl': 0, 'avg_pnl': 0}
            
        total_pnl = sum(trade['pnlcomm'] for trade in self.trades)
        return {
            'total_trades': len(self.trades),
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(self.trades) if self.trades else 0,
            'winning_trades': len([t for t in self.trades if t['pnlcomm'] > 0]),
            'losing_trades': len([t for t in self.trades if t['pnlcomm'] < 0])
        }
