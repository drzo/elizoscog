"""
Modular Strategy Engine with Historical Data Replay

This module provides a comprehensive, plug-and-play trading strategy engine
with historical data replay capabilities for backtesting and validation.
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import math
import statistics
from pathlib import Path

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Types of trading strategies"""
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    PAIRS_TRADING = "pairs_trading"
    RISK_PARITY = "risk_parity"
    MACHINE_LEARNING = "machine_learning"
    HYBRID = "hybrid"


class SignalStrength(Enum):
    """Signal strength indicators"""
    VERY_WEAK = 0.1
    WEAK = 0.3
    MODERATE = 0.5
    STRONG = 0.7
    VERY_STRONG = 0.9


@dataclass
class HistoricalDataPoint:
    """Single historical data point for replay"""
    timestamp: datetime
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    adjusted_close: Optional[float] = None
    dividends: Optional[float] = 0.0
    splits: Optional[float] = 1.0


@dataclass
class TradingSignal:
    """Enhanced trading signal with detailed information"""
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    strength: SignalStrength
    confidence: float
    timestamp: datetime
    strategy_id: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[float] = None
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyPerformanceMetrics:
    """Comprehensive strategy performance metrics"""
    strategy_id: str
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_trade_duration: timedelta
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional Value at Risk 95%


@runtime_checkable
class TradingStrategy(Protocol):
    """Protocol for plug-and-play trading strategies"""
    
    @property
    def strategy_id(self) -> str:
        """Unique strategy identifier"""
        ...
    
    @property
    def strategy_name(self) -> str:
        """Human-readable strategy name"""
        ...
    
    @property
    def strategy_type(self) -> StrategyType:
        """Strategy type classification"""
        ...
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Strategy parameters"""
        ...
    
    async def generate_signals(self, historical_data: List[HistoricalDataPoint]) -> List[TradingSignal]:
        """Generate trading signals from historical data"""
        ...
    
    async def update_parameters(self, new_parameters: Dict[str, Any]) -> None:
        """Update strategy parameters"""
        ...
    
    def get_required_data_history(self) -> int:
        """Get minimum required data points for strategy"""
        ...


class HistoricalDataReplay:
    """Historical data replay engine for backtesting"""
    
    def __init__(self, data_source: Optional[str] = None):
        self.data_source = data_source or "mock"
        self.data_cache: Dict[str, List[HistoricalDataPoint]] = {}
        self.replay_position: Dict[str, int] = {}
        
    async def load_historical_data(self, symbols: List[str], 
                                 start_date: datetime, 
                                 end_date: datetime,
                                 interval: str = "1d") -> Dict[str, List[HistoricalDataPoint]]:
        """Load historical data for specified symbols and date range"""
        
        historical_data = {}
        
        for symbol in symbols:
            if self.data_source == "mock":
                # Generate mock historical data
                data_points = self._generate_mock_data(symbol, start_date, end_date, interval)
            else:
                # In production, load from real data sources
                data_points = await self._fetch_real_data(symbol, start_date, end_date, interval)
            
            historical_data[symbol] = data_points
            self.data_cache[symbol] = data_points
            self.replay_position[symbol] = 0
        
        logger.info(f"Loaded historical data for {len(symbols)} symbols from {start_date} to {end_date}")
        return historical_data
    
    def _generate_mock_data(self, symbol: str, start_date: datetime, 
                           end_date: datetime, interval: str) -> List[HistoricalDataPoint]:
        """Generate realistic mock historical data"""
        
        # Create date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic price movements
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        # Base parameters by symbol type
        if symbol in ['SPY', 'QQQ', 'VTI']:
            base_price = 400.0
            volatility = 0.15
            drift = 0.08 / 252  # 8% annual return
        elif symbol in ['AAPL', 'MSFT', 'GOOGL']:
            base_price = 150.0
            volatility = 0.25
            drift = 0.12 / 252  # 12% annual return
        else:
            base_price = 100.0
            volatility = 0.20
            drift = 0.10 / 252  # 10% annual return
        
        data_points = []
        current_price = base_price
        
        for date in dates:
            # Generate daily return using geometric Brownian motion
            daily_return = np.random.normal(drift, volatility / np.sqrt(252))
            current_price *= (1 + daily_return)
            
            # Generate intraday high/low
            high_factor = 1 + abs(np.random.normal(0, 0.01))
            low_factor = 1 - abs(np.random.normal(0, 0.01))
            
            high_price = current_price * high_factor
            low_price = current_price * low_factor
            open_price = current_price * (1 + np.random.normal(0, 0.005))
            
            # Generate volume
            base_volume = 1000000
            volume_variation = np.random.lognormal(0, 0.5)
            volume = int(base_volume * volume_variation)
            
            data_point = HistoricalDataPoint(
                timestamp=date,
                symbol=symbol,
                open_price=open_price,
                high_price=max(high_price, open_price, current_price),
                low_price=min(low_price, open_price, current_price),
                close_price=current_price,
                volume=volume,
                adjusted_close=current_price,
                dividends=0.01 if np.random.random() < 0.1 else 0.0,  # 10% chance of dividend
                splits=1.0
            )
            
            data_points.append(data_point)
        
        return data_points
    
    async def _fetch_real_data(self, symbol: str, start_date: datetime,
                              end_date: datetime, interval: str) -> List[HistoricalDataPoint]:
        """Fetch real historical data from external sources"""
        # Placeholder for real data fetching (Yahoo Finance, Alpha Vantage, etc.)
        return self._generate_mock_data(symbol, start_date, end_date, interval)
    
    async def replay_data_stream(self, symbols: List[str], 
                               callback: callable,
                               speed_multiplier: float = 1.0) -> None:
        """Replay historical data as a real-time stream"""
        
        if not self.data_cache:
            raise ValueError("No historical data loaded. Call load_historical_data first.")
        
        # Find the minimum data length across all symbols
        min_length = min(len(self.data_cache[symbol]) for symbol in symbols)
        
        for i in range(min_length):
            # Get current data points for all symbols
            current_data = {}
            for symbol in symbols:
                current_data[symbol] = self.data_cache[symbol][i]
                self.replay_position[symbol] = i
            
            # Call the callback with current data
            await callback(current_data)
            
            # Control replay speed
            if speed_multiplier < float('inf'):
                await asyncio.sleep(1.0 / speed_multiplier)
    
    def get_data_slice(self, symbol: str, start_index: int, end_index: int) -> List[HistoricalDataPoint]:
        """Get a slice of historical data for a symbol"""
        if symbol not in self.data_cache:
            return []
        
        return self.data_cache[symbol][start_index:end_index]
    
    def get_current_position(self, symbol: str) -> int:
        """Get current replay position for a symbol"""
        return self.replay_position.get(symbol, 0)


class ModularStrategyEngine:
    """Comprehensive modular strategy engine with plug-and-play capabilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.strategies: Dict[str, TradingStrategy] = {}
        self.historical_replay = HistoricalDataReplay()
        self.performance_metrics: Dict[str, StrategyPerformanceMetrics] = {}
        self.active_signals: Dict[str, List[TradingSignal]] = {}
        
        # Initialize built-in strategies
        self._initialize_builtin_strategies()
    
    def _initialize_builtin_strategies(self) -> None:
        """Initialize built-in trading strategies"""
        
        # Mean Reversion Strategy
        self.register_strategy(MeanReversionStrategy())
        
        # Momentum Strategy  
        self.register_strategy(MomentumStrategy())
        
        # Pairs Trading Strategy
        self.register_strategy(PairsTradingStrategy())
        
        # Risk Parity Strategy
        self.register_strategy(RiskParityStrategy())
    
    def register_strategy(self, strategy: TradingStrategy) -> None:
        """Register a new trading strategy"""
        self.strategies[strategy.strategy_id] = strategy
        logger.info(f"Registered strategy: {strategy.strategy_name} ({strategy.strategy_id})")
    
    def unregister_strategy(self, strategy_id: str) -> None:
        """Unregister a trading strategy"""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            logger.info(f"Unregistered strategy: {strategy_id}")
    
    def list_strategies(self) -> List[Dict[str, Any]]:
        """List all registered strategies"""
        return [
            {
                'strategy_id': strategy.strategy_id,
                'strategy_name': strategy.strategy_name,
                'strategy_type': strategy.strategy_type.value,
                'parameters': strategy.parameters
            }
            for strategy in self.strategies.values()
        ]
    
    async def backtest_strategy(self, strategy_id: str, symbols: List[str],
                               start_date: datetime, end_date: datetime,
                               initial_capital: float = 100000.0,
                               transaction_cost: float = 0.001) -> StrategyPerformanceMetrics:
        """Comprehensive backtesting of a strategy"""
        
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        strategy = self.strategies[strategy_id]
        
        # Load historical data
        historical_data = await self.historical_replay.load_historical_data(
            symbols, start_date, end_date
        )
        
        # Initialize portfolio
        portfolio = BacktestPortfolio(initial_capital, transaction_cost)
        
        # Get all historical data points
        all_data_points = []
        for symbol_data in historical_data.values():
            all_data_points.extend(symbol_data)
        
        # Sort by timestamp
        all_data_points.sort(key=lambda x: x.timestamp)
        
        # Group by timestamp for synchronous processing
        data_by_timestamp = {}
        for data_point in all_data_points:
            timestamp = data_point.timestamp
            if timestamp not in data_by_timestamp:
                data_by_timestamp[timestamp] = []
            data_by_timestamp[timestamp].append(data_point)
        
        trades = []
        daily_returns = []
        equity_curve = []
        
        # Required history for strategy
        required_history = strategy.get_required_data_history()
        
        # Process each timestamp
        sorted_timestamps = sorted(data_by_timestamp.keys())
        for i, timestamp in enumerate(sorted_timestamps):
            current_data = data_by_timestamp[timestamp]
            
            # Skip if not enough historical data
            if i < required_history:
                equity_curve.append(portfolio.total_value)
                continue
            
            # Get historical context
            historical_context = []
            for j in range(max(0, i - required_history), i + 1):
                historical_context.extend(data_by_timestamp[sorted_timestamps[j]])
            
            # Generate signals
            signals = await strategy.generate_signals(historical_context)
            
            # Execute trades based on signals
            for signal in signals:
                trade = await portfolio.execute_signal(signal, current_data)
                if trade:
                    trades.append(trade)
            
            # Update portfolio value
            portfolio.update_portfolio_value(current_data)
            equity_curve.append(portfolio.total_value)
            
            # Calculate daily return
            if len(equity_curve) > 1:
                daily_return = (equity_curve[-1] - equity_curve[-2]) / equity_curve[-2]
                daily_returns.append(daily_return)
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(
            strategy_id, equity_curve, daily_returns, trades, start_date, end_date
        )
        
        self.performance_metrics[strategy_id] = metrics
        logger.info(f"Backtest completed for {strategy_id}: {metrics.total_return:.2%} return")
        
        return metrics
    
    def _calculate_performance_metrics(self, strategy_id: str, equity_curve: List[float],
                                     daily_returns: List[float], trades: List[Dict],
                                     start_date: datetime, end_date: datetime) -> StrategyPerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        if not equity_curve or not daily_returns:
            # Return minimal metrics if no data
            return StrategyPerformanceMetrics(
                strategy_id=strategy_id,
                total_return=0.0,
                annualized_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                max_drawdown=0.0,
                calmar_ratio=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                avg_trade_duration=timedelta(0),
                var_95=0.0,
                cvar_95=0.0
            )
        
        # Basic returns
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        
        # Annualized return
        days = (end_date - start_date).days
        years = days / 365.25
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0
        
        # Volatility (annualized)
        volatility = np.std(daily_returns) * np.sqrt(252) if daily_returns else 0.0
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0.0
        
        # Sortino ratio
        negative_returns = [r for r in daily_returns if r < 0]
        downside_deviation = np.std(negative_returns) * np.sqrt(252) if negative_returns else 0.0
        sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0.0
        
        # Maximum drawdown
        running_max = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - running_max) / running_max
        max_drawdown = abs(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0
        
        # Calmar ratio
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0.0
        
        # Trade statistics
        winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
        losing_trades = sum(1 for trade in trades if trade.get('pnl', 0) < 0)
        total_trades = len(trades)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        # Profit factor
        gross_profit = sum(trade.get('pnl', 0) for trade in trades if trade.get('pnl', 0) > 0)
        gross_loss = sum(abs(trade.get('pnl', 0)) for trade in trades if trade.get('pnl', 0) < 0)
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        
        # Average win/loss
        avg_win = gross_profit / winning_trades if winning_trades > 0 else 0.0
        avg_loss = -gross_loss / losing_trades if losing_trades > 0 else 0.0
        
        # Average trade duration
        trade_durations = [trade.get('duration', timedelta(0)) for trade in trades]
        avg_trade_duration = sum(trade_durations, timedelta(0)) / len(trade_durations) if trade_durations else timedelta(0)
        
        # Value at Risk (VaR) and Conditional VaR (CVaR)
        if daily_returns:
            var_95 = np.percentile(daily_returns, 5)
            cvar_95 = np.mean([r for r in daily_returns if r <= var_95])
        else:
            var_95 = 0.0
            cvar_95 = 0.0
        
        return StrategyPerformanceMetrics(
            strategy_id=strategy_id,
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_trade_duration=avg_trade_duration,
            var_95=var_95,
            cvar_95=cvar_95
        )
    
    async def run_strategy_comparison(self, strategy_ids: List[str], symbols: List[str],
                                    start_date: datetime, end_date: datetime) -> Dict[str, StrategyPerformanceMetrics]:
        """Run comparative analysis of multiple strategies"""
        
        results = {}
        
        for strategy_id in strategy_ids:
            if strategy_id in self.strategies:
                try:
                    metrics = await self.backtest_strategy(strategy_id, symbols, start_date, end_date)
                    results[strategy_id] = metrics
                except Exception as e:
                    logger.error(f"Error backtesting strategy {strategy_id}: {e}")
                    continue
        
        # Log comparison summary
        if results:
            best_strategy = max(results.keys(), key=lambda k: results[k].sharpe_ratio)
            logger.info(f"Strategy comparison complete. Best performing: {best_strategy}")
        
        return results


class BacktestPortfolio:
    """Portfolio management for backtesting"""
    
    def __init__(self, initial_capital: float, transaction_cost: float = 0.001):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}  # symbol -> position info
        self.transaction_cost = transaction_cost
        self.total_value = initial_capital
        
    async def execute_signal(self, signal: TradingSignal, 
                           current_data: List[HistoricalDataPoint]) -> Optional[Dict[str, Any]]:
        """Execute a trading signal"""
        
        # Find current price for the symbol
        current_price = None
        for data_point in current_data:
            if data_point.symbol == signal.symbol:
                current_price = data_point.close_price
                break
        
        if current_price is None:
            return None
        
        trade = None
        
        if signal.signal_type == 'BUY':
            trade = await self._execute_buy(signal, current_price)
        elif signal.signal_type == 'SELL':
            trade = await self._execute_sell(signal, current_price)
        # HOLD signals don't generate trades
        
        return trade
    
    async def _execute_buy(self, signal: TradingSignal, price: float) -> Optional[Dict[str, Any]]:
        """Execute a buy order"""
        
        # Determine position size (default to 10% of portfolio or signal specification)
        if signal.position_size:
            position_value = self.total_value * signal.position_size
        else:
            position_value = self.total_value * 0.1  # 10% default
        
        # Check if we have enough cash
        total_cost = position_value * (1 + self.transaction_cost)
        if total_cost > self.cash:
            return None  # Insufficient funds
        
        shares = position_value // price
        if shares <= 0:
            return None
        
        actual_cost = shares * price * (1 + self.transaction_cost)
        
        # Update portfolio
        self.cash -= actual_cost
        
        if signal.symbol in self.positions:
            self.positions[signal.symbol]['shares'] += shares
            # Update average cost basis
            old_value = self.positions[signal.symbol]['shares'] * self.positions[signal.symbol]['avg_price']
            new_value = shares * price
            total_shares = self.positions[signal.symbol]['shares']
            self.positions[signal.symbol]['avg_price'] = (old_value + new_value) / total_shares
        else:
            self.positions[signal.symbol] = {
                'shares': shares,
                'avg_price': price,
                'entry_time': signal.timestamp
            }
        
        return {
            'type': 'BUY',
            'symbol': signal.symbol,
            'shares': shares,
            'price': price,
            'timestamp': signal.timestamp,
            'cost': actual_cost,
            'strategy_id': signal.strategy_id
        }
    
    async def _execute_sell(self, signal: TradingSignal, price: float) -> Optional[Dict[str, Any]]:
        """Execute a sell order"""
        
        # Check if we have the position
        if signal.symbol not in self.positions or self.positions[signal.symbol]['shares'] <= 0:
            return None
        
        # Determine how much to sell
        available_shares = self.positions[signal.symbol]['shares']
        
        if signal.position_size:
            # Sell specified percentage
            shares_to_sell = int(available_shares * signal.position_size)
        else:
            # Sell all shares
            shares_to_sell = available_shares
        
        if shares_to_sell <= 0:
            return None
        
        # Execute the sale
        gross_proceeds = shares_to_sell * price
        net_proceeds = gross_proceeds * (1 - self.transaction_cost)
        
        # Update portfolio
        self.cash += net_proceeds
        self.positions[signal.symbol]['shares'] -= shares_to_sell
        
        # Calculate P&L
        avg_cost = self.positions[signal.symbol]['avg_price']
        pnl = shares_to_sell * (price - avg_cost) - gross_proceeds * self.transaction_cost
        
        # Remove position if fully sold
        if self.positions[signal.symbol]['shares'] <= 0:
            entry_time = self.positions[signal.symbol]['entry_time']
            duration = signal.timestamp - entry_time
            del self.positions[signal.symbol]
        else:
            duration = timedelta(0)  # Partial sale
        
        return {
            'type': 'SELL',
            'symbol': signal.symbol,
            'shares': shares_to_sell,
            'price': price,
            'timestamp': signal.timestamp,
            'proceeds': net_proceeds,
            'pnl': pnl,
            'duration': duration,
            'strategy_id': signal.strategy_id
        }
    
    def update_portfolio_value(self, current_data: List[HistoricalDataPoint]) -> None:
        """Update total portfolio value based on current market prices"""
        
        # Start with cash
        total_value = self.cash
        
        # Add market value of positions
        price_data = {data.symbol: data.close_price for data in current_data}
        
        for symbol, position in self.positions.items():
            if symbol in price_data:
                market_value = position['shares'] * price_data[symbol]
                total_value += market_value
        
        self.total_value = total_value


# Built-in Strategy Implementations

class MeanReversionStrategy:
    """Mean reversion trading strategy"""
    
    def __init__(self, lookback_period: int = 20, std_dev_threshold: float = 2.0):
        self._strategy_id = "mean_reversion_v2"
        self._strategy_name = "Enhanced Mean Reversion"
        self._strategy_type = StrategyType.MEAN_REVERSION
        self._parameters = {
            'lookback_period': lookback_period,
            'std_dev_threshold': std_dev_threshold,
            'min_volume': 100000
        }
    
    @property
    def strategy_id(self) -> str:
        return self._strategy_id
    
    @property
    def strategy_name(self) -> str:
        return self._strategy_name
    
    @property
    def strategy_type(self) -> StrategyType:
        return self._strategy_type
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters.copy()
    
    async def generate_signals(self, historical_data: List[HistoricalDataPoint]) -> List[TradingSignal]:
        """Generate mean reversion signals"""
        
        signals = []
        
        # Group data by symbol
        symbol_data = {}
        for data_point in historical_data:
            if data_point.symbol not in symbol_data:
                symbol_data[data_point.symbol] = []
            symbol_data[data_point.symbol].append(data_point)
        
        # Generate signals for each symbol
        for symbol, data_points in symbol_data.items():
            # Sort by timestamp
            data_points.sort(key=lambda x: x.timestamp)
            
            # Need enough data points
            if len(data_points) < self._parameters['lookback_period'] + 1:
                continue
            
            # Get recent prices
            recent_prices = [dp.close_price for dp in data_points[-self._parameters['lookback_period']:]]
            current_price = data_points[-1].close_price
            current_volume = data_points[-1].volume
            
            # Skip if volume too low
            if current_volume < self._parameters['min_volume']:
                continue
            
            # Calculate mean and standard deviation
            mean_price = statistics.mean(recent_prices)
            std_dev = statistics.stdev(recent_prices) if len(recent_prices) > 1 else 0
            
            if std_dev == 0:
                continue
            
            # Calculate z-score
            z_score = (current_price - mean_price) / std_dev
            
            # Generate signals based on z-score
            timestamp = data_points[-1].timestamp
            
            if z_score < -self._parameters['std_dev_threshold']:
                # Price is significantly below mean - BUY signal
                signals.append(TradingSignal(
                    symbol=symbol,
                    signal_type='BUY',
                    strength=SignalStrength.STRONG if abs(z_score) > 2.5 else SignalStrength.MODERATE,
                    confidence=min(0.9, abs(z_score) / 3.0),
                    timestamp=timestamp,
                    strategy_id=self._strategy_id,
                    entry_price=current_price,
                    stop_loss=current_price * 0.95,
                    take_profit=mean_price,
                    reasoning=f"Mean reversion: price {z_score:.2f} std devs below mean"
                ))
                
            elif z_score > self._parameters['std_dev_threshold']:
                # Price is significantly above mean - SELL signal
                signals.append(TradingSignal(
                    symbol=symbol,
                    signal_type='SELL',
                    strength=SignalStrength.STRONG if abs(z_score) > 2.5 else SignalStrength.MODERATE,
                    confidence=min(0.9, abs(z_score) / 3.0),
                    timestamp=timestamp,
                    strategy_id=self._strategy_id,
                    entry_price=current_price,
                    stop_loss=current_price * 1.05,
                    take_profit=mean_price,
                    reasoning=f"Mean reversion: price {z_score:.2f} std devs above mean"
                ))
        
        return signals
    
    async def update_parameters(self, new_parameters: Dict[str, Any]) -> None:
        """Update strategy parameters"""
        self._parameters.update(new_parameters)
    
    def get_required_data_history(self) -> int:
        """Get minimum required data points"""
        return self._parameters['lookback_period'] + 1


class MomentumStrategy:
    """Momentum trading strategy"""
    
    def __init__(self, momentum_period: int = 12, min_momentum: float = 0.05):
        self._strategy_id = "momentum_v2"
        self._strategy_name = "Enhanced Momentum"
        self._strategy_type = StrategyType.MOMENTUM
        self._parameters = {
            'momentum_period': momentum_period,
            'min_momentum': min_momentum,
            'stop_loss_pct': 0.08,
            'min_volume': 500000
        }
    
    @property
    def strategy_id(self) -> str:
        return self._strategy_id
    
    @property
    def strategy_name(self) -> str:
        return self._strategy_name
    
    @property
    def strategy_type(self) -> StrategyType:
        return self._strategy_type
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters.copy()
    
    async def generate_signals(self, historical_data: List[HistoricalDataPoint]) -> List[TradingSignal]:
        """Generate momentum signals"""
        
        signals = []
        
        # Group data by symbol
        symbol_data = {}
        for data_point in historical_data:
            if data_point.symbol not in symbol_data:
                symbol_data[data_point.symbol] = []
            symbol_data[data_point.symbol].append(data_point)
        
        # Generate signals for each symbol
        for symbol, data_points in symbol_data.items():
            # Sort by timestamp
            data_points.sort(key=lambda x: x.timestamp)
            
            # Need enough data points
            if len(data_points) < self._parameters['momentum_period'] + 1:
                continue
            
            # Calculate momentum
            current_price = data_points[-1].close_price
            past_price = data_points[-(self._parameters['momentum_period'] + 1)].close_price
            momentum = (current_price - past_price) / past_price
            
            # Check volume
            current_volume = data_points[-1].volume
            if current_volume < self._parameters['min_volume']:
                continue
            
            timestamp = data_points[-1].timestamp
            
            # Generate signals based on momentum
            if momentum > self._parameters['min_momentum']:
                # Strong upward momentum - BUY signal
                signals.append(TradingSignal(
                    symbol=symbol,
                    signal_type='BUY',
                    strength=SignalStrength.STRONG if momentum > 0.1 else SignalStrength.MODERATE,
                    confidence=min(0.9, momentum * 10),
                    timestamp=timestamp,
                    strategy_id=self._strategy_id,
                    entry_price=current_price,
                    stop_loss=current_price * (1 - self._parameters['stop_loss_pct']),
                    reasoning=f"Momentum: {momentum:.2%} over {self._parameters['momentum_period']} periods"
                ))
                
            elif momentum < -self._parameters['min_momentum']:
                # Strong downward momentum - SELL signal
                signals.append(TradingSignal(
                    symbol=symbol,
                    signal_type='SELL',
                    strength=SignalStrength.STRONG if momentum < -0.1 else SignalStrength.MODERATE,
                    confidence=min(0.9, abs(momentum) * 10),
                    timestamp=timestamp,
                    strategy_id=self._strategy_id,
                    entry_price=current_price,
                    stop_loss=current_price * (1 + self._parameters['stop_loss_pct']),
                    reasoning=f"Momentum: {momentum:.2%} over {self._parameters['momentum_period']} periods"
                ))
        
        return signals
    
    async def update_parameters(self, new_parameters: Dict[str, Any]) -> None:
        """Update strategy parameters"""
        self._parameters.update(new_parameters)
    
    def get_required_data_history(self) -> int:
        """Get minimum required data points"""
        return self._parameters['momentum_period'] + 1


class PairsTradingStrategy:
    """Pairs trading strategy"""
    
    def __init__(self, correlation_threshold: float = 0.8, spread_threshold: float = 2.0):
        self._strategy_id = "pairs_trading_v2"
        self._strategy_name = "Enhanced Pairs Trading"
        self._strategy_type = StrategyType.PAIRS_TRADING
        self._parameters = {
            'correlation_threshold': correlation_threshold,
            'spread_threshold': spread_threshold,
            'lookback_period': 60,
            'min_volume': 200000
        }
    
    @property
    def strategy_id(self) -> str:
        return self._strategy_id
    
    @property
    def strategy_name(self) -> str:
        return self._strategy_name
    
    @property
    def strategy_type(self) -> StrategyType:
        return self._strategy_type
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters.copy()
    
    async def generate_signals(self, historical_data: List[HistoricalDataPoint]) -> List[TradingSignal]:
        """Generate pairs trading signals"""
        
        signals = []
        
        # Group data by symbol
        symbol_data = {}
        for data_point in historical_data:
            if data_point.symbol not in symbol_data:
                symbol_data[data_point.symbol] = []
            symbol_data[data_point.symbol].append(data_point)
        
        # Need at least 2 symbols for pairs trading
        symbols = list(symbol_data.keys())
        if len(symbols) < 2:
            return signals
        
        # Find correlated pairs
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                symbol1, symbol2 = symbols[i], symbols[j]
                
                # Get aligned price series
                data1 = sorted(symbol_data[symbol1], key=lambda x: x.timestamp)
                data2 = sorted(symbol_data[symbol2], key=lambda x: x.timestamp)
                
                if len(data1) < self._parameters['lookback_period'] or len(data2) < self._parameters['lookback_period']:
                    continue
                
                # Calculate correlation
                prices1 = [dp.close_price for dp in data1[-self._parameters['lookback_period']:]]
                prices2 = [dp.close_price for dp in data2[-self._parameters['lookback_period']:]]
                
                if len(prices1) != len(prices2):
                    continue
                
                correlation = np.corrcoef(prices1, prices2)[0, 1]
                
                if abs(correlation) < self._parameters['correlation_threshold']:
                    continue
                
                # Calculate spread
                current_price1 = data1[-1].close_price
                current_price2 = data2[-1].close_price
                
                # Normalize prices to ratio
                avg_price1 = statistics.mean(prices1)
                avg_price2 = statistics.mean(prices2)
                
                normalized_price1 = current_price1 / avg_price1
                normalized_price2 = current_price2 / avg_price2
                
                spread = normalized_price1 - normalized_price2
                
                # Calculate historical spread statistics
                spreads = []
                for k in range(len(prices1)):
                    norm_p1 = prices1[k] / avg_price1
                    norm_p2 = prices2[k] / avg_price2
                    spreads.append(norm_p1 - norm_p2)
                
                spread_mean = statistics.mean(spreads)
                spread_std = statistics.stdev(spreads) if len(spreads) > 1 else 0
                
                if spread_std == 0:
                    continue
                
                spread_z_score = (spread - spread_mean) / spread_std
                
                timestamp = max(data1[-1].timestamp, data2[-1].timestamp)
                
                # Generate signals based on spread divergence
                if abs(spread_z_score) > self._parameters['spread_threshold']:
                    if spread_z_score > 0:
                        # Symbol1 overvalued relative to Symbol2
                        # SELL Symbol1, BUY Symbol2
                        if (data1[-1].volume >= self._parameters['min_volume'] and 
                            data2[-1].volume >= self._parameters['min_volume']):
                            
                            signals.append(TradingSignal(
                                symbol=symbol1,
                                signal_type='SELL',
                                strength=SignalStrength.MODERATE,
                                confidence=min(0.8, abs(spread_z_score) / 3.0),
                                timestamp=timestamp,
                                strategy_id=self._strategy_id,
                                entry_price=current_price1,
                                reasoning=f"Pairs trading: {symbol1} overvalued vs {symbol2}"
                            ))
                            
                            signals.append(TradingSignal(
                                symbol=symbol2,
                                signal_type='BUY',
                                strength=SignalStrength.MODERATE,
                                confidence=min(0.8, abs(spread_z_score) / 3.0),
                                timestamp=timestamp,
                                strategy_id=self._strategy_id,
                                entry_price=current_price2,
                                reasoning=f"Pairs trading: {symbol2} undervalued vs {symbol1}"
                            ))
                    else:
                        # Symbol2 overvalued relative to Symbol1
                        # BUY Symbol1, SELL Symbol2
                        if (data1[-1].volume >= self._parameters['min_volume'] and 
                            data2[-1].volume >= self._parameters['min_volume']):
                            
                            signals.append(TradingSignal(
                                symbol=symbol1,
                                signal_type='BUY',
                                strength=SignalStrength.MODERATE,
                                confidence=min(0.8, abs(spread_z_score) / 3.0),
                                timestamp=timestamp,
                                strategy_id=self._strategy_id,
                                entry_price=current_price1,
                                reasoning=f"Pairs trading: {symbol1} undervalued vs {symbol2}"
                            ))
                            
                            signals.append(TradingSignal(
                                symbol=symbol2,
                                signal_type='SELL',
                                strength=SignalStrength.MODERATE,
                                confidence=min(0.8, abs(spread_z_score) / 3.0),
                                timestamp=timestamp,
                                strategy_id=self._strategy_id,
                                entry_price=current_price2,
                                reasoning=f"Pairs trading: {symbol2} overvalued vs {symbol1}"
                            ))
        
        return signals
    
    async def update_parameters(self, new_parameters: Dict[str, Any]) -> None:
        """Update strategy parameters"""
        self._parameters.update(new_parameters)
    
    def get_required_data_history(self) -> int:
        """Get minimum required data points"""
        return self._parameters['lookback_period']


class RiskParityStrategy:
    """Risk parity strategy"""
    
    def __init__(self, rebalance_threshold: float = 0.05, target_volatility: float = 0.10):
        self._strategy_id = "risk_parity_v2"
        self._strategy_name = "Enhanced Risk Parity"
        self._strategy_type = StrategyType.RISK_PARITY
        self._parameters = {
            'rebalance_threshold': rebalance_threshold,
            'target_volatility': target_volatility,
            'volatility_lookback': 60,
            'min_weight': 0.05,
            'max_weight': 0.40
        }
    
    @property
    def strategy_id(self) -> str:
        return self._strategy_id
    
    @property
    def strategy_name(self) -> str:
        return self._strategy_name
    
    @property
    def strategy_type(self) -> StrategyType:
        return self._strategy_type
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters.copy()
    
    async def generate_signals(self, historical_data: List[HistoricalDataPoint]) -> List[TradingSignal]:
        """Generate risk parity signals"""
        
        signals = []
        
        # Group data by symbol
        symbol_data = {}
        for data_point in historical_data:
            if data_point.symbol not in symbol_data:
                symbol_data[data_point.symbol] = []
            symbol_data[data_point.symbol].append(data_point)
        
        symbols = list(symbol_data.keys())
        if len(symbols) < 2:
            return signals
        
        # Calculate volatilities for each symbol
        volatilities = {}
        for symbol, data_points in symbol_data.items():
            data_points.sort(key=lambda x: x.timestamp)
            
            if len(data_points) < self._parameters['volatility_lookback']:
                continue
            
            # Calculate returns
            prices = [dp.close_price for dp in data_points[-self._parameters['volatility_lookback']:]]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            
            if len(returns) > 1:
                volatility = statistics.stdev(returns) * math.sqrt(252)  # Annualized
                volatilities[symbol] = volatility
        
        if not volatilities:
            return signals
        
        # Calculate inverse volatility weights
        inv_volatilities = {symbol: 1.0 / vol for symbol, vol in volatilities.items() if vol > 0}
        
        if not inv_volatilities:
            return signals
        
        # Normalize to get target weights
        total_inv_vol = sum(inv_volatilities.values())
        target_weights = {symbol: inv_vol / total_inv_vol for symbol, inv_vol in inv_volatilities.items()}
        
        # Apply weight constraints
        for symbol in target_weights:
            target_weights[symbol] = max(self._parameters['min_weight'], 
                                       min(self._parameters['max_weight'], target_weights[symbol]))
        
        # Re-normalize after constraints
        total_weight = sum(target_weights.values())
        for symbol in target_weights:
            target_weights[symbol] /= total_weight
        
        # Generate rebalancing signals (simplified)
        timestamp = max(data_points[-1].timestamp for data_points in symbol_data.values())
        
        for symbol, target_weight in target_weights.items():
            # In practice, would compare with current portfolio weights
            # For now, generate BUY signals for rebalancing
            signals.append(TradingSignal(
                symbol=symbol,
                signal_type='BUY',
                strength=SignalStrength.MODERATE,
                confidence=0.7,
                timestamp=timestamp,
                strategy_id=self._strategy_id,
                position_size=target_weight,
                entry_price=symbol_data[symbol][-1].close_price,
                reasoning=f"Risk parity rebalance to {target_weight:.1%} weight"
            ))
        
        return signals
    
    async def update_parameters(self, new_parameters: Dict[str, Any]) -> None:
        """Update strategy parameters"""
        self._parameters.update(new_parameters)
    
    def get_required_data_history(self) -> int:
        """Get minimum required data points"""
        return self._parameters['volatility_lookback']