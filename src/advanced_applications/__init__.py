"""
Phase 5: Advanced Applications Module

This module contains intelligent financial advisory, market analysis integration,
modular strategy engine, and GGML-based ML trading strategies for the 
ElizaOS-OpenCog-GnuCash framework.
"""

from .intelligent_financial_advisory import (
    IntelligentFinancialAdvisor,
    FinancialGoal,
    InvestmentRecommendation,
    TaxOptimization,
    RiskTolerance,
    InvestmentObjective
)

from .market_analysis_integration import (
    MarketAnalysisEngine,
    MarketData,
    SentimentIndicator,
    TradingStrategy as MarketTradingStrategy,
    PortfolioOptimization,
    MarketSentiment,
    TradingSignal as MarketTradingSignal,
    RiskLevel
)

from .strategy_engine import (
    ModularStrategyEngine,
    HistoricalDataReplay,
    BacktestPortfolio,
    TradingSignal,
    TradingStrategy,
    StrategyPerformanceMetrics,
    HistoricalDataPoint,
    SignalStrength,
    StrategyType,
    MeanReversionStrategy,
    MomentumStrategy,
    PairsTradingStrategy,
    RiskParityStrategy
)

from .ggml_strategies import (
    GGMLIntegration,
    MLBasedTradingStrategy,
    HypergraphPatternAnalyzer,
    MLModelType,
    MLFeatureSet,
    MLModelPrediction,
    HypergraphNode,
    HypergraphEdge
)

__all__ = [
    # Intelligent Financial Advisory
    'IntelligentFinancialAdvisor',
    'FinancialGoal',
    'InvestmentRecommendation',
    'TaxOptimization',
    'RiskTolerance',
    'InvestmentObjective',
    
    # Market Analysis Integration  
    'MarketAnalysisEngine',
    'MarketData',
    'SentimentIndicator',
    'MarketTradingStrategy',
    'PortfolioOptimization',
    'MarketSentiment',
    'MarketTradingSignal',
    'RiskLevel',
    
    # Modular Strategy Engine
    'ModularStrategyEngine',
    'HistoricalDataReplay',
    'BacktestPortfolio',
    'TradingSignal',
    'TradingStrategy',
    'StrategyPerformanceMetrics',
    'HistoricalDataPoint',
    'SignalStrength',
    'StrategyType',
    'MeanReversionStrategy',
    'MomentumStrategy',
    'PairsTradingStrategy',
    'RiskParityStrategy',
    
    # GGML ML Integration
    'GGMLIntegration',
    'MLBasedTradingStrategy',
    'HypergraphPatternAnalyzer',
    'MLModelType',
    'MLFeatureSet',
    'MLModelPrediction',
    'HypergraphNode',
    'HypergraphEdge'
]