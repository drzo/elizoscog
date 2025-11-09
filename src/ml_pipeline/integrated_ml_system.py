"""
Phase 5: Integrated ML Pipeline and Market Analysis System

Complete integration of ML model pipeline, automated retraining, drift detection,
and real-time sentiment analysis for cognitive-financial intelligence.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from .ml_model_pipeline import MLModelPipeline, ModelConfig, ModelType, PipelineStage
from .automated_retraining_scheduler import (
    AutomatedRetrainingScheduler, RetrainingJob, RetrainingTrigger, 
    ScheduleFrequency, ModelPerformanceMetrics
)
from .model_drift_detector import ModelDriftDetector, DriftType
from .realtime_sentiment_analyzer import (
    RealTimeSentimentAnalyzer, NewsDataSource, SocialMediaDataSource, 
    MarketDataSource, DataSourceType
)
from .onnx_optimization import ONNXIntegration, ONNXModelConfig, ONNXOptimizationLevel, ONNXProviderType

logger = logging.getLogger(__name__)


class Phase5MLIntegratedSystem:
    """
    Complete Phase 5 ML system integrating all components:
    - ML Model Pipeline with notebook-based development
    - Automated retraining scheduler with drift triggers
    - Model drift detection and performance monitoring
    - Real-time sentiment analysis and cognitive synthesis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize base paths
        self.base_path = Path(self.config.get('base_path', './phase5_ml_system'))
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize all components
        self.ml_pipeline = MLModelPipeline({
            'base_path': str(self.base_path / 'ml_pipeline'),
            **self.config.get('ml_pipeline', {})
        })
        
        self.retraining_scheduler = AutomatedRetrainingScheduler({
            'base_path': str(self.base_path / 'retraining'),
            'ml_pipeline_config': {'base_path': str(self.base_path / 'ml_pipeline')},
            **self.config.get('retraining', {})
        })
        
        self.drift_detector = ModelDriftDetector({
            'base_path': str(self.base_path / 'drift_detection'),
            **self.config.get('drift_detection', {})
        })
        
        self.sentiment_analyzer = RealTimeSentimentAnalyzer({
            'base_path': str(self.base_path / 'sentiment_analysis'),
            **self.config.get('sentiment_analysis', {})
        })
        
        # Phase 6: Add ONNX optimization integration
        self.onnx_integration = ONNXIntegration()
        
        # System state
        self.is_running = False
        self.monitoring_tasks = []
        
        logger.info("Phase 5 ML Integrated System initialized")
    
    async def initialize(self):
        """Initialize the complete system"""
        try:
            # Setup default data sources for sentiment analysis
            await self._setup_default_data_sources()
            
            # Register default models
            await self._setup_default_models()
            
            # Setup default retraining jobs
            await self._setup_default_retraining_jobs()
            
            logger.info("Phase 5 ML Integrated System initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phase 5 ML system: {e}")
            raise
    
    async def _setup_default_data_sources(self):
        """Setup default data sources for sentiment analysis"""
        
        # Financial news source
        news_source = NewsDataSource('financial_news_primary', {
            'api_key': 'demo_key',
            'base_url': 'https://api.financial-news.com',
            'symbols': ['SPY', 'QQQ', 'TLT', 'GLD', 'VIX']
        })
        await self.sentiment_analyzer.register_data_source(news_source)
        
        # Social media source
        social_source = SocialMediaDataSource('social_sentiment', {
            'platforms': ['twitter', 'reddit'],
            'keywords': ['stocks', 'market', 'trading', 'investment', 'fed', 'economy']
        })
        await self.sentiment_analyzer.register_data_source(social_source)
        
        # Market data source
        market_source = MarketDataSource('market_data_realtime', {
            'symbols': ['SPY', 'QQQ', 'TLT', 'GLD'],
            'data_types': ['price', 'volume', 'volatility']
        })
        await self.sentiment_analyzer.register_data_source(market_source)
        
        logger.info("Default data sources configured")
    
    async def _setup_default_models(self):
        """Setup default ML models"""
        
        models = [
            ModelConfig(
                model_id="lstm_price_predictor_v1",
                model_type=ModelType.LSTM_PRICE_PREDICTION,
                name="LSTM Price Predictor v1",
                description="LSTM model for price prediction with technical indicators",
                hyperparameters={
                    'sequence_length': 60,
                    'lstm_units': [128, 64, 32],
                    'dropout': 0.2,
                    'learning_rate': 0.001
                },
                training_config={
                    'epochs': 100,
                    'batch_size': 32,
                    'validation_split': 0.2
                },
                data_requirements={
                    'symbols': ['SPY', 'QQQ'],
                    'features': ['price', 'volume', 'technical_indicators'],
                    'history_days': 252
                },
                performance_targets={
                    'accuracy': 0.75,
                    'sharpe_ratio': 1.2,
                    'max_drawdown': 0.15
                }
            ),
            ModelConfig(
                model_id="transformer_sentiment_v1", 
                model_type=ModelType.TRANSFORMER_SENTIMENT,
                name="Financial Sentiment Transformer v1",
                description="Transformer model for financial sentiment analysis",
                hyperparameters={
                    'model_name': 'distilbert-base-uncased',
                    'max_length': 512,
                    'learning_rate': 2e-5
                },
                training_config={
                    'epochs': 5,
                    'batch_size': 16
                },
                data_requirements={
                    'data_types': ['news', 'social_media'],
                    'min_samples': 10000
                },
                performance_targets={
                    'accuracy': 0.85,
                    'f1_score': 0.82
                }
            ),
            ModelConfig(
                model_id="hypergraph_market_patterns_v1",
                model_type=ModelType.HYPERGRAPH_NEURAL,
                name="Hypergraph Market Pattern Analyzer v1", 
                description="Hypergraph neural network for market pattern recognition",
                hyperparameters={
                    'num_nodes': 1000,
                    'num_edges': 5000,
                    'embedding_dim': 128,
                    'num_layers': 4
                },
                training_config={
                    'epochs': 50,
                    'batch_size': 64
                },
                data_requirements={
                    'symbols': ['SPY', 'QQQ', 'TLT', 'GLD', 'VIX'],
                    'relationship_types': ['correlation', 'causality', 'sentiment']
                },
                performance_targets={
                    'pattern_accuracy': 0.78,
                    'signal_quality': 0.65
                }
            )
        ]
        
        for model_config in models:
            await self.ml_pipeline.register_model(model_config)
            
            # Establish baselines for drift detection
            await self._establish_model_baseline(model_config.model_id)
        
        logger.info(f"Registered {len(models)} default models")
    
    async def _establish_model_baseline(self, model_id: str):
        """Establish baseline for a model"""
        # Generate mock baseline data
        baseline_data = []
        baseline_predictions = []
        
        import random
        for i in range(500):  # Generate 500 baseline samples
            baseline_data.append({
                'feature1': random.gauss(10, 2),
                'feature2': random.gauss(5, 1),
                'feature3': random.gauss(0, 0.5),
                'feature4': random.gauss(100, 20),
                'feature5': random.gauss(50, 10)
            })
            baseline_predictions.append(random.gauss(0.6, 0.2))
        
        await self.drift_detector.establish_baseline(
            model_id, baseline_data, baseline_predictions
        )
        
        logger.info(f"Established baseline for model {model_id}")
    
    async def _setup_default_retraining_jobs(self):
        """Setup default retraining jobs for models"""
        
        jobs = [
            RetrainingJob(
                job_id="daily_lstm_retraining",
                model_id="lstm_price_predictor_v1",
                name="Daily LSTM Retraining",
                description="Daily retraining for LSTM price predictor",
                schedule_frequency=ScheduleFrequency.DAILY,
                triggers=[
                    RetrainingTrigger.SCHEDULED,
                    RetrainingTrigger.PERFORMANCE_DECAY,
                    RetrainingTrigger.DATA_DRIFT
                ],
                performance_thresholds={
                    'accuracy': 0.70,
                    'sharpe_ratio': 1.0
                },
                drift_thresholds={
                    'data_drift': 0.3,
                    'model_drift': 0.25
                },
                notification_settings={
                    'console': {'enabled': True},
                    'email': {
                        'enabled': False,
                        'recipients': ['ml-team@example.com']
                    }
                }
            ),
            RetrainingJob(
                job_id="weekly_sentiment_retraining",
                model_id="transformer_sentiment_v1",
                name="Weekly Sentiment Model Retraining",
                description="Weekly retraining for sentiment transformer",
                schedule_frequency=ScheduleFrequency.WEEKLY,
                triggers=[
                    RetrainingTrigger.SCHEDULED,
                    RetrainingTrigger.CONCEPT_DRIFT
                ],
                performance_thresholds={
                    'accuracy': 0.80,
                    'f1_score': 0.78
                },
                drift_thresholds={
                    'concept_drift': 0.4
                }
            )
        ]
        
        for job in jobs:
            await self.retraining_scheduler.register_retraining_job(job)
        
        logger.info(f"Registered {len(jobs)} retraining jobs")
    
    async def start_system(self):
        """Start the complete system"""
        if self.is_running:
            logger.warning("System is already running")
            return
        
        try:
            # Start sentiment analysis
            await self.sentiment_analyzer.start_real_time_ingestion()
            
            # Start retraining scheduler
            self.retraining_scheduler.start_scheduler()
            
            # Start monitoring tasks
            self.monitoring_tasks = [
                asyncio.create_task(self._continuous_monitoring_loop()),
                asyncio.create_task(self._performance_reporting_loop())
            ]
            
            self.is_running = True
            logger.info("Phase 5 ML Integrated System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Phase 5 ML system: {e}")
            await self.stop_system()
            raise
    
    async def stop_system(self):
        """Stop the complete system"""
        if not self.is_running:
            return
        
        try:
            # Stop monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Stop retraining scheduler
            self.retraining_scheduler.stop_scheduler()
            
            # Stop sentiment analysis
            await self.sentiment_analyzer.stop_real_time_ingestion()
            
            self.is_running = False
            logger.info("Phase 5 ML Integrated System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping system: {e}")
    
    async def _continuous_monitoring_loop(self):
        """Continuous monitoring of all system components"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Monitor model performance
                await self._monitor_model_performance()
                
                # Check for drift
                await self._check_model_drift()
                
                # Monitor data ingestion
                self._monitor_data_ingestion()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_model_performance(self):
        """Monitor model performance and record metrics"""
        
        # Simulate model performance monitoring
        import random
        
        model_ids = [
            "lstm_price_predictor_v1",
            "transformer_sentiment_v1", 
            "hypergraph_market_patterns_v1"
        ]
        
        for model_id in model_ids:
            # Generate mock performance metrics
            metrics = ModelPerformanceMetrics(
                model_id=model_id,
                timestamp=datetime.now(),
                accuracy=random.uniform(0.65, 0.85),
                precision=random.uniform(0.60, 0.82),
                recall=random.uniform(0.58, 0.80),
                f1_score=random.uniform(0.59, 0.81),
                prediction_latency_ms=random.uniform(10, 100),
                throughput_qps=random.uniform(50, 200),
                error_rate=random.uniform(0, 0.05),
                data_drift_score=random.uniform(0, 0.4),
                model_drift_score=random.uniform(0, 0.3),
                concept_drift_score=random.uniform(0, 0.2)
            )
            
            await self.retraining_scheduler.record_model_performance(metrics)
            
            # Also record monitoring metrics for drift detector
            monitoring_metrics = ModelMonitoringMetrics(
                model_id=model_id,
                timestamp=metrics.timestamp,
                accuracy=metrics.accuracy,
                precision=metrics.precision,
                recall=metrics.recall,
                f1_score=metrics.f1_score,
                prediction_latency_ms=metrics.prediction_latency_ms,
                throughput_qps=metrics.throughput_qps,
                error_rate=metrics.error_rate,
                data_drift_score=metrics.data_drift_score,
                model_drift_score=metrics.model_drift_score,
                concept_drift_score=metrics.concept_drift_score
            )
            
            if model_id not in self.drift_detector.monitoring_metrics:
                self.drift_detector.monitoring_metrics[model_id] = []
            self.drift_detector.monitoring_metrics[model_id].append(monitoring_metrics)
        
        logger.debug("Model performance monitoring completed")
    
    async def _check_model_drift(self):
        """Check for model drift across all models"""
        
        model_ids = [
            "lstm_price_predictor_v1",
            "transformer_sentiment_v1", 
            "hypergraph_market_patterns_v1"
        ]
        
        for model_id in model_ids:
            if model_id not in self.drift_detector.baseline_distributions:
                continue
                
            # Generate mock current data for drift detection
            import random
            current_data = []
            current_predictions = []
            
            for i in range(200):
                # Add some drift to the data
                drift_factor = random.uniform(0.8, 1.2)
                current_data.append({
                    'feature1': random.gauss(10 * drift_factor, 2),
                    'feature2': random.gauss(5 * drift_factor, 1),
                    'feature3': random.gauss(0, 0.5),
                    'feature4': random.gauss(100 * drift_factor, 20),
                    'feature5': random.gauss(50, 10)
                })
                current_predictions.append(random.gauss(0.6 * drift_factor, 0.2))
            
            # Detect drift
            drift_results = await self.drift_detector.detect_drift(
                model_id, current_data, current_predictions
            )
            
            if drift_results:
                logger.info(f"Detected {len(drift_results)} drift issues for model {model_id}")
                
                # Log significant drift
                for drift_result in drift_results:
                    if drift_result.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
                        logger.warning(f"High severity drift detected: {drift_result.explanation}")
    
    def _monitor_data_ingestion(self):
        """Monitor data ingestion performance"""
        ingestion_metrics = self.sentiment_analyzer.get_source_metrics()
        
        for source_name, metrics in ingestion_metrics.items():
            if metrics['error_rate'] > 0.1:  # More than 10% error rate
                logger.warning(f"High error rate in data source {source_name}: {metrics['error_rate']:.2%}")
            
            if metrics['data_quality_score'] < 0.8:  # Below 80% quality
                logger.warning(f"Low data quality in source {source_name}: {metrics['data_quality_score']:.2%}")
        
        logger.debug("Data ingestion monitoring completed")
    
    async def _performance_reporting_loop(self):
        """Generate periodic performance reports"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Generate report every hour
                
                report = await self.generate_system_performance_report()
                
                # Save report
                report_file = self.base_path / 'reports' / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                report_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(report_file, 'w') as f:
                    import json
                    json.dump(report, f, indent=2)
                
                logger.info(f"Generated system performance report: {report_file}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance reporting loop: {e}")
                await asyncio.sleep(300)
    
    async def generate_system_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive system performance report"""
        
        timestamp = datetime.now()
        
        # System overview
        system_overview = {
            'timestamp': timestamp.isoformat(),
            'system_status': 'running' if self.is_running else 'stopped',
            'uptime_hours': (datetime.now() - timestamp).total_seconds() / 3600,
            'components': {
                'ml_pipeline': 'active',
                'retraining_scheduler': 'active' if self.retraining_scheduler.scheduler_running else 'inactive',
                'drift_detector': 'active',
                'sentiment_analyzer': 'active'
            }
        }
        
        # Model performance summary
        model_performance = {}
        for job_id in self.retraining_scheduler.jobs.keys():
            job_status = self.retraining_scheduler.get_job_status(job_id)
            model_performance[job_status['model_id']] = {
                'execution_count': job_status['execution_count'],
                'success_rate': job_status['success_rate'],
                'last_execution': job_status['last_execution']
            }
        
        # Drift detection summary
        drift_summary = {}
        for model_id in self.drift_detector.baseline_distributions.keys():
            recent_drifts = self.drift_detector.get_drift_history(model_id, days=7)
            drift_summary[model_id] = {
                'drift_events_7d': len(recent_drifts),
                'latest_drift': recent_drifts[0] if recent_drifts else None
            }
        
        # Sentiment analysis summary
        sentiment_summary = self.sentiment_analyzer.get_current_sentiment_synthesis()
        
        # Data ingestion summary
        ingestion_summary = self.sentiment_analyzer.get_source_metrics()
        
        return {
            'system_overview': system_overview,
            'model_performance': model_performance,
            'drift_detection': drift_summary,
            'sentiment_analysis': sentiment_summary,
            'data_ingestion': ingestion_summary
        }
    
    async def create_model_from_template(self, template_id: str, model_id: str, 
                                       custom_params: Optional[Dict[str, Any]] = None) -> str:
        """Create a new model from notebook template"""
        return await self.ml_pipeline.create_notebook_from_template(
            template_id, model_id, custom_params
        )
    
    async def deploy_new_model(self, model_config: ModelConfig, 
                             setup_retraining: bool = True) -> Dict[str, str]:
        """Deploy a new model with complete setup"""
        
        # Register model
        await self.ml_pipeline.register_model(model_config)
        
        # Establish baseline
        await self._establish_model_baseline(model_config.model_id)
        
        # Setup retraining job if requested
        retraining_job_id = None
        if setup_retraining:
            retraining_job = RetrainingJob(
                job_id=f"retraining_{model_config.model_id}",
                model_id=model_config.model_id,
                name=f"Retraining for {model_config.name}",
                description=f"Automated retraining job for {model_config.name}",
                schedule_frequency=ScheduleFrequency.DAILY,
                triggers=[
                    RetrainingTrigger.SCHEDULED,
                    RetrainingTrigger.PERFORMANCE_DECAY,
                    RetrainingTrigger.DATA_DRIFT
                ],
                performance_thresholds=model_config.performance_targets,
                drift_thresholds={'data_drift': 0.3, 'model_drift': 0.25}
            )
            
            await self.retraining_scheduler.register_retraining_job(retraining_job)
            retraining_job_id = retraining_job.job_id
        
        logger.info(f"Successfully deployed model {model_config.model_id}")
        
        return {
            'model_id': model_config.model_id,
            'retraining_job_id': retraining_job_id,
            'status': 'deployed'
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'is_running': self.is_running,
            'models_registered': len(self.ml_pipeline.models),
            'retraining_jobs_active': len([
                job for job in self.retraining_scheduler.jobs.values() 
                if job.enabled
            ]),
            'data_sources_active': len(self.sentiment_analyzer.data_sources),
            'current_sentiment': self.sentiment_analyzer.get_current_sentiment_synthesis(),
            'uptime': 'running' if self.is_running else 'stopped',
            # Phase 6 enhancements
            'onnx_optimizers': len(self.onnx_integration.optimizers),
            'onnx_models_ready': sum(1 for opt in self.onnx_integration.optimizers.values() if opt.session is not None),
            'phase6_features_enabled': True
        }
    
    # Phase 6: ONNX Optimization Methods
    
    async def setup_onnx_optimization(self, model_id: str, input_shape: Tuple[int, ...], 
                                     output_shape: Tuple[int, ...], 
                                     optimization_level: ONNXOptimizationLevel = ONNXOptimizationLevel.EXTENDED,
                                     provider_type: ONNXProviderType = ONNXProviderType.CPU) -> str:
        """Setup ONNX optimization for a specific model"""
        config = ONNXModelConfig(
            model_name=model_id,
            input_shape=input_shape,
            output_shape=output_shape,
            optimization_level=optimization_level,
            provider_type=provider_type
        )
        
        optimizer = await self.onnx_integration.create_optimizer(model_id, config)
        logger.info(f"ONNX optimization setup for model {model_id}")
        
        return f"onnx_optimizer_{model_id}"
    
    async def optimize_model_with_onnx(self, model_id: str, source_model: Any, 
                                      model_format: str = "pytorch") -> Dict[str, Any]:
        """Optimize an existing model using ONNX"""
        try:
            result = await self.onnx_integration.optimize_pipeline_model(
                model_id, source_model, model_format
            )
            
            logger.info(f"Successfully optimized model {model_id} with ONNX")
            return {
                "status": "success",
                "model_id": model_id,
                "optimization_result": result,
                "performance_gains": "Estimated 1.2-3x speedup depending on model complexity"
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize model {model_id} with ONNX: {e}")
            return {
                "status": "error",
                "model_id": model_id,
                "error": str(e)
            }
    
    async def benchmark_onnx_models(self, test_data_size: int = 32) -> Dict[str, Any]:
        """Benchmark all ONNX optimized models"""
        import numpy as np
        
        benchmark_results = {}
        
        for model_name, optimizer in self.onnx_integration.optimizers.items():
            try:
                # Generate test data based on model input shape
                test_data = np.random.randn(test_data_size, *optimizer.config.input_shape[1:]).astype(np.float32)
                
                # Run benchmark
                benchmark_result = await optimizer.benchmark_model(test_data, num_iterations=50)
                benchmark_results[model_name] = benchmark_result
                
                logger.info(f"Benchmarked ONNX model {model_name}: {benchmark_result['latency_stats']['mean_ms']:.2f}ms avg latency")
                
            except Exception as e:
                logger.error(f"Failed to benchmark ONNX model {model_name}: {e}")
                benchmark_results[model_name] = {"error": str(e)}
        
        return {
            "benchmark_timestamp": datetime.now().isoformat(),
            "test_batch_size": test_data_size,
            "model_results": benchmark_results,
            "summary": self._summarize_onnx_benchmarks(benchmark_results)
        }
    
    def _summarize_onnx_benchmarks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize ONNX benchmark results"""
        successful_results = [r for r in results.values() if "error" not in r]
        
        if not successful_results:
            return {"status": "no_successful_benchmarks"}
        
        import numpy as np
        latencies = [r["latency_stats"]["mean_ms"] for r in successful_results]
        throughputs = [r["throughput_stats"]["mean_ops_per_sec"] for r in successful_results]
        
        return {
            "total_models": len(results),
            "successful_benchmarks": len(successful_results),
            "average_latency_ms": np.mean(latencies),
            "best_latency_ms": np.min(latencies),
            "worst_latency_ms": np.max(latencies),
            "average_throughput": np.mean(throughputs),
            "total_model_size_mb": sum(r.get("model_size_mb", 0) for r in successful_results)
        }
    
    def get_onnx_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive ONNX optimization report"""
        return self.onnx_integration.get_all_optimization_reports()