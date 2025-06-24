"""
Performance Analyzer
===================

This module implements performance analysis functionality.
"""

import backtrader as bt


class PerformanceAnalyzer(bt.Analyzer):
    """Custom analyzer to calculate performance metrics."""
    
    def __init__(self):
        self.start_val = self.strategy.broker.getvalue()
        self.end_val = None
        
    def stop(self):
        self.end_val = self.strategy.broker.getvalue()
        
    def get_analysis(self):
        """Return the analysis results."""
        return {
            'start_value': self.start_val,
            'end_value': self.end_val,
            'total_return': self.end_val - self.start_val if self.end_val else 0,
            'total_return_pct': ((self.end_val / self.start_val - 1) * 100) if self.end_val and self.start_val else 0
        }
