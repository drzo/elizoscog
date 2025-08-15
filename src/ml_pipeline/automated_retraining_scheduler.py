"""
Phase 5: Automated Model Retraining Scheduler

Implements scheduled model retraining, performance monitoring, and automated
model lifecycle management for continuous learning systems.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import threading
import time
from pathlib import Path

from .ml_model_pipeline import MLModelPipeline, ModelConfig, PipelineStage

logger = logging.getLogger(__name__)


class RetrainingTrigger(Enum):
    """Types of retraining triggers"""
    SCHEDULED = "scheduled"
    PERFORMANCE_DECAY = "performance_decay"
    DATA_DRIFT = "data_drift"
    MODEL_DRIFT = "model_drift"
    MANUAL = "manual"
    CONCEPT_DRIFT = "concept_drift"


class ScheduleFrequency(Enum):
    """Schedule frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM_CRON = "custom_cron"


@dataclass
class RetrainingJob:
    """Automated retraining job configuration"""
    job_id: str
    model_id: str
    name: str
    description: str
    schedule_frequency: ScheduleFrequency
    cron_expression: Optional[str] = None
    triggers: List[RetrainingTrigger] = field(default_factory=list)
    performance_thresholds: Dict[str, float] = field(default_factory=dict)
    drift_thresholds: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True
    max_retries: int = 3
    retry_delay_minutes: int = 30
    notification_settings: Dict[str, Any] = field(default_factory=dict)
    last_execution: Optional[datetime] = None
    last_success: Optional[datetime] = None
    execution_count: int = 0
    failure_count: int = 0


@dataclass
class RetrainingExecution:
    """Retraining execution record"""
    execution_id: str
    job_id: str
    model_id: str
    trigger: RetrainingTrigger
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    trigger_details: Dict[str, Any] = field(default_factory=dict)
    performance_before: Dict[str, float] = field(default_factory=dict)
    performance_after: Dict[str, float] = field(default_factory=dict)
    improvement_metrics: Dict[str, float] = field(default_factory=dict)
    pipeline_execution_id: Optional[str] = None
    error_message: Optional[str] = None
    logs: List[str] = field(default_factory=list)


@dataclass
class ModelPerformanceMetrics:
    """Model performance tracking metrics"""
    model_id: str
    timestamp: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    prediction_latency_ms: float = 0.0
    throughput_qps: float = 0.0
    error_rate: float = 0.0
    data_drift_score: float = 0.0
    model_drift_score: float = 0.0
    concept_drift_score: float = 0.0
    feature_importance_drift: Dict[str, float] = field(default_factory=dict)


class AutomatedRetrainingScheduler:
    """Automated model retraining scheduler and lifecycle manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.ml_pipeline = MLModelPipeline(config.get('ml_pipeline_config', {}))
        
        # Job and execution tracking
        self.jobs: Dict[str, RetrainingJob] = {}
        self.executions: Dict[str, RetrainingExecution] = {}
        self.performance_history: Dict[str, List[ModelPerformanceMetrics]] = {}
        
        # Scheduler state
        self.scheduler_running = False
        self.scheduler_thread = None
        self.notification_handlers: Dict[str, Callable] = {}
        
        # Initialize directories
        self.base_path = Path(self.config.get('base_path', './retraining_scheduler'))
        self.jobs_path = self.base_path / 'jobs'
        self.executions_path = self.base_path / 'executions'
        self.metrics_path = self.base_path / 'metrics'
        
        self._ensure_directories()
        self._initialize_notification_handlers()
        
    def _ensure_directories(self):
        """Create necessary directories"""
        for path in [self.base_path, self.jobs_path, self.executions_path, self.metrics_path]:
            path.mkdir(parents=True, exist_ok=True)
            
    def _initialize_notification_handlers(self):
        """Initialize notification handlers"""
        self.notification_handlers = {
            'email': self._send_email_notification,
            'webhook': self._send_webhook_notification,
            'slack': self._send_slack_notification,
            'console': self._send_console_notification
        }
    
    async def register_retraining_job(self, job: RetrainingJob):
        """Register a new automated retraining job"""
        self.jobs[job.job_id] = job
        
        # Validate schedule
        if job.schedule_frequency == ScheduleFrequency.CUSTOM_CRON and not job.cron_expression:
            raise ValueError("Custom cron schedule requires cron_expression")
            
        # Save job configuration
        job_config_path = self.jobs_path / f"{job.job_id}.json"
        with open(job_config_path, 'w') as f:
            job_dict = {
                'job_id': job.job_id,
                'model_id': job.model_id,
                'name': job.name,
                'description': job.description,
                'schedule_frequency': job.schedule_frequency.value,
                'cron_expression': job.cron_expression,
                'triggers': [t.value for t in job.triggers],
                'performance_thresholds': job.performance_thresholds,
                'drift_thresholds': job.drift_thresholds,
                'enabled': job.enabled,
                'max_retries': job.max_retries,
                'retry_delay_minutes': job.retry_delay_minutes,
                'notification_settings': job.notification_settings,
                'last_execution': job.last_execution.isoformat() if job.last_execution else None,
                'last_success': job.last_success.isoformat() if job.last_success else None,
                'execution_count': job.execution_count,
                'failure_count': job.failure_count
            }
            json.dump(job_dict, f, indent=2)
            
        logger.info(f"Registered retraining job {job.job_id} for model {job.model_id}")
    
    def start_scheduler(self):
        """Start the automated retraining scheduler"""
        if self.scheduler_running:
            logger.warning("Scheduler is already running")
            return
            
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Started automated retraining scheduler")
    
    def stop_scheduler(self):
        """Stop the automated retraining scheduler"""
        if not self.scheduler_running:
            logger.warning("Scheduler is not running")
            return
            
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        logger.info("Stopped automated retraining scheduler")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.scheduler_running:
            try:
                # Check scheduled jobs
                asyncio.run(self._check_scheduled_jobs())
                
                # Check trigger-based jobs
                asyncio.run(self._check_trigger_jobs())
                
                # Clean up old executions
                self._cleanup_old_executions()
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
                
        logger.info("Scheduler loop stopped")
    
    async def _check_scheduled_jobs(self):
        """Check for jobs that need to run based on schedule"""
        current_time = datetime.now()
        
        for job in self.jobs.values():
            if not job.enabled:
                continue
                
            if not RetrainingTrigger.SCHEDULED in job.triggers:
                continue
                
            should_run = False
            
            if job.schedule_frequency == ScheduleFrequency.HOURLY:
                if not job.last_execution or (current_time - job.last_execution) >= timedelta(hours=1):
                    should_run = True
                    
            elif job.schedule_frequency == ScheduleFrequency.DAILY:
                if not job.last_execution or (current_time - job.last_execution) >= timedelta(days=1):
                    should_run = True
                    
            elif job.schedule_frequency == ScheduleFrequency.WEEKLY:
                if not job.last_execution or (current_time - job.last_execution) >= timedelta(weeks=1):
                    should_run = True
                    
            elif job.schedule_frequency == ScheduleFrequency.MONTHLY:
                if not job.last_execution or (current_time - job.last_execution) >= timedelta(days=30):
                    should_run = True
                    
            elif job.schedule_frequency == ScheduleFrequency.CUSTOM_CRON:
                # Simplified cron check - in production would use proper cron library
                should_run = self._should_run_cron_job(job)
                
            if should_run:
                await self._execute_retraining_job(job.job_id, RetrainingTrigger.SCHEDULED)
    
    def _should_run_cron_job(self, job: RetrainingJob) -> bool:
        """Check if cron job should run (simplified implementation)"""
        if not job.cron_expression:
            return False
            
        # This is a simplified implementation
        # In production, use a proper cron library like python-crontab
        current_time = datetime.now()
        
        if job.cron_expression == "0 0 * * *":  # Daily at midnight
            if not job.last_execution or (current_time - job.last_execution) >= timedelta(days=1):
                return current_time.hour == 0 and current_time.minute == 0
                
        elif job.cron_expression == "0 * * * *":  # Every hour
            if not job.last_execution or (current_time - job.last_execution) >= timedelta(hours=1):
                return current_time.minute == 0
                
        return False
    
    async def _check_trigger_jobs(self):
        """Check for jobs that need to run based on performance/drift triggers"""
        for job in self.jobs.values():
            if not job.enabled:
                continue
                
            model_id = job.model_id
            
            # Get latest performance metrics
            if model_id not in self.performance_history or not self.performance_history[model_id]:
                continue
                
            latest_metrics = self.performance_history[model_id][-1]
            
            # Check performance decay trigger
            if RetrainingTrigger.PERFORMANCE_DECAY in job.triggers:
                if await self._check_performance_decay(job, latest_metrics):
                    await self._execute_retraining_job(job.job_id, RetrainingTrigger.PERFORMANCE_DECAY)
                    continue
                    
            # Check data drift trigger
            if RetrainingTrigger.DATA_DRIFT in job.triggers:
                if await self._check_data_drift(job, latest_metrics):
                    await self._execute_retraining_job(job.job_id, RetrainingTrigger.DATA_DRIFT)
                    continue
                    
            # Check model drift trigger
            if RetrainingTrigger.MODEL_DRIFT in job.triggers:
                if await self._check_model_drift(job, latest_metrics):
                    await self._execute_retraining_job(job.job_id, RetrainingTrigger.MODEL_DRIFT)
                    continue
                    
            # Check concept drift trigger
            if RetrainingTrigger.CONCEPT_DRIFT in job.triggers:
                if await self._check_concept_drift(job, latest_metrics):
                    await self._execute_retraining_job(job.job_id, RetrainingTrigger.CONCEPT_DRIFT)
                    continue
    
    async def _check_performance_decay(self, job: RetrainingJob, metrics: ModelPerformanceMetrics) -> bool:
        """Check if model performance has decayed below threshold"""
        for metric_name, threshold in job.performance_thresholds.items():
            if hasattr(metrics, metric_name):
                current_value = getattr(metrics, metric_name)
                if current_value < threshold:
                    logger.info(f"Performance decay detected for model {job.model_id}: "
                              f"{metric_name}={current_value} < {threshold}")
                    return True
        return False
    
    async def _check_data_drift(self, job: RetrainingJob, metrics: ModelPerformanceMetrics) -> bool:
        """Check if data drift has exceeded threshold"""
        threshold = job.drift_thresholds.get('data_drift', 0.5)
        if metrics.data_drift_score > threshold:
            logger.info(f"Data drift detected for model {job.model_id}: "
                       f"score={metrics.data_drift_score} > {threshold}")
            return True
        return False
    
    async def _check_model_drift(self, job: RetrainingJob, metrics: ModelPerformanceMetrics) -> bool:
        """Check if model drift has exceeded threshold"""
        threshold = job.drift_thresholds.get('model_drift', 0.3)
        if metrics.model_drift_score > threshold:
            logger.info(f"Model drift detected for model {job.model_id}: "
                       f"score={metrics.model_drift_score} > {threshold}")
            return True
        return False
    
    async def _check_concept_drift(self, job: RetrainingJob, metrics: ModelPerformanceMetrics) -> bool:
        """Check if concept drift has exceeded threshold"""
        threshold = job.drift_thresholds.get('concept_drift', 0.4)
        if metrics.concept_drift_score > threshold:
            logger.info(f"Concept drift detected for model {job.model_id}: "
                       f"score={metrics.concept_drift_score} > {threshold}")
            return True
        return False
    
    async def _execute_retraining_job(self, job_id: str, trigger: RetrainingTrigger, 
                                    trigger_details: Optional[Dict[str, Any]] = None) -> str:
        """Execute a retraining job"""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
            
        job = self.jobs[job_id]
        
        execution_id = f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(trigger)) % 10000}"
        
        # Get current performance metrics
        current_metrics = {}
        if job.model_id in self.performance_history and self.performance_history[job.model_id]:
            latest_metrics = self.performance_history[job.model_id][-1]
            current_metrics = {
                'accuracy': latest_metrics.accuracy,
                'precision': latest_metrics.precision,
                'recall': latest_metrics.recall,
                'f1_score': latest_metrics.f1_score
            }
        
        execution = RetrainingExecution(
            execution_id=execution_id,
            job_id=job_id,
            model_id=job.model_id,
            trigger=trigger,
            start_time=datetime.now(),
            trigger_details=trigger_details or {},
            performance_before=current_metrics
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Update job tracking
            job.last_execution = execution.start_time
            job.execution_count += 1
            
            # Send start notification
            await self._send_notification(job, f"Retraining started for model {job.model_id}", 
                                        'retraining_started', {'execution_id': execution_id})
            
            # Execute retraining pipeline
            execution.logs.append(f"Starting retraining pipeline for trigger: {trigger.value}")
            
            pipeline_stages = [
                PipelineStage.DATA_COLLECTION,
                PipelineStage.DATA_PREPROCESSING,
                PipelineStage.FEATURE_ENGINEERING,
                PipelineStage.MODEL_TRAINING,
                PipelineStage.MODEL_VALIDATION,
                PipelineStage.MODEL_DEPLOYMENT
            ]
            
            pipeline_execution_id = await self.ml_pipeline.execute_pipeline(job.model_id, pipeline_stages)
            execution.pipeline_execution_id = pipeline_execution_id
            execution.logs.append(f"Pipeline execution started: {pipeline_execution_id}")
            
            # Wait for pipeline completion (simplified - in practice would be async)
            pipeline_status = self.ml_pipeline.get_execution_status(pipeline_execution_id)
            
            if pipeline_status.get('status') == 'completed':
                # Get new performance metrics
                validation_results = pipeline_status.get('results', {}).get('model_validation', {})
                execution.performance_after = {
                    'accuracy': validation_results.get('accuracy', 0),
                    'precision': validation_results.get('precision', 0),
                    'recall': validation_results.get('recall', 0),
                    'f1_score': validation_results.get('f1_score', 0)
                }
                
                # Calculate improvement metrics
                execution.improvement_metrics = {}
                for metric, after_value in execution.performance_after.items():
                    if metric in execution.performance_before:
                        before_value = execution.performance_before[metric]
                        improvement = after_value - before_value
                        execution.improvement_metrics[f"{metric}_improvement"] = improvement
                        execution.improvement_metrics[f"{metric}_improvement_pct"] = (
                            improvement / before_value * 100 if before_value > 0 else 0
                        )
                
                execution.status = "completed"
                execution.end_time = datetime.now()
                job.last_success = execution.end_time
                
                # Send success notification
                await self._send_notification(job, f"Retraining completed successfully for model {job.model_id}", 
                                            'retraining_completed', {
                                                'execution_id': execution_id,
                                                'improvement_metrics': execution.improvement_metrics
                                            })
                
            else:
                execution.status = "failed"
                execution.end_time = datetime.now()
                execution.error_message = f"Pipeline execution failed: {pipeline_status.get('status')}"
                job.failure_count += 1
                
                # Send failure notification
                await self._send_notification(job, f"Retraining failed for model {job.model_id}", 
                                            'retraining_failed', {
                                                'execution_id': execution_id,
                                                'error_message': execution.error_message
                                            })
                
        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now()
            execution.error_message = str(e)
            job.failure_count += 1
            
            logger.error(f"Retraining execution {execution_id} failed: {e}")
            
            # Send failure notification
            await self._send_notification(job, f"Retraining failed for model {job.model_id}: {str(e)}", 
                                        'retraining_failed', {
                                            'execution_id': execution_id,
                                            'error_message': execution.error_message
                                        })
        
        # Save execution record
        await self._save_execution_record(execution)
        
        # Update job configuration
        await self._update_job_config(job)
        
        logger.info(f"Retraining execution {execution_id} completed with status: {execution.status}")
        return execution_id
    
    async def record_model_performance(self, metrics: ModelPerformanceMetrics):
        """Record model performance metrics for monitoring"""
        model_id = metrics.model_id
        
        if model_id not in self.performance_history:
            self.performance_history[model_id] = []
            
        self.performance_history[model_id].append(metrics)
        
        # Keep only recent history (last 1000 records)
        if len(self.performance_history[model_id]) > 1000:
            self.performance_history[model_id] = self.performance_history[model_id][-1000:]
        
        # Save metrics to file
        metrics_file = self.metrics_path / f"{model_id}_metrics.json"
        metrics_data = []
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                metrics_data = json.load(f)
        
        metrics_data.append({
            'model_id': metrics.model_id,
            'timestamp': metrics.timestamp.isoformat(),
            'accuracy': metrics.accuracy,
            'precision': metrics.precision,
            'recall': metrics.recall,
            'f1_score': metrics.f1_score,
            'auc_roc': metrics.auc_roc,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'prediction_latency_ms': metrics.prediction_latency_ms,
            'throughput_qps': metrics.throughput_qps,
            'error_rate': metrics.error_rate,
            'data_drift_score': metrics.data_drift_score,
            'model_drift_score': metrics.model_drift_score,
            'concept_drift_score': metrics.concept_drift_score,
            'feature_importance_drift': metrics.feature_importance_drift
        })
        
        # Keep only recent records in file
        if len(metrics_data) > 10000:
            metrics_data = metrics_data[-10000:]
            
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f)
        
        logger.debug(f"Recorded performance metrics for model {model_id}")
    
    async def trigger_manual_retraining(self, job_id: str, reason: str = "Manual trigger") -> str:
        """Manually trigger retraining for a job"""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
            
        trigger_details = {'reason': reason, 'triggered_by': 'manual'}
        
        return await self._execute_retraining_job(job_id, RetrainingTrigger.MANUAL, trigger_details)
    
    async def _send_notification(self, job: RetrainingJob, message: str, event_type: str, 
                               context: Dict[str, Any]):
        """Send notification using configured handlers"""
        if not job.notification_settings:
            return
            
        for handler_type, config in job.notification_settings.items():
            if handler_type in self.notification_handlers and config.get('enabled', False):
                try:
                    await self.notification_handlers[handler_type](job, message, event_type, context, config)
                except Exception as e:
                    logger.error(f"Failed to send {handler_type} notification: {e}")
    
    async def _send_email_notification(self, job: RetrainingJob, message: str, event_type: str, 
                                     context: Dict[str, Any], config: Dict[str, Any]):
        """Send email notification (mock implementation)"""
        logger.info(f"EMAIL NOTIFICATION [{event_type}] for job {job.job_id}: {message}")
        # In production: integrate with email service (SMTP, SendGrid, etc.)
    
    async def _send_webhook_notification(self, job: RetrainingJob, message: str, event_type: str, 
                                       context: Dict[str, Any], config: Dict[str, Any]):
        """Send webhook notification (mock implementation)"""
        webhook_url = config.get('url')
        logger.info(f"WEBHOOK NOTIFICATION to {webhook_url} [{event_type}] for job {job.job_id}: {message}")
        # In production: make HTTP POST request to webhook URL
    
    async def _send_slack_notification(self, job: RetrainingJob, message: str, event_type: str, 
                                     context: Dict[str, Any], config: Dict[str, Any]):
        """Send Slack notification (mock implementation)"""
        channel = config.get('channel', '#ml-alerts')
        logger.info(f"SLACK NOTIFICATION to {channel} [{event_type}] for job {job.job_id}: {message}")
        # In production: integrate with Slack API
    
    async def _send_console_notification(self, job: RetrainingJob, message: str, event_type: str, 
                                       context: Dict[str, Any], config: Dict[str, Any]):
        """Send console notification"""
        print(f"RETRAINING ALERT [{event_type}] Job: {job.job_id} - {message}")
    
    async def _save_execution_record(self, execution: RetrainingExecution):
        """Save execution record to file"""
        execution_file = self.executions_path / f"{execution.execution_id}.json"
        
        execution_dict = {
            'execution_id': execution.execution_id,
            'job_id': execution.job_id,
            'model_id': execution.model_id,
            'trigger': execution.trigger.value,
            'start_time': execution.start_time.isoformat(),
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'status': execution.status,
            'trigger_details': execution.trigger_details,
            'performance_before': execution.performance_before,
            'performance_after': execution.performance_after,
            'improvement_metrics': execution.improvement_metrics,
            'pipeline_execution_id': execution.pipeline_execution_id,
            'error_message': execution.error_message,
            'logs': execution.logs
        }
        
        with open(execution_file, 'w') as f:
            json.dump(execution_dict, f, indent=2)
    
    async def _update_job_config(self, job: RetrainingJob):
        """Update job configuration file"""
        job_config_path = self.jobs_path / f"{job.job_id}.json"
        
        job_dict = {
            'job_id': job.job_id,
            'model_id': job.model_id,
            'name': job.name,
            'description': job.description,
            'schedule_frequency': job.schedule_frequency.value,
            'cron_expression': job.cron_expression,
            'triggers': [t.value for t in job.triggers],
            'performance_thresholds': job.performance_thresholds,
            'drift_thresholds': job.drift_thresholds,
            'enabled': job.enabled,
            'max_retries': job.max_retries,
            'retry_delay_minutes': job.retry_delay_minutes,
            'notification_settings': job.notification_settings,
            'last_execution': job.last_execution.isoformat() if job.last_execution else None,
            'last_success': job.last_success.isoformat() if job.last_success else None,
            'execution_count': job.execution_count,
            'failure_count': job.failure_count
        }
        
        with open(job_config_path, 'w') as f:
            json.dump(job_dict, f, indent=2)
    
    def _cleanup_old_executions(self):
        """Clean up old execution records"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for execution_id, execution in list(self.executions.items()):
            if execution.start_time < cutoff_date:
                # Remove from memory
                del self.executions[execution_id]
                
                # Remove file
                execution_file = self.executions_path / f"{execution_id}.json"
                if execution_file.exists():
                    execution_file.unlink()
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a retraining job"""
        if job_id not in self.jobs:
            return {'error': 'Job not found'}
            
        job = self.jobs[job_id]
        
        # Get recent executions
        recent_executions = [
            {
                'execution_id': exec_id,
                'start_time': execution.start_time.isoformat(),
                'status': execution.status,
                'trigger': execution.trigger.value
            }
            for exec_id, execution in self.executions.items()
            if execution.job_id == job_id
        ]
        
        # Sort by start time (most recent first)
        recent_executions.sort(key=lambda x: x['start_time'], reverse=True)
        recent_executions = recent_executions[:10]  # Last 10 executions
        
        return {
            'job_id': job.job_id,
            'model_id': job.model_id,
            'name': job.name,
            'enabled': job.enabled,
            'schedule_frequency': job.schedule_frequency.value,
            'triggers': [t.value for t in job.triggers],
            'last_execution': job.last_execution.isoformat() if job.last_execution else None,
            'last_success': job.last_success.isoformat() if job.last_success else None,
            'execution_count': job.execution_count,
            'failure_count': job.failure_count,
            'success_rate': (job.execution_count - job.failure_count) / job.execution_count * 100 if job.execution_count > 0 else 0,
            'recent_executions': recent_executions
        }
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all retraining jobs"""
        return [self.get_job_status(job_id) for job_id in self.jobs.keys()]
    
    def get_model_performance_history(self, model_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get performance history for a model"""
        if model_id not in self.performance_history:
            return []
            
        history = self.performance_history[model_id][-limit:]
        
        return [
            {
                'timestamp': metrics.timestamp.isoformat(),
                'accuracy': metrics.accuracy,
                'precision': metrics.precision,
                'recall': metrics.recall,
                'f1_score': metrics.f1_score,
                'data_drift_score': metrics.data_drift_score,
                'model_drift_score': metrics.model_drift_score,
                'concept_drift_score': metrics.concept_drift_score
            }
            for metrics in history
        ]