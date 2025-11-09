"""
Phase 5 ML Pipeline Package

Advanced ML model development pipeline, automated retraining scheduler,
model drift detection, and real-time sentiment analysis.
"""

from .ml_model_pipeline import (
    MLModelPipeline,
    ModelConfig,
    ModelType,
    PipelineStage,
    NotebookTemplate,
    PipelineExecution
)

from .automated_retraining_scheduler import (
    AutomatedRetrainingScheduler,
    RetrainingJob,
    RetrainingTrigger,
    ScheduleFrequency,
    ModelPerformanceMetrics,
    RetrainingExecution
)

from .model_drift_detector import (
    ModelDriftDetector,
    DriftType,
    DriftSeverity,
    DriftDetectionResult,
    ModelMonitoringMetrics,
    DataQualityReport,
    MonitoringAlert
)

from .realtime_sentiment_analyzer import (
    RealTimeSentimentAnalyzer,
    NewsDataSource,
    SocialMediaDataSource,
    MarketDataSource,
    DataSourceType,
    SentimentPolarity,
    SentimentData,
    CognitiveSentimentSynthesis
)

__version__ = "1.0.0"
__author__ = "ElizaOS-OpenCog-GnuCash Team"

__all__ = [
    # ML Pipeline
    'MLModelPipeline',
    'ModelConfig', 
    'ModelType',
    'PipelineStage',
    'NotebookTemplate',
    'PipelineExecution',
    
    # Automated Retraining
    'AutomatedRetrainingScheduler',
    'RetrainingJob',
    'RetrainingTrigger',
    'ScheduleFrequency', 
    'ModelPerformanceMetrics',
    'RetrainingExecution',
    
    # Drift Detection
    'ModelDriftDetector',
    'DriftType',
    'DriftSeverity',
    'DriftDetectionResult',
    'ModelMonitoringMetrics',
    'DataQualityReport',
    'MonitoringAlert',
    
    # Sentiment Analysis
    'RealTimeSentimentAnalyzer',
    'NewsDataSource',
    'SocialMediaDataSource', 
    'MarketDataSource',
    'DataSourceType',
    'SentimentPolarity',
    'SentimentData',
    'CognitiveSentimentSynthesis'
]