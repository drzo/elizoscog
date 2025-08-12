"""
Phase 5: Model Drift Detection and Performance Monitoring

Implements comprehensive model drift detection, performance monitoring,
and quality assurance for production ML models.
"""

import asyncio
import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of model drift"""
    DATA_DRIFT = "data_drift"
    MODEL_DRIFT = "model_drift"  
    CONCEPT_DRIFT = "concept_drift"
    FEATURE_DRIFT = "feature_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"


class DriftSeverity(Enum):
    """Drift severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MonitoringAlert(Enum):
    """Types of monitoring alerts"""
    DRIFT_DETECTED = "drift_detected"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MODEL_ERROR = "model_error"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    LATENCY_SPIKE = "latency_spike"
    THROUGHPUT_DROP = "throughput_drop"


@dataclass
class DriftDetectionResult:
    """Result of drift detection analysis"""
    drift_id: str
    model_id: str
    drift_type: DriftType
    severity: DriftSeverity
    score: float
    threshold: float
    detection_time: datetime
    affected_features: List[str] = field(default_factory=list)
    statistical_tests: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    explanation: str = ""
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMonitoringMetrics:
    """Comprehensive model monitoring metrics"""
    model_id: str
    timestamp: datetime
    
    # Performance metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: Optional[float] = None
    
    # Operational metrics
    prediction_latency_ms: float = 0.0
    throughput_qps: float = 0.0
    error_rate: float = 0.0
    availability: float = 1.0
    
    # Data quality metrics
    missing_value_rate: float = 0.0
    outlier_rate: float = 0.0
    schema_violations: int = 0
    data_completeness: float = 1.0
    
    # Drift scores
    data_drift_score: float = 0.0
    model_drift_score: float = 0.0
    concept_drift_score: float = 0.0
    feature_drift_scores: Dict[str, float] = field(default_factory=dict)
    
    # Distribution statistics
    feature_distributions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    prediction_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Model-specific metrics (financial)
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None


@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    report_id: str
    model_id: str
    timestamp: datetime
    sample_size: int
    
    # Quality metrics
    completeness_score: float
    validity_score: float
    consistency_score: float
    uniqueness_score: float
    overall_quality_score: float
    
    # Issue details
    missing_values: Dict[str, int] = field(default_factory=dict)
    invalid_values: Dict[str, int] = field(default_factory=dict)
    duplicate_records: int = 0
    schema_violations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommendations
    quality_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ModelDriftDetector:
    """Comprehensive model drift detection and monitoring system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Detection thresholds
        self.drift_thresholds = self.config.get('drift_thresholds', {
            'data_drift': 0.3,
            'model_drift': 0.25,
            'concept_drift': 0.4,
            'feature_drift': 0.2,
            'performance_drift': 0.05
        })
        
        # Monitoring configuration
        self.monitoring_window_days = self.config.get('monitoring_window_days', 30)
        self.min_samples_for_detection = self.config.get('min_samples_for_detection', 100)
        self.statistical_significance_level = self.config.get('statistical_significance_level', 0.05)
        
        # Storage
        self.base_path = Path(self.config.get('base_path', './model_monitoring'))
        self.drift_reports_path = self.base_path / 'drift_reports'
        self.metrics_path = self.base_path / 'metrics'
        self.quality_reports_path = self.base_path / 'quality_reports'
        
        # Data storage
        self.baseline_distributions: Dict[str, Dict[str, Any]] = {}
        self.drift_history: Dict[str, List[DriftDetectionResult]] = {}
        self.monitoring_metrics: Dict[str, List[ModelMonitoringMetrics]] = {}
        self.quality_reports: Dict[str, List[DataQualityReport]] = {}
        
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create necessary directories"""
        for path in [self.base_path, self.drift_reports_path, 
                     self.metrics_path, self.quality_reports_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def establish_baseline(self, model_id: str, baseline_data: List[Dict[str, Any]], 
                               baseline_predictions: List[float]):
        """Establish baseline distributions for drift detection"""
        
        if not baseline_data or len(baseline_data) < self.min_samples_for_detection:
            raise ValueError(f"Insufficient baseline data: need at least {self.min_samples_for_detection} samples")
        
        baseline = {
            'model_id': model_id,
            'established_at': datetime.now().isoformat(),
            'sample_size': len(baseline_data),
            'feature_distributions': {},
            'prediction_distribution': {},
            'correlation_matrix': {},
            'statistical_properties': {}
        }
        
        # Calculate feature distributions
        if baseline_data:
            feature_names = set()
            for sample in baseline_data:
                feature_names.update(sample.keys())
            
            for feature in feature_names:
                values = [sample.get(feature, 0) for sample in baseline_data if feature in sample]
                if values and all(isinstance(v, (int, float)) for v in values):
                    baseline['feature_distributions'][feature] = {
                        'mean': statistics.mean(values),
                        'std': statistics.stdev(values) if len(values) > 1 else 0,
                        'min': min(values),
                        'max': max(values),
                        'median': statistics.median(values),
                        'q25': self._calculate_percentile(values, 25),
                        'q75': self._calculate_percentile(values, 75),
                        'skewness': self._calculate_skewness(values),
                        'kurtosis': self._calculate_kurtosis(values)
                    }
        
        # Calculate prediction distribution
        if baseline_predictions:
            baseline['prediction_distribution'] = {
                'mean': statistics.mean(baseline_predictions),
                'std': statistics.stdev(baseline_predictions) if len(baseline_predictions) > 1 else 0,
                'min': min(baseline_predictions),
                'max': max(baseline_predictions),
                'median': statistics.median(baseline_predictions),
                'q25': self._calculate_percentile(baseline_predictions, 25),
                'q75': self._calculate_percentile(baseline_predictions, 75)
            }
        
        self.baseline_distributions[model_id] = baseline
        
        # Save baseline
        baseline_file = self.metrics_path / f"{model_id}_baseline.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
            
        logger.info(f"Established baseline for model {model_id} with {len(baseline_data)} samples")
    
    async def detect_drift(self, model_id: str, current_data: List[Dict[str, Any]], 
                          current_predictions: List[float], 
                          current_labels: Optional[List[float]] = None) -> List[DriftDetectionResult]:
        """Detect various types of drift in model data and predictions"""
        
        if model_id not in self.baseline_distributions:
            raise ValueError(f"No baseline established for model {model_id}")
        
        if len(current_data) < self.min_samples_for_detection:
            logger.warning(f"Insufficient current data for drift detection: {len(current_data)} samples")
            return []
        
        baseline = self.baseline_distributions[model_id]
        drift_results = []
        
        # Data drift detection
        data_drift = await self._detect_data_drift(model_id, baseline, current_data)
        if data_drift:
            drift_results.append(data_drift)
        
        # Feature-level drift detection
        feature_drifts = await self._detect_feature_drift(model_id, baseline, current_data)
        drift_results.extend(feature_drifts)
        
        # Prediction drift detection
        prediction_drift = await self._detect_prediction_drift(model_id, baseline, current_predictions)
        if prediction_drift:
            drift_results.append(prediction_drift)
        
        # Concept drift detection (if labels available)
        if current_labels:
            concept_drift = await self._detect_concept_drift(model_id, current_data, 
                                                           current_predictions, current_labels)
            if concept_drift:
                drift_results.append(concept_drift)
        
        # Model performance drift (if labels available)
        if current_labels:
            performance_drift = await self._detect_performance_drift(model_id, current_predictions, 
                                                                   current_labels)
            if performance_drift:
                drift_results.append(performance_drift)
        
        # Store drift results
        if model_id not in self.drift_history:
            self.drift_history[model_id] = []
        self.drift_history[model_id].extend(drift_results)
        
        # Save drift reports
        for drift_result in drift_results:
            await self._save_drift_report(drift_result)
        
        logger.info(f"Detected {len(drift_results)} drift issues for model {model_id}")
        return drift_results
    
    async def _detect_data_drift(self, model_id: str, baseline: Dict[str, Any], 
                               current_data: List[Dict[str, Any]]) -> Optional[DriftDetectionResult]:
        """Detect overall data drift using multiple statistical tests"""
        
        # Calculate KL divergence for numeric features
        kl_divergences = []
        js_divergences = []
        
        for feature, baseline_dist in baseline['feature_distributions'].items():
            current_values = [sample.get(feature, 0) for sample in current_data if feature in sample]
            if not current_values:
                continue
                
            # Calculate current distribution
            current_stats = self._calculate_distribution_stats(current_values)
            
            # KL divergence approximation
            kl_div = self._approximate_kl_divergence(baseline_dist, current_stats)
            if kl_div is not None:
                kl_divergences.append(kl_div)
            
            # Jensen-Shannon divergence
            js_div = self._calculate_js_divergence(baseline_dist, current_stats)
            if js_div is not None:
                js_divergences.append(js_div)
        
        if not kl_divergences and not js_divergences:
            return None
        
        # Calculate overall data drift score
        avg_kl_div = statistics.mean(kl_divergences) if kl_divergences else 0
        avg_js_div = statistics.mean(js_divergences) if js_divergences else 0
        
        # Combined drift score (weighted average)
        drift_score = (avg_kl_div * 0.6 + avg_js_div * 0.4) if avg_js_div > 0 else avg_kl_div
        
        threshold = self.drift_thresholds['data_drift']
        
        if drift_score > threshold:
            severity = self._determine_drift_severity(drift_score, threshold)
            
            return DriftDetectionResult(
                drift_id=self._generate_drift_id(model_id, DriftType.DATA_DRIFT),
                model_id=model_id,
                drift_type=DriftType.DATA_DRIFT,
                severity=severity,
                score=drift_score,
                threshold=threshold,
                detection_time=datetime.now(),
                statistical_tests={
                    'kl_divergence': {'mean': avg_kl_div, 'values': kl_divergences},
                    'js_divergence': {'mean': avg_js_div, 'values': js_divergences}
                },
                explanation=f"Data distribution has shifted significantly (score: {drift_score:.3f})",
                recommendations=[
                    "Investigate data source changes",
                    "Consider model retraining",
                    "Review data preprocessing pipeline",
                    "Check for data quality issues"
                ]
            )
        
        return None
    
    async def _detect_feature_drift(self, model_id: str, baseline: Dict[str, Any], 
                                  current_data: List[Dict[str, Any]]) -> List[DriftDetectionResult]:
        """Detect drift in individual features"""
        
        feature_drifts = []
        threshold = self.drift_thresholds['feature_drift']
        
        for feature, baseline_dist in baseline['feature_distributions'].items():
            current_values = [sample.get(feature, 0) for sample in current_data if feature in sample]
            if len(current_values) < self.min_samples_for_detection:
                continue
            
            current_stats = self._calculate_distribution_stats(current_values)
            
            # Kolmogorov-Smirnov test approximation
            ks_statistic = self._approximate_ks_statistic(baseline_dist, current_stats)
            
            # Population Stability Index (PSI)
            psi_score = self._calculate_psi(baseline_dist, current_stats)
            
            # Combined feature drift score
            drift_score = (ks_statistic * 0.6 + psi_score * 0.4) if psi_score is not None else ks_statistic
            
            if drift_score > threshold:
                severity = self._determine_drift_severity(drift_score, threshold)
                
                feature_drifts.append(DriftDetectionResult(
                    drift_id=self._generate_drift_id(model_id, DriftType.FEATURE_DRIFT, feature),
                    model_id=model_id,
                    drift_type=DriftType.FEATURE_DRIFT,
                    severity=severity,
                    score=drift_score,
                    threshold=threshold,
                    detection_time=datetime.now(),
                    affected_features=[feature],
                    statistical_tests={
                        'ks_statistic': ks_statistic,
                        'psi_score': psi_score,
                        'baseline_stats': baseline_dist,
                        'current_stats': current_stats
                    },
                    explanation=f"Feature '{feature}' distribution has drifted (score: {drift_score:.3f})",
                    recommendations=[
                        f"Investigate changes in feature '{feature}'",
                        "Check feature engineering pipeline",
                        "Validate data source for this feature",
                        "Consider feature-specific preprocessing adjustments"
                    ]
                ))
        
        return feature_drifts
    
    async def _detect_prediction_drift(self, model_id: str, baseline: Dict[str, Any], 
                                     current_predictions: List[float]) -> Optional[DriftDetectionResult]:
        """Detect drift in model predictions"""
        
        if 'prediction_distribution' not in baseline or not current_predictions:
            return None
        
        baseline_pred_dist = baseline['prediction_distribution']
        current_pred_stats = self._calculate_distribution_stats(current_predictions)
        
        # Calculate prediction drift metrics
        mean_shift = abs(current_pred_stats['mean'] - baseline_pred_dist['mean'])
        std_change = abs(current_pred_stats['std'] - baseline_pred_dist['std'])
        
        # Normalize by baseline values
        normalized_mean_shift = mean_shift / (abs(baseline_pred_dist['mean']) + 1e-6)
        normalized_std_change = std_change / (baseline_pred_dist['std'] + 1e-6)
        
        # Combined prediction drift score
        drift_score = (normalized_mean_shift + normalized_std_change) / 2
        
        threshold = self.drift_thresholds.get('prediction_drift', 0.2)
        
        if drift_score > threshold:
            severity = self._determine_drift_severity(drift_score, threshold)
            
            return DriftDetectionResult(
                drift_id=self._generate_drift_id(model_id, DriftType.PREDICTION_DRIFT),
                model_id=model_id,
                drift_type=DriftType.PREDICTION_DRIFT,
                severity=severity,
                score=drift_score,
                threshold=threshold,
                detection_time=datetime.now(),
                statistical_tests={
                    'mean_shift': mean_shift,
                    'std_change': std_change,
                    'normalized_mean_shift': normalized_mean_shift,
                    'normalized_std_change': normalized_std_change,
                    'baseline_distribution': baseline_pred_dist,
                    'current_distribution': current_pred_stats
                },
                explanation=f"Model prediction distribution has shifted (score: {drift_score:.3f})",
                recommendations=[
                    "Investigate model behavior changes",
                    "Check for input data changes",
                    "Validate model integrity",
                    "Consider model retraining"
                ]
            )
        
        return None
    
    async def _detect_concept_drift(self, model_id: str, current_data: List[Dict[str, Any]], 
                                  current_predictions: List[float], 
                                  current_labels: List[float]) -> Optional[DriftDetectionResult]:
        """Detect concept drift using prediction accuracy over time"""
        
        if len(current_predictions) != len(current_labels):
            return None
        
        # Calculate current accuracy
        correct_predictions = sum(1 for pred, label in zip(current_predictions, current_labels) 
                                if abs(pred - label) < 0.5)  # Adjust threshold as needed
        current_accuracy = correct_predictions / len(current_labels)
        
        # Get historical accuracy (from monitoring metrics)
        historical_accuracies = []
        if model_id in self.monitoring_metrics:
            recent_metrics = self.monitoring_metrics[model_id][-10:]  # Last 10 records
            historical_accuracies = [m.accuracy for m in recent_metrics if m.accuracy > 0]
        
        if not historical_accuracies:
            return None  # No historical data to compare
        
        # Calculate concept drift score
        baseline_accuracy = statistics.mean(historical_accuracies)
        accuracy_drop = baseline_accuracy - current_accuracy
        
        # Normalize by baseline accuracy
        drift_score = accuracy_drop / baseline_accuracy if baseline_accuracy > 0 else 0
        
        threshold = self.drift_thresholds['concept_drift']
        
        if drift_score > threshold:
            severity = self._determine_drift_severity(drift_score, threshold)
            
            return DriftDetectionResult(
                drift_id=self._generate_drift_id(model_id, DriftType.CONCEPT_DRIFT),
                model_id=model_id,
                drift_type=DriftType.CONCEPT_DRIFT,
                severity=severity,
                score=drift_score,
                threshold=threshold,
                detection_time=datetime.now(),
                statistical_tests={
                    'current_accuracy': current_accuracy,
                    'baseline_accuracy': baseline_accuracy,
                    'accuracy_drop': accuracy_drop,
                    'historical_accuracies': historical_accuracies
                },
                explanation=f"Model accuracy has dropped significantly indicating concept drift (score: {drift_score:.3f})",
                recommendations=[
                    "Investigate changes in data relationships",
                    "Check for environmental changes affecting the target",
                    "Consider immediate model retraining",
                    "Review feature relevance and importance"
                ]
            )
        
        return None
    
    async def _detect_performance_drift(self, model_id: str, current_predictions: List[float], 
                                      current_labels: List[float]) -> Optional[DriftDetectionResult]:
        """Detect performance drift over time"""
        
        if len(current_predictions) != len(current_labels):
            return None
        
        # Calculate current performance metrics
        current_perf = self._calculate_performance_metrics(current_predictions, current_labels)
        
        # Get historical performance
        historical_perfs = []
        if model_id in self.monitoring_metrics:
            recent_metrics = self.monitoring_metrics[model_id][-20:]  # Last 20 records
            for metric in recent_metrics:
                if metric.accuracy > 0:  # Valid metric
                    historical_perfs.append({
                        'accuracy': metric.accuracy,
                        'precision': metric.precision,
                        'recall': metric.recall,
                        'f1_score': metric.f1_score
                    })
        
        if not historical_perfs:
            return None
        
        # Calculate performance drift score
        drift_scores = []
        for metric_name in ['accuracy', 'precision', 'recall', 'f1_score']:
            if metric_name in current_perf and current_perf[metric_name] is not None:
                historical_values = [p[metric_name] for p in historical_perfs if p[metric_name] is not None]
                if historical_values:
                    baseline = statistics.mean(historical_values)
                    current = current_perf[metric_name]
                    if baseline > 0:
                        perf_drop = (baseline - current) / baseline
                        drift_scores.append(max(0, perf_drop))  # Only consider degradation
        
        if not drift_scores:
            return None
        
        drift_score = statistics.mean(drift_scores)
        threshold = self.drift_thresholds['performance_drift']
        
        if drift_score > threshold:
            severity = self._determine_drift_severity(drift_score, threshold)
            
            return DriftDetectionResult(
                drift_id=self._generate_drift_id(model_id, DriftType.PERFORMANCE_DRIFT),
                model_id=model_id,
                drift_type=DriftType.PERFORMANCE_DRIFT,
                severity=severity,
                score=drift_score,
                threshold=threshold,
                detection_time=datetime.now(),
                statistical_tests={
                    'current_performance': current_perf,
                    'historical_performance': {
                        metric: statistics.mean([p[metric] for p in historical_perfs if p[metric] is not None])
                        for metric in ['accuracy', 'precision', 'recall', 'f1_score']
                    },
                    'performance_drops': {
                        f"{metric}_drop": drift_scores[i] if i < len(drift_scores) else 0
                        for i, metric in enumerate(['accuracy', 'precision', 'recall', 'f1_score'])
                    }
                },
                explanation=f"Model performance has degraded significantly (score: {drift_score:.3f})",
                recommendations=[
                    "Immediate model retraining required",
                    "Investigate data quality issues",
                    "Check for model corruption or degradation",
                    "Review model serving infrastructure"
                ]
            )
        
        return None
    
    async def assess_data_quality(self, model_id: str, data_sample: List[Dict[str, Any]], 
                                schema: Optional[Dict[str, Any]] = None) -> DataQualityReport:
        """Assess data quality and generate comprehensive report"""
        
        report_id = self._generate_quality_report_id(model_id)
        timestamp = datetime.now()
        sample_size = len(data_sample)
        
        if not data_sample:
            return DataQualityReport(
                report_id=report_id,
                model_id=model_id,
                timestamp=timestamp,
                sample_size=0,
                completeness_score=0,
                validity_score=0,
                consistency_score=0,
                uniqueness_score=0,
                overall_quality_score=0,
                quality_issues=["No data provided"],
                recommendations=["Ensure data is available for quality assessment"]
            )
        
        # Get expected features from schema or first sample
        expected_features = set(schema.keys()) if schema else set(data_sample[0].keys())
        
        # Completeness assessment
        missing_values = {}
        total_missing = 0
        
        for feature in expected_features:
            missing_count = sum(1 for sample in data_sample if feature not in sample or sample[feature] is None)
            missing_values[feature] = missing_count
            total_missing += missing_count
        
        completeness_score = 1 - (total_missing / (len(expected_features) * sample_size))
        
        # Validity assessment
        invalid_values = {}
        total_invalid = 0
        
        for feature in expected_features:
            invalid_count = 0
            for sample in data_sample:
                if feature in sample and sample[feature] is not None:
                    value = sample[feature]
                    # Basic validity checks
                    if schema and feature in schema:
                        expected_type = schema[feature].get('type')
                        if expected_type == 'numeric' and not isinstance(value, (int, float)):
                            invalid_count += 1
                        elif expected_type == 'string' and not isinstance(value, str):
                            invalid_count += 1
            
            invalid_values[feature] = invalid_count
            total_invalid += invalid_count
        
        validity_score = 1 - (total_invalid / (len(expected_features) * sample_size)) if sample_size > 0 else 0
        
        # Consistency assessment (simplified)
        consistency_score = 0.9  # Mock score - would implement actual consistency checks
        
        # Uniqueness assessment
        duplicate_records = 0
        seen_records = set()
        
        for sample in data_sample:
            record_hash = hashlib.md5(json.dumps(sample, sort_keys=True).encode()).hexdigest()
            if record_hash in seen_records:
                duplicate_records += 1
            else:
                seen_records.add(record_hash)
        
        uniqueness_score = 1 - (duplicate_records / sample_size) if sample_size > 0 else 1
        
        # Overall quality score
        overall_quality_score = (
            completeness_score * 0.3 +
            validity_score * 0.3 +
            consistency_score * 0.2 +
            uniqueness_score * 0.2
        )
        
        # Generate issues and recommendations
        quality_issues = []
        recommendations = []
        
        if completeness_score < 0.9:
            quality_issues.append(f"Data completeness is low ({completeness_score:.2%})")
            recommendations.append("Investigate and fix missing data issues")
        
        if validity_score < 0.95:
            quality_issues.append(f"Data validity issues detected ({validity_score:.2%})")
            recommendations.append("Implement data validation and cleaning procedures")
        
        if duplicate_records > 0:
            quality_issues.append(f"Found {duplicate_records} duplicate records")
            recommendations.append("Implement deduplication process")
        
        if overall_quality_score < 0.8:
            recommendations.append("Overall data quality is below acceptable threshold - comprehensive data cleaning required")
        
        report = DataQualityReport(
            report_id=report_id,
            model_id=model_id,
            timestamp=timestamp,
            sample_size=sample_size,
            completeness_score=completeness_score,
            validity_score=validity_score,
            consistency_score=consistency_score,
            uniqueness_score=uniqueness_score,
            overall_quality_score=overall_quality_score,
            missing_values=missing_values,
            invalid_values=invalid_values,
            duplicate_records=duplicate_records,
            quality_issues=quality_issues,
            recommendations=recommendations
        )
        
        # Store report
        if model_id not in self.quality_reports:
            self.quality_reports[model_id] = []
        self.quality_reports[model_id].append(report)
        
        # Save report
        await self._save_quality_report(report)
        
        logger.info(f"Generated data quality report for model {model_id}: {overall_quality_score:.2%} quality")
        return report
    
    def _calculate_distribution_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate distribution statistics for a list of values"""
        if not values:
            return {}
        
        return {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'median': statistics.median(values),
            'q25': self._calculate_percentile(values, 25),
            'q75': self._calculate_percentile(values, 75),
            'skewness': self._calculate_skewness(values),
            'kurtosis': self._calculate_kurtosis(values)
        }
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_values[int(k)]
        return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)
    
    def _calculate_skewness(self, values: List[float]) -> float:
        """Calculate skewness of distribution"""
        if len(values) < 3:
            return 0
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        if std_val == 0:
            return 0
        n = len(values)
        skewness = sum(((x - mean_val) / std_val) ** 3 for x in values) * n / ((n - 1) * (n - 2))
        return skewness
    
    def _calculate_kurtosis(self, values: List[float]) -> float:
        """Calculate kurtosis of distribution"""
        if len(values) < 4:
            return 0
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        if std_val == 0:
            return 0
        n = len(values)
        kurtosis = sum(((x - mean_val) / std_val) ** 4 for x in values) * n * (n + 1) / ((n - 1) * (n - 2) * (n - 3)) - 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))
        return kurtosis
    
    def _approximate_kl_divergence(self, baseline_dist: Dict[str, float], 
                                  current_dist: Dict[str, float]) -> Optional[float]:
        """Approximate KL divergence between two distributions"""
        try:
            # Simplified KL divergence approximation using distribution moments
            mean_diff = abs(current_dist['mean'] - baseline_dist['mean'])
            std_ratio = current_dist['std'] / (baseline_dist['std'] + 1e-6)
            
            # Approximate KL divergence for normal distributions
            kl_div = math.log(std_ratio) + (baseline_dist['std']**2 + mean_diff**2) / (2 * current_dist['std']**2 + 1e-6) - 0.5
            return max(0, kl_div)
        except (ValueError, ZeroDivisionError):
            return None
    
    def _calculate_js_divergence(self, baseline_dist: Dict[str, float], 
                               current_dist: Dict[str, float]) -> Optional[float]:
        """Calculate Jensen-Shannon divergence (simplified)"""
        try:
            # Simplified JS divergence using distribution moments
            mean_diff = abs(current_dist['mean'] - baseline_dist['mean'])
            std_diff = abs(current_dist['std'] - baseline_dist['std'])
            
            # Normalize by baseline values
            norm_mean_diff = mean_diff / (abs(baseline_dist['mean']) + 1e-6)
            norm_std_diff = std_diff / (baseline_dist['std'] + 1e-6)
            
            js_div = (norm_mean_diff + norm_std_diff) / 2
            return js_div
        except (ValueError, ZeroDivisionError):
            return None
    
    def _approximate_ks_statistic(self, baseline_dist: Dict[str, float], 
                                 current_dist: Dict[str, float]) -> float:
        """Approximate Kolmogorov-Smirnov statistic"""
        # Simplified KS statistic approximation using quantiles
        ks_stats = []
        
        for quantile in [0.25, 0.5, 0.75]:
            baseline_q = self._interpolate_quantile(baseline_dist, quantile)
            current_q = self._interpolate_quantile(current_dist, quantile)
            
            if baseline_q != 0:
                ks_stat = abs(current_q - baseline_q) / abs(baseline_q)
                ks_stats.append(ks_stat)
        
        return max(ks_stats) if ks_stats else 0
    
    def _interpolate_quantile(self, dist: Dict[str, float], quantile: float) -> float:
        """Interpolate quantile from distribution statistics"""
        if quantile == 0.25:
            return dist.get('q25', dist.get('mean', 0))
        elif quantile == 0.5:
            return dist.get('median', dist.get('mean', 0))
        elif quantile == 0.75:
            return dist.get('q75', dist.get('mean', 0))
        else:
            return dist.get('mean', 0)
    
    def _calculate_psi(self, baseline_dist: Dict[str, float], 
                      current_dist: Dict[str, float]) -> Optional[float]:
        """Calculate Population Stability Index (PSI)"""
        try:
            # Simplified PSI calculation using distribution percentages
            # In practice, would use binned distributions
            baseline_mean = baseline_dist['mean']
            current_mean = current_dist['mean']
            
            # Approximate PSI using mean shift
            if baseline_mean == 0:
                return None
            
            ratio = current_mean / baseline_mean
            psi = (current_mean - baseline_mean) * math.log(ratio + 1e-6)
            return abs(psi)
        except (ValueError, ZeroDivisionError):
            return None
    
    def _calculate_performance_metrics(self, predictions: List[float], 
                                     labels: List[float]) -> Dict[str, Optional[float]]:
        """Calculate performance metrics from predictions and labels"""
        if len(predictions) != len(labels) or not predictions:
            return {}
        
        # For regression-like predictions, calculate MAE-based accuracy
        mae = statistics.mean([abs(pred - label) for pred, label in zip(predictions, labels)])
        max_error = max([abs(pred - label) for pred, label in zip(predictions, labels)])
        
        # Convert to accuracy-like metric
        accuracy = max(0, 1 - mae) if mae < 1 else 0
        
        # For classification-like metrics, use thresholding
        threshold = 0.5
        binary_preds = [1 if pred > threshold else 0 for pred in predictions]
        binary_labels = [1 if label > threshold else 0 for label in labels]
        
        tp = sum(1 for p, l in zip(binary_preds, binary_labels) if p == 1 and l == 1)
        fp = sum(1 for p, l in zip(binary_preds, binary_labels) if p == 1 and l == 0)
        tn = sum(1 for p, l in zip(binary_preds, binary_labels) if p == 0 and l == 0)
        fn = sum(1 for p, l in zip(binary_preds, binary_labels) if p == 0 and l == 1)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'mae': mae,
            'max_error': max_error
        }
    
    def _determine_drift_severity(self, drift_score: float, threshold: float) -> DriftSeverity:
        """Determine drift severity based on score and threshold"""
        if drift_score >= threshold * 3:
            return DriftSeverity.CRITICAL
        elif drift_score >= threshold * 2:
            return DriftSeverity.HIGH
        elif drift_score >= threshold * 1.5:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW
    
    def _generate_drift_id(self, model_id: str, drift_type: DriftType, 
                          feature: Optional[str] = None) -> str:
        """Generate unique drift detection ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        feature_suffix = f"_{feature}" if feature else ""
        return f"{model_id}_{drift_type.value}{feature_suffix}_{timestamp}"
    
    def _generate_quality_report_id(self, model_id: str) -> str:
        """Generate unique quality report ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"quality_{model_id}_{timestamp}"
    
    async def _save_drift_report(self, drift_result: DriftDetectionResult):
        """Save drift detection report to file"""
        report_file = self.drift_reports_path / f"{drift_result.drift_id}.json"
        
        report_dict = {
            'drift_id': drift_result.drift_id,
            'model_id': drift_result.model_id,
            'drift_type': drift_result.drift_type.value,
            'severity': drift_result.severity.value,
            'score': drift_result.score,
            'threshold': drift_result.threshold,
            'detection_time': drift_result.detection_time.isoformat(),
            'affected_features': drift_result.affected_features,
            'statistical_tests': drift_result.statistical_tests,
            'explanation': drift_result.explanation,
            'recommendations': drift_result.recommendations,
            'metadata': drift_result.metadata
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
    
    async def _save_quality_report(self, report: DataQualityReport):
        """Save data quality report to file"""
        report_file = self.quality_reports_path / f"{report.report_id}.json"
        
        report_dict = {
            'report_id': report.report_id,
            'model_id': report.model_id,
            'timestamp': report.timestamp.isoformat(),
            'sample_size': report.sample_size,
            'completeness_score': report.completeness_score,
            'validity_score': report.validity_score,
            'consistency_score': report.consistency_score,
            'uniqueness_score': report.uniqueness_score,
            'overall_quality_score': report.overall_quality_score,
            'missing_values': report.missing_values,
            'invalid_values': report.invalid_values,
            'duplicate_records': report.duplicate_records,
            'schema_violations': report.schema_violations,
            'quality_issues': report.quality_issues,
            'recommendations': report.recommendations
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
    
    def get_drift_history(self, model_id: str, drift_type: Optional[DriftType] = None, 
                         days: int = 30) -> List[Dict[str, Any]]:
        """Get drift detection history for a model"""
        if model_id not in self.drift_history:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        history = self.drift_history[model_id]
        
        # Filter by date and optionally by drift type
        filtered_history = [
            drift for drift in history
            if drift.detection_time >= cutoff_date and
            (drift_type is None or drift.drift_type == drift_type)
        ]
        
        return [
            {
                'drift_id': drift.drift_id,
                'drift_type': drift.drift_type.value,
                'severity': drift.severity.value,
                'score': drift.score,
                'detection_time': drift.detection_time.isoformat(),
                'explanation': drift.explanation
            }
            for drift in filtered_history
        ]
    
    def get_quality_history(self, model_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get data quality history for a model"""
        if model_id not in self.quality_reports:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        reports = self.quality_reports[model_id]
        
        # Filter by date
        filtered_reports = [
            report for report in reports
            if report.timestamp >= cutoff_date
        ]
        
        return [
            {
                'report_id': report.report_id,
                'timestamp': report.timestamp.isoformat(),
                'overall_quality_score': report.overall_quality_score,
                'completeness_score': report.completeness_score,
                'validity_score': report.validity_score,
                'sample_size': report.sample_size,
                'quality_issues': len(report.quality_issues)
            }
            for report in filtered_reports
        ]