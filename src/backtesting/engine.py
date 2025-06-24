"""
Backtesting Engine Module
========================

Core backtesting engine that orchestrates the backtesting process.
Decoupled from data feeding - receives data feeds and strategies as inputs.
"""

import backtrader as bt
from typing import Dict, Any, Optional, Type, List
from ..data.providers import DataFeed
from ..analyzers.performance import PerformanceAnalyzer
from ..analyzers.trades import TradeAnalyzer
from ..database.manager import DatabaseManager


class BacktestEngine:
    """
    Core backtesting engine that runs strategy backtests.
    Completely decoupled from data sources - accepts DataFeed objects.
    """
    
    def __init__(self, initial_cash: float = 100000.0, commission: float = 0.001):
        """
        Initialize the backtesting engine.
        
        Args:
            initial_cash: Starting cash amount
            commission: Commission rate (default 0.1%)
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.cerebro = None
        self.results = None
        
    def setup_cerebro(self) -> bt.Cerebro:
        """
        Set up the Cerebro engine with default configuration.
        
        Returns:
            Configured Cerebro instance
        """
        cerebro = bt.Cerebro()
        
        # Set initial cash
        cerebro.broker.setcash(self.initial_cash)
        
        # Set commission
        cerebro.broker.setcommission(commission=self.commission)
        
        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(PerformanceAnalyzer, _name='performance')
        cerebro.addanalyzer(TradeAnalyzer, _name='trade_list')
        
        return cerebro
    
    def add_data_feed(self, cerebro: bt.Cerebro, data_feed: DataFeed):
        """
        Add a data feed to the Cerebro engine.
        
        Args:
            cerebro: Cerebro instance
            data_feed: DataFeed object to add
        """
        bt_feed = data_feed.to_backtrader_feed()
        cerebro.adddata(bt_feed, name=data_feed.name)
    
    def add_strategy(
        self, 
        cerebro: bt.Cerebro, 
        strategy_class: Type[bt.Strategy], 
        strategy_params: Optional[Dict[str, Any]] = None
    ):
        """
        Add a strategy to the Cerebro engine.
        
        Args:
            cerebro: Cerebro instance
            strategy_class: Strategy class to add
            strategy_params: Parameters for the strategy
        """
        if strategy_params:
            cerebro.addstrategy(strategy_class, **strategy_params)
        else:
            cerebro.addstrategy(strategy_class)
    
    def run_backtest(
        self,
        data_feed: DataFeed,
        strategy_class: Type[bt.Strategy],
        strategy_params: Optional[Dict[str, Any]] = None,
        cerebro_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a complete backtest.
        
        Args:
            data_feed: DataFeed object containing the trading data
            strategy_class: Strategy class to test
            strategy_params: Parameters for the strategy
            cerebro_config: Additional Cerebro configuration
            
        Returns:
            Dictionary containing backtest results
        """
        # Setup Cerebro
        self.cerebro = self.setup_cerebro()
        
        # Apply additional configuration if provided
        if cerebro_config:
            for key, value in cerebro_config.items():
                if hasattr(self.cerebro, key):
                    setattr(self.cerebro, key, value)
        
        # Add data feed
        self.add_data_feed(self.cerebro, data_feed)
        
        # Add strategy
        self.add_strategy(self.cerebro, strategy_class, strategy_params)
        
        # Run backtest
        print(f"Starting Portfolio Value: ${self.initial_cash:,.2f}")
        self.results = self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        print(f"Final Portfolio Value: ${final_value:,.2f}")
        
        # Extract and process results
        return self._extract_results(data_feed, strategy_class, strategy_params)
    
    def run_multiple_backtests(
        self,
        test_configs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Run multiple backtests with different configurations.
        
        Args:
            test_configs: List of test configurations
                         Each config should contain: data_feed, strategy_class, strategy_params
                         
        Returns:
            List of backtest results
        """
        results = []
        
        for i, config in enumerate(test_configs):
            print(f"\nRunning backtest {i+1}/{len(test_configs)}...")
            
            result = self.run_backtest(
                data_feed=config['data_feed'],
                strategy_class=config['strategy_class'],
                strategy_params=config.get('strategy_params'),
                cerebro_config=config.get('cerebro_config')
            )
            
            results.append(result)
        
        return results
    
    def optimize_strategy(
        self,
        data_feed: DataFeed,
        strategy_class: Type[bt.Strategy],
        param_ranges: Dict[str, list],
        optimization_target: str = 'total_return_pct'
    ) -> Dict[str, Any]:
        """
        Optimize strategy parameters using grid search.
        
        Args:
            data_feed: DataFeed object
            strategy_class: Strategy class to optimize
            param_ranges: Dictionary of parameter ranges to test
            optimization_target: Metric to optimize for
            
        Returns:
            Dictionary with optimization results
        """
        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(param_ranges)
        
        best_result = None
        best_score = -float('inf')
        all_results = []
        
        print(f"Running optimization with {len(param_combinations)} parameter combinations...")
        
        for i, params in enumerate(param_combinations):
            print(f"Testing combination {i+1}/{len(param_combinations)}: {params}")
            
            result = self.run_backtest(
                data_feed=data_feed,
                strategy_class=strategy_class,
                strategy_params=params
            )
            
            all_results.append({
                'params': params,
                'result': result
            })
            
            # Check if this is the best result
            score = result.get(optimization_target, -float('inf'))
            if score > best_score:
                best_score = score
                best_result = {
                    'params': params,
                    'result': result
                }
        
        return {
            'best_result': best_result,
            'best_score': best_score,
            'all_results': all_results,
            'optimization_target': optimization_target
        }
    
    def _generate_param_combinations(self, param_ranges: Dict[str, list]) -> List[Dict[str, Any]]:
        """Generate all combinations of parameters."""
        import itertools
        
        keys = list(param_ranges.keys())
        values = list(param_ranges.values())
        
        combinations = []
        for value_combo in itertools.product(*values):
            combinations.append(dict(zip(keys, value_combo)))
        
        return combinations
    
    def _extract_results(
        self, 
        data_feed: DataFeed, 
        strategy_class: Type[bt.Strategy], 
        strategy_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract and format backtest results.
        
        Args:
            data_feed: DataFeed used in the backtest
            strategy_class: Strategy class used
            strategy_params: Strategy parameters used
            
        Returns:
            Formatted results dictionary
        """
        if not self.results:
            raise RuntimeError("No results available. Run backtest first.")
        
        strat = self.results[0]
        final_value = self.cerebro.broker.getvalue()
        
        # Get analyzer results
        sharpe_ratio = strat.analyzers.sharpe.get_analysis().get('sharperatio', None)
        drawdown = strat.analyzers.drawdown.get_analysis()
        trade_analysis = strat.analyzers.trades.get_analysis()
        returns_analysis = strat.analyzers.returns.get_analysis()
        trade_list = strat.analyzers.trade_list.trades
        
        # Calculate performance metrics
        total_return = final_value - self.initial_cash
        total_return_pct = (final_value / self.initial_cash - 1) * 100
        
        # Trade statistics
        total_trades = trade_analysis.get('total', {}).get('closed', 0)
        winning_trades = trade_analysis.get('won', {}).get('total', 0)
        losing_trades = trade_analysis.get('lost', {}).get('total', 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_trade_return = 0
        if total_trades > 0:
            avg_win = trade_analysis.get('won', {}).get('pnl', {}).get('average', 0)
            avg_loss = trade_analysis.get('lost', {}).get('pnl', {}).get('average', 0)
            avg_trade_return = (avg_win * winning_trades + avg_loss * losing_trades) / total_trades
        
        # Get data info
        data_stats = data_feed.get_statistics()
        
        # Compile results
        results_dict = {
            'strategy_name': strategy_class.__name__,
            'data_feed_name': data_feed.name,
            'start_date': data_stats['data_info']['start_date'],
            'end_date': data_stats['data_info']['end_date'],
            'initial_cash': self.initial_cash,
            'final_cash': final_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': drawdown.get('max', {}).get('moneydown', 0),
            'max_drawdown_pct': drawdown.get('max', {}).get('drawdown', 0),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_trade_return': avg_trade_return,
            'strategy_params': strategy_params or {},
            'data_info': data_stats['data_info'],
            'data_metadata': data_feed.metadata,
            'trades': trade_list,
            'commission': self.commission
        }
        
        return results_dict
    
    def save_results(
        self, 
        results: Dict[str, Any], 
        db_manager: Optional[DatabaseManager] = None
    ) -> Optional[int]:
        """
        Save backtest results to database.
        
        Args:
            results: Results dictionary
            db_manager: Database manager instance
            
        Returns:
            Database ID of saved results
        """
        if db_manager is None:
            db_manager = DatabaseManager()
        
        return db_manager.save_backtest_result(results)
    
    def get_cerebro(self) -> Optional[bt.Cerebro]:
        """Get the current Cerebro instance."""
        return self.cerebro
    
    def get_results(self) -> Optional[list]:
        """Get the current backtest results."""
        return self.results


def print_performance_summary(results: Dict[str, Any]):
    """
    Print a formatted performance summary.
    
    Args:
        results: Backtest results dictionary
    """
    print("\n" + "="*60)
    print(f"BACKTEST PERFORMANCE SUMMARY - {results['strategy_name']}")
    print("="*60)
    
    print(f"Period: {results['start_date']} to {results['end_date']}")
    print(f"Initial Cash: ${results['initial_cash']:,.2f}")
    print(f"Final Cash: ${results['final_cash']:,.2f}")
    print(f"Total Return: ${results['total_return']:,.2f} ({results['total_return_pct']:.2f}%)")
    
    if results['sharpe_ratio']:
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
    
    print(f"Max Drawdown: ${results['max_drawdown']:,.2f} ({results['max_drawdown_pct']:.2f}%)")
    
    print(f"\nTrade Statistics:")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Winning Trades: {results['winning_trades']}")
    print(f"Losing Trades: {results['losing_trades']}")
    print(f"Win Rate: {results['win_rate']:.2f}%")
    print(f"Average Trade Return: ${results['avg_trade_return']:.2f}")
    
    if results.get('strategy_params'):
        print(f"\nStrategy Parameters:")
        for param, value in results['strategy_params'].items():
            print(f"  {param}: {value}")
    
    print("="*60)


# Example usage
if __name__ == "__main__":
    from ..data.providers import DataProvider
    from ..strategies.base import SimpleMovingAverageStrategy
    
    print("Testing backtesting engine...")
    
    # Initialize components
    data_provider = DataProvider()
    engine = BacktestEngine(initial_cash=100000)
    
    # Generate test data
    data_feed = data_provider.generate_synthetic(
        start_date='2023-01-01',
        end_date='2023-03-31',
        seed=42
    )
    
    print(f"Created data feed: {data_feed.name} with {len(data_feed.data)} rows")
    
    # Run backtest
    results = engine.run_backtest(
        data_feed=data_feed,
        strategy_class=SimpleMovingAverageStrategy,
        strategy_params={'short_period': 10, 'long_period': 30}
    )
    
    print(f"✓ Backtest completed: {results['total_return_pct']:.2f}% return")
    print("Backtesting engine working correctly!")
