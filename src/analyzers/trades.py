"""
Trade Analyzer
=============

This module implements trade analysis functionality.
"""

import backtrader as bt


class TradeAnalyzer(bt.Analyzer):
    """Custom analyzer to track individual trades."""
    
    def __init__(self):
        self.trades = []
        self.current_trade = None
        
    def notify_trade(self, trade):
        if trade.isclosed:
            trade_info = {
                'entry_date': trade.open_datetime().strftime('%Y-%m-%d'),
                'exit_date': trade.close_datetime().strftime('%Y-%m-%d'),
                'entry_price': trade.price,
                'exit_price': trade.price + trade.pnl / trade.size,
                'size': trade.size,
                'pnl': trade.pnl,
                'pnl_pct': trade.pnlcomm / abs(trade.price * trade.size) * 100,
                'trade_duration': (trade.close_datetime() - trade.open_datetime()).days
            }
            self.trades.append(trade_info)
            
    def get_analysis(self):
        """Return the analysis results."""
        return {
            'trades': self.trades,
            'total_trades': len(self.trades),
            'winning_trades': len([t for t in self.trades if t['pnl'] > 0]),
            'losing_trades': len([t for t in self.trades if t['pnl'] < 0]),
            'avg_pnl': sum(t['pnl'] for t in self.trades) / len(self.trades) if self.trades else 0
        }
