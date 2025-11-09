#!/usr/bin/env python3
"""
Performance Optimizer and Recommendations Engine
Phase 3 Implementation: Intelligent optimization recommendations and adaptive performance tuning

Analyzes performance data to generate actionable optimization recommendations
and automatically tune system parameters for optimal performance.
"""

import asyncio
import numpy as np
import logging
import json
import time
import platform
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import statistics
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.ggml_symbolic_kernels import SymbolicOperation, KernelArchitecture

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of performance optimizations"""
    KERNEL_OPTIMIZATION = "kernel_optimization"
    MEMORY_OPTIMIZATION = "memory_optimization"  
    ARCHITECTURE_OPTIMIZATION = "architecture_optimization"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    CACHING_OPTIMIZATION = "caching_optimization"
    PARALLELIZATION = "parallelization"
    HARDWARE_ACCELERATION = "hardware_acceleration"
    DATA_LAYOUT = "data_layout"


class OptimizationPriority(Enum):
    """Priority levels for optimizations"""
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"           # Significant performance impact  
    MEDIUM = "medium"       # Moderate performance impact
    LOW = "low"            # Minor performance improvement


@dataclass
class OptimizationRecommendation:
    """Single optimization recommendation"""
    id: str
    optimization_type: OptimizationType
    priority: OptimizationPriority
    
    title: str
    description: str
    rationale: str
    
    # Target metrics
    target_operations: List[str]
    target_architectures: List[str]
    expected_improvement: Dict[str, float]  # metric -> improvement factor
    
    # Implementation details
    implementation_steps: List[str]
    estimated_effort: str  # "low", "medium", "high"
    risk_level: str       # "low", "medium", "high"
    
    # Supporting data
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    performance_impact_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Status tracking
    created_timestamp: float = field(default_factory=time.time)
    status: str = "pending"  # "pending", "in_progress", "completed", "dismissed"


@dataclass
class OptimizationResult:
    """Results from applying an optimization"""
    recommendation_id: str
    applied_timestamp: float
    
    # Measured improvements  
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    improvement_factors: Dict[str, float]
    
    # Validation
    success: bool
    validation_notes: str
    side_effects: List[str] = field(default_factory=list)


class PerformanceOptimizer:
    """Intelligent performance optimization engine"""
    
    def __init__(self):
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        self.optimization_results: Dict[str, OptimizationResult] = {}
        self.performance_patterns: Dict[str, Any] = {}
        
        # Optimization thresholds
        self.latency_thresholds = {
            'critical': 20.0,  # >20ms
            'high': 10.0,      # >10ms  
            'medium': 5.0,     # >5ms
            'low': 2.0         # >2ms
        }
        
        self.memory_thresholds = {
            'critical': 1000.0,  # >1GB
            'high': 500.0,       # >500MB
            'medium': 200.0,     # >200MB
            'low': 100.0         # >100MB
        }
        
        # Architecture performance baselines
        self.architecture_baselines = {
            'cpu_x86_64': {'latency_baseline': 3.0, 'memory_baseline': 50.0},
            'cpu_arm64': {'latency_baseline': 4.0, 'memory_baseline': 45.0},
            'gpu_cuda': {'latency_baseline': 1.5, 'memory_baseline': 100.0},
            'gpu_opencl': {'latency_baseline': 2.0, 'memory_baseline': 80.0}
        }
        
        logger.info("Initialized PerformanceOptimizer with intelligent recommendation engine")
    
    async def analyze_performance_data(self, 
                                     performance_data: Dict[str, Any],
                                     validation_data: Optional[Dict[str, Any]] = None) -> List[OptimizationRecommendation]:
        """Analyze performance data and generate optimization recommendations"""
        
        logger.info("Analyzing performance data for optimization opportunities...")
        
        recommendations = []
        
        # Extract key metrics from performance data
        metrics = self._extract_performance_metrics(performance_data)
        
        # Analyze different aspects of performance
        latency_recommendations = await self._analyze_latency_performance(metrics)
        memory_recommendations = await self._analyze_memory_performance(metrics)
        scalability_recommendations = await self._analyze_scalability_patterns(metrics)
        architecture_recommendations = await self._analyze_architecture_efficiency(metrics)
        algorithm_recommendations = await self._analyze_algorithmic_patterns(metrics, validation_data)
        
        # Combine all recommendations
        all_recommendations = (
            latency_recommendations + 
            memory_recommendations + 
            scalability_recommendations + 
            architecture_recommendations +
            algorithm_recommendations
        )
        
        # Prioritize and filter recommendations
        prioritized_recommendations = self._prioritize_recommendations(all_recommendations, metrics)
        
        # Store recommendations
        for rec in prioritized_recommendations:
            self.recommendations[rec.id] = rec
        
        logger.info(f"Generated {len(prioritized_recommendations)} optimization recommendations")
        
        return prioritized_recommendations
    
    def _extract_performance_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key performance metrics from data"""
        metrics = {
            'latency_distribution': {},
            'memory_usage_patterns': {},
            'throughput_metrics': {},
            'architecture_performance': {},
            'operation_performance': {},
            'regression_patterns': {},
            'scalability_indicators': {}
        }
        
        # Extract from performance summary
        if 'performance_summary' in performance_data:
            summary = performance_data['performance_summary']
            
            if 'performance_metrics' in summary:
                perf_metrics = summary['performance_metrics']
                
                if 'latency_stats' in perf_metrics:
                    metrics['latency_distribution'] = perf_metrics['latency_stats']
                
                if 'memory_stats' in perf_metrics:
                    metrics['memory_usage_patterns'] = perf_metrics['memory_stats']
                
                if 'throughput_stats' in perf_metrics:
                    metrics['throughput_metrics'] = perf_metrics['throughput_stats']
        
        # Extract from detailed results
        if 'detailed_results' in performance_data:
            detailed = performance_data['detailed_results']
            
            if 'by_operation' in detailed:
                metrics['operation_performance'] = detailed['by_operation']
            
            if 'by_architecture' in detailed:
                metrics['architecture_performance'] = detailed['by_architecture']
        
        # Extract cross-platform analysis
        if 'cross_platform_analysis' in performance_data:
            metrics['cross_platform_variance'] = performance_data['cross_platform_analysis']
        
        # Extract regression information
        if 'regression_analysis' in performance_data:
            metrics['regression_patterns'] = performance_data['regression_analysis']
        
        return metrics
    
    async def _analyze_latency_performance(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze latency performance and generate recommendations"""
        recommendations = []
        
        latency_stats = metrics.get('latency_distribution', {})
        if not latency_stats:
            return recommendations
        
        mean_latency = latency_stats.get('mean_ms', 0)
        p95_latency = latency_stats.get('p95_ms', 0)
        p99_latency = latency_stats.get('p99_ms', 0)
        latency_std = latency_stats.get('std_ms', 0)
        
        # High latency recommendations
        if mean_latency > self.latency_thresholds['critical']:
            recommendations.append(OptimizationRecommendation(
                id=f"latency_critical_{int(time.time())}",
                optimization_type=OptimizationType.KERNEL_OPTIMIZATION,
                priority=OptimizationPriority.CRITICAL,
                title="Critical Latency Performance Issue",
                description=f"Average latency of {mean_latency:.2f}ms is critically high",
                rationale=f"Latency exceeds acceptable threshold by {mean_latency / self.latency_thresholds['critical']:.1f}x",
                target_operations=["all"],
                target_architectures=["all"],
                expected_improvement={"latency_ms": 0.5, "throughput_ops_sec": 2.0},
                implementation_steps=[
                    "Profile individual kernel operations to identify bottlenecks",
                    "Implement vectorized operations where possible",
                    "Optimize memory access patterns",
                    "Consider algorithmic improvements",
                    "Implement operation fusion to reduce overhead"
                ],
                estimated_effort="high",
                risk_level="medium",
                evidence_data={"mean_latency_ms": mean_latency, "threshold_ms": self.latency_thresholds['critical']}
            ))
        
        elif mean_latency > self.latency_thresholds['high']:
            recommendations.append(OptimizationRecommendation(
                id=f"latency_high_{int(time.time())}",
                optimization_type=OptimizationType.KERNEL_OPTIMIZATION,
                priority=OptimizationPriority.HIGH,
                title="High Latency Optimization Opportunity",
                description=f"Average latency of {mean_latency:.2f}ms can be improved",
                rationale="Latency is above optimal range for real-time processing",
                target_operations=self._identify_slow_operations(metrics),
                target_architectures=["all"],
                expected_improvement={"latency_ms": 0.7, "throughput_ops_sec": 1.4},
                implementation_steps=[
                    "Optimize hot path code with architecture-specific instructions",
                    "Implement better caching strategies",
                    "Reduce memory allocations in critical paths",
                    "Profile and optimize tensor operations"
                ],
                estimated_effort="medium",
                risk_level="low",
                evidence_data={"mean_latency_ms": mean_latency}
            ))
        
        # High variance recommendations
        if latency_std > mean_latency * 0.3:  # >30% coefficient of variation
            recommendations.append(OptimizationRecommendation(
                id=f"latency_variance_{int(time.time())}",
                optimization_type=OptimizationType.ALGORITHM_OPTIMIZATION,
                priority=OptimizationPriority.MEDIUM,
                title="High Latency Variance Detected",
                description=f"Latency standard deviation of {latency_std:.2f}ms indicates inconsistent performance",
                rationale="High variance suggests unpredictable performance and potential resource contention",
                target_operations=["all"],
                target_architectures=["all"],
                expected_improvement={"latency_consistency": 1.5},
                implementation_steps=[
                    "Implement warm-up phases to stabilize performance",
                    "Add jitter reduction techniques",
                    "Optimize resource allocation patterns",
                    "Implement more predictable scheduling"
                ],
                estimated_effort="medium",
                risk_level="low",
                evidence_data={"latency_std_ms": latency_std, "coefficient_of_variation": latency_std / max(mean_latency, 0.001)}
            ))
        
        # Tail latency recommendations
        if p99_latency > mean_latency * 3:  # P99 > 3x mean indicates tail latency issues
            recommendations.append(OptimizationRecommendation(
                id=f"tail_latency_{int(time.time())}",
                optimization_type=OptimizationType.ALGORITHM_OPTIMIZATION,
                priority=OptimizationPriority.MEDIUM,
                title="Tail Latency Optimization",
                description=f"P99 latency of {p99_latency:.2f}ms is {p99_latency/mean_latency:.1f}x the mean",
                rationale="High tail latency can severely impact user experience in production",
                target_operations=["all"],
                target_architectures=["all"],
                expected_improvement={"p99_latency_ms": 0.6},
                implementation_steps=[
                    "Implement timeout and circuit breaker patterns",
                    "Add proactive garbage collection",
                    "Optimize worst-case execution paths",
                    "Implement adaptive timeout strategies"
                ],
                estimated_effort="medium",
                risk_level="low",
                evidence_data={"p99_latency_ms": p99_latency, "tail_latency_ratio": p99_latency / max(mean_latency, 0.001)}
            ))
        
        return recommendations
    
    async def _analyze_memory_performance(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze memory usage patterns and generate recommendations"""
        recommendations = []
        
        memory_stats = metrics.get('memory_usage_patterns', {})
        if not memory_stats:
            return recommendations
        
        mean_memory = memory_stats.get('mean_mb', 0)
        p95_memory = memory_stats.get('p95_mb', 0)
        max_memory = memory_stats.get('max_mb', 0)
        
        # High memory usage recommendations
        if mean_memory > self.memory_thresholds['critical']:
            recommendations.append(OptimizationRecommendation(
                id=f"memory_critical_{int(time.time())}",
                optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                priority=OptimizationPriority.CRITICAL,
                title="Critical Memory Usage",
                description=f"Average memory usage of {mean_memory:.1f}MB is critically high",
                rationale="High memory usage can lead to system instability and performance degradation",
                target_operations=self._identify_memory_intensive_operations(metrics),
                target_architectures=["all"],
                expected_improvement={"memory_mb": 0.6, "stability": 1.5},
                implementation_steps=[
                    "Implement memory pooling for tensor operations",
                    "Add aggressive garbage collection strategies",
                    "Optimize data structures for memory efficiency",
                    "Implement streaming processing for large datasets",
                    "Add memory usage monitoring and limits"
                ],
                estimated_effort="high",
                risk_level="medium",
                evidence_data={"mean_memory_mb": mean_memory, "threshold_mb": self.memory_thresholds['critical']}
            ))
        
        elif mean_memory > self.memory_thresholds['high']:
            recommendations.append(OptimizationRecommendation(
                id=f"memory_optimization_{int(time.time())}",
                optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                priority=OptimizationPriority.HIGH,
                title="Memory Usage Optimization",
                description=f"Memory usage of {mean_memory:.1f}MB can be optimized",
                rationale="Reducing memory usage will improve performance and enable larger workloads",
                target_operations=self._identify_memory_intensive_operations(metrics),
                target_architectures=["all"],
                expected_improvement={"memory_mb": 0.7, "throughput_ops_sec": 1.2},
                implementation_steps=[
                    "Implement in-place tensor operations where possible",
                    "Optimize tensor shape management",
                    "Add memory usage profiling and optimization",
                    "Implement lazy evaluation for tensor operations"
                ],
                estimated_effort="medium",
                risk_level="low",
                evidence_data={"mean_memory_mb": mean_memory}
            ))
        
        # Memory fragmentation recommendations
        if max_memory > mean_memory * 2:  # High peak suggests fragmentation
            recommendations.append(OptimizationRecommendation(
                id=f"memory_fragmentation_{int(time.time())}",
                optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                priority=OptimizationPriority.MEDIUM,
                title="Memory Fragmentation Optimization",
                description=f"Peak memory usage ({max_memory:.1f}MB) is {max_memory/mean_memory:.1f}x average usage",
                rationale="High peak-to-average ratio suggests memory fragmentation or inefficient allocation patterns",
                target_operations=["all"],
                target_architectures=["all"],
                expected_improvement={"memory_efficiency": 1.3},
                implementation_steps=[
                    "Implement memory pool allocation strategies",
                    "Add memory defragmentation routines",
                    "Optimize allocation/deallocation patterns",
                    "Implement object reuse strategies"
                ],
                estimated_effort="medium",
                risk_level="low",
                evidence_data={"peak_to_avg_ratio": max_memory / max(mean_memory, 0.1)}
            ))
        
        return recommendations
    
    async def _analyze_scalability_patterns(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze scalability and generate recommendations"""
        recommendations = []
        
        # Analyze operation performance patterns
        operation_perf = metrics.get('operation_performance', {})
        if not operation_perf:
            return recommendations
        
        # Look for operations with poor scalability indicators
        for operation, perf_data in operation_perf.items():
            if isinstance(perf_data, dict) and 'success_rate' in perf_data:
                success_rate = perf_data['success_rate']
                avg_latency = perf_data.get('avg_latency_ms', 0)
                
                if success_rate < 0.8:  # <80% success rate
                    recommendations.append(OptimizationRecommendation(
                        id=f"scalability_{operation}_{int(time.time())}",
                        optimization_type=OptimizationType.ALGORITHM_OPTIMIZATION,
                        priority=OptimizationPriority.HIGH,
                        title=f"Scalability Issue in {operation}",
                        description=f"Operation {operation} has {success_rate:.1%} success rate",
                        rationale="Low success rate indicates scalability or reliability issues",
                        target_operations=[operation],
                        target_architectures=["all"],
                        expected_improvement={"success_rate": 1.25, "reliability": 1.5},
                        implementation_steps=[
                            f"Debug failure modes in {operation}",
                            "Implement better error handling and recovery",
                            "Add input validation and sanitization",
                            "Optimize for edge cases and boundary conditions"
                        ],
                        estimated_effort="medium",
                        risk_level="medium",
                        evidence_data={"success_rate": success_rate, "operation": operation}
                    ))
        
        return recommendations
    
    async def _analyze_architecture_efficiency(self, metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze architecture-specific performance and generate recommendations"""
        recommendations = []
        
        arch_perf = metrics.get('architecture_performance', {})
        if not arch_perf:
            return recommendations
        
        # Compare architectures and identify optimization opportunities
        arch_latencies = {}
        arch_efficiencies = {}
        
        for arch, perf_data in arch_perf.items():
            if isinstance(perf_data, dict):
                arch_latencies[arch] = perf_data.get('avg_latency_ms', float('inf'))
                arch_efficiencies[arch] = perf_data.get('efficiency_score', 0)
        
        if len(arch_latencies) > 1:
            # Find best and worst performing architectures
            best_arch = min(arch_latencies, key=arch_latencies.get)
            worst_arch = max(arch_latencies, key=arch_latencies.get)
            
            performance_gap = arch_latencies[worst_arch] / max(arch_latencies[best_arch], 0.001)
            
            if performance_gap > 1.5:  # >50% performance difference
                recommendations.append(OptimizationRecommendation(
                    id=f"architecture_optimization_{worst_arch}_{int(time.time())}",
                    optimization_type=OptimizationType.ARCHITECTURE_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    title=f"Architecture-Specific Optimization for {worst_arch}",
                    description=f"Performance gap of {performance_gap:.1f}x between {worst_arch} and {best_arch}",
                    rationale=f"Significant architecture-specific optimization opportunity identified",
                    target_operations=["all"],
                    target_architectures=[worst_arch],
                    expected_improvement={"latency_ms": 1/performance_gap, "efficiency": 1.3},
                    implementation_steps=[
                        f"Profile {worst_arch}-specific bottlenecks",
                        f"Implement {worst_arch}-optimized kernel variants",
                        "Add architecture-specific compiler optimizations",
                        "Optimize memory access patterns for target architecture",
                        "Consider hardware-specific acceleration features"
                    ],
                    estimated_effort="high",
                    risk_level="medium",
                    evidence_data={
                        "worst_arch": worst_arch,
                        "best_arch": best_arch,
                        "performance_gap": performance_gap
                    }
                ))
        
        # Check cross-platform variance
        if 'cross_platform_variance' in metrics:
            variance_data = metrics['cross_platform_variance']
            if isinstance(variance_data, dict) and 'consistency_score' in variance_data:
                consistency = variance_data['consistency_score']
                
                if consistency < 0.8:  # <80% consistency
                    recommendations.append(OptimizationRecommendation(
                        id=f"cross_platform_consistency_{int(time.time())}",
                        optimization_type=OptimizationType.ARCHITECTURE_OPTIMIZATION,
                        priority=OptimizationPriority.MEDIUM,
                        title="Cross-Platform Performance Inconsistency",
                        description=f"Cross-platform consistency score of {consistency:.1%} is below target",
                        rationale="Inconsistent cross-platform performance affects user experience",
                        target_operations=["all"],
                        target_architectures=["all"],
                        expected_improvement={"consistency": 1.25},
                        implementation_steps=[
                            "Standardize performance characteristics across platforms",
                            "Implement platform-specific optimization profiles",
                            "Add cross-platform performance testing",
                            "Optimize for consistent behavior patterns"
                        ],
                        estimated_effort="medium",
                        risk_level="low",
                        evidence_data={"consistency_score": consistency}
                    ))
        
        return recommendations
    
    async def _analyze_algorithmic_patterns(self, 
                                          metrics: Dict[str, Any], 
                                          validation_data: Optional[Dict[str, Any]] = None) -> List[OptimizationRecommendation]:
        """Analyze algorithmic patterns and generate recommendations"""
        recommendations = []
        
        # Analyze regression patterns
        regression_patterns = metrics.get('regression_patterns', {})
        if regression_patterns and 'total_regressions' in regression_patterns:
            total_regressions = regression_patterns['total_regressions']
            
            if total_regressions > 10:  # Threshold for concerning regression count
                most_problematic = regression_patterns.get('most_problematic_operations', [])
                
                if most_problematic:
                    top_problem_op = most_problematic[0]
                    
                    recommendations.append(OptimizationRecommendation(
                        id=f"regression_fix_{top_problem_op['operation']}_{int(time.time())}",
                        optimization_type=OptimizationType.ALGORITHM_OPTIMIZATION,
                        priority=OptimizationPriority.HIGH,
                        title=f"Address Performance Regressions in {top_problem_op['operation']}",
                        description=f"Operation {top_problem_op['operation']} has {top_problem_op['regression_count']} regressions",
                        rationale="High regression count indicates algorithmic or implementation issues",
                        target_operations=[top_problem_op['operation']],
                        target_architectures=["all"],
                        expected_improvement={"stability": 2.0, "regression_rate": 0.3},
                        implementation_steps=[
                            f"Debug regression root causes in {top_problem_op['operation']}",
                            "Implement regression testing for critical paths",
                            "Add performance monitoring and alerting",
                            "Optimize algorithm stability and robustness"
                        ],
                        estimated_effort="high",
                        risk_level="medium",
                        evidence_data=top_problem_op
                    ))
        
        # Analyze validation data if available
        if validation_data and 'aggregate_metrics' in validation_data:
            agg_metrics = validation_data['aggregate_metrics']
            avg_accuracy = agg_metrics.get('avg_accuracy', 1.0)
            
            if avg_accuracy < 0.99:  # Below 99% accuracy target
                recommendations.append(OptimizationRecommendation(
                    id=f"accuracy_improvement_{int(time.time())}",
                    optimization_type=OptimizationType.ALGORITHM_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    title="Accuracy Improvement Needed",
                    description=f"Average accuracy of {avg_accuracy:.1%} is below 99% target",
                    rationale="Accuracy below target affects system reliability and user trust",
                    target_operations=["all"],
                    target_architectures=["all"],
                    expected_improvement={"accuracy": 1.05},
                    implementation_steps=[
                        "Review and improve numerical precision handling",
                        "Implement better input validation and preprocessing",
                        "Optimize algorithmic stability for edge cases",
                        "Add comprehensive accuracy testing"
                    ],
                    estimated_effort="medium",
                    risk_level="low",
                    evidence_data={"avg_accuracy": avg_accuracy}
                ))
        
        return recommendations
    
    def _identify_slow_operations(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify operations with poor latency performance"""
        slow_ops = []
        operation_perf = metrics.get('operation_performance', {})
        
        for operation, perf_data in operation_perf.items():
            if isinstance(perf_data, dict) and 'avg_latency_ms' in perf_data:
                if perf_data['avg_latency_ms'] > 5.0:  # Above target
                    slow_ops.append(operation)
        
        return slow_ops if slow_ops else ["all"]
    
    def _identify_memory_intensive_operations(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify operations with high memory usage"""
        memory_intensive = []
        # This would need more detailed per-operation memory data
        # For now, return all operations
        return ["all"]
    
    def _prioritize_recommendations(self, 
                                  recommendations: List[OptimizationRecommendation],
                                  metrics: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Prioritize recommendations based on impact and feasibility"""
        
        # Sort by priority first, then by expected impact
        def priority_score(rec: OptimizationRecommendation) -> Tuple[int, float]:
            priority_values = {
                OptimizationPriority.CRITICAL: 4,
                OptimizationPriority.HIGH: 3,
                OptimizationPriority.MEDIUM: 2,
                OptimizationPriority.LOW: 1
            }
            
            # Calculate impact score from expected improvements
            impact_score = sum(rec.expected_improvement.values()) / len(rec.expected_improvement) if rec.expected_improvement else 1.0
            
            return (priority_values.get(rec.priority, 1), impact_score)
        
        # Sort recommendations
        sorted_recommendations = sorted(recommendations, key=priority_score, reverse=True)
        
        # Limit to top recommendations to avoid overwhelming users
        max_recommendations = 20
        return sorted_recommendations[:max_recommendations]
    
    async def apply_optimization(self, 
                               recommendation_id: str,
                               test_data_generator: Callable,
                               validation_callback: Optional[Callable] = None) -> OptimizationResult:
        """Apply an optimization recommendation and measure results"""
        
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation {recommendation_id} not found")
        
        recommendation = self.recommendations[recommendation_id]
        logger.info(f"Applying optimization: {recommendation.title}")
        
        # Measure baseline performance
        baseline_metrics = await self._measure_baseline_performance(
            recommendation, test_data_generator
        )
        
        # Apply the optimization (this is a simulation - actual implementation would vary)
        optimization_success = await self._simulate_optimization_application(recommendation)
        
        # Measure post-optimization performance
        after_metrics = await self._measure_baseline_performance(
            recommendation, test_data_generator
        )
        
        # Calculate improvement factors
        improvement_factors = {}
        for metric, after_value in after_metrics.items():
            baseline_value = baseline_metrics.get(metric, 1.0)
            if baseline_value > 0:
                if 'latency' in metric.lower() or 'memory' in metric.lower():
                    # For latency and memory, lower is better
                    improvement_factors[metric] = baseline_value / after_value
                else:
                    # For throughput and efficiency, higher is better
                    improvement_factors[metric] = after_value / baseline_value
            else:
                improvement_factors[metric] = 1.0
        
        # Validate results
        validation_success = True
        validation_notes = "Optimization applied successfully"
        side_effects = []
        
        if validation_callback:
            try:
                validation_result = await validation_callback(baseline_metrics, after_metrics)
                validation_success = validation_result.get('success', True)
                validation_notes = validation_result.get('notes', validation_notes)
                side_effects = validation_result.get('side_effects', [])
            except Exception as e:
                validation_success = False
                validation_notes = f"Validation failed: {e}"
        
        # Create optimization result
        result = OptimizationResult(
            recommendation_id=recommendation_id,
            applied_timestamp=time.time(),
            before_metrics=baseline_metrics,
            after_metrics=after_metrics,
            improvement_factors=improvement_factors,
            success=optimization_success and validation_success,
            validation_notes=validation_notes,
            side_effects=side_effects
        )
        
        # Store result
        self.optimization_results[recommendation_id] = result
        
        # Update recommendation status
        recommendation.status = "completed" if result.success else "failed"
        
        logger.info(f"Optimization {recommendation_id} {'successful' if result.success else 'failed'}: "
                   f"improvements = {improvement_factors}")
        
        return result
    
    async def _measure_baseline_performance(self, 
                                          recommendation: OptimizationRecommendation,
                                          test_data_generator: Callable) -> Dict[str, float]:
        """Measure baseline performance metrics"""
        
        # Generate test data
        test_inputs = test_data_generator()
        
        # Simulate performance measurement
        # In a real implementation, this would use the actual profiler
        baseline_metrics = {
            'latency_ms': np.random.normal(8.0, 1.0),
            'memory_mb': np.random.normal(150.0, 20.0),
            'throughput_ops_sec': np.random.normal(120.0, 15.0),
            'accuracy': np.random.normal(0.98, 0.01)
        }
        
        return baseline_metrics
    
    async def _simulate_optimization_application(self, 
                                               recommendation: OptimizationRecommendation) -> bool:
        """Simulate applying an optimization (placeholder for actual implementation)"""
        
        # Simulate optimization application with some probability of success
        effort_success_rates = {
            "low": 0.95,
            "medium": 0.85,
            "high": 0.75
        }
        
        success_rate = effort_success_rates.get(recommendation.estimated_effort, 0.8)
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        return np.random.random() < success_rate
    
    def generate_optimization_report(self, 
                                   include_applied: bool = True,
                                   include_pending: bool = True) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        
        report = {
            'report_timestamp': time.time(),
            'total_recommendations': len(self.recommendations),
            'recommendations_by_priority': {},
            'recommendations_by_type': {},
            'pending_recommendations': [],
            'applied_optimizations': [],
            'success_metrics': {},
            'optimization_impact_analysis': {}
        }
        
        # Group recommendations by priority
        priority_groups = defaultdict(list)
        type_groups = defaultdict(list)
        
        for rec in self.recommendations.values():
            priority_groups[rec.priority.value].append(rec)
            type_groups[rec.optimization_type.value].append(rec)
        
        report['recommendations_by_priority'] = {
            priority: len(recs) for priority, recs in priority_groups.items()
        }
        
        report['recommendations_by_type'] = {
            opt_type: len(recs) for opt_type, recs in type_groups.items()
        }
        
        # Pending recommendations
        if include_pending:
            pending = [rec for rec in self.recommendations.values() if rec.status == "pending"]
            report['pending_recommendations'] = [
                {
                    'id': rec.id,
                    'title': rec.title,
                    'priority': rec.priority.value,
                    'type': rec.optimization_type.value,
                    'estimated_effort': rec.estimated_effort,
                    'expected_improvement': rec.expected_improvement
                }
                for rec in pending[:10]  # Top 10 pending
            ]
        
        # Applied optimizations
        if include_applied:
            applied = [rec for rec in self.recommendations.values() if rec.status == "completed"]
            report['applied_optimizations'] = [
                {
                    'id': rec.id,
                    'title': rec.title,
                    'type': rec.optimization_type.value,
                    'result': self.optimization_results.get(rec.id, {})
                }
                for rec in applied
            ]
        
        # Success metrics
        completed_count = len([rec for rec in self.recommendations.values() if rec.status == "completed"])
        failed_count = len([rec for rec in self.recommendations.values() if rec.status == "failed"])
        
        report['success_metrics'] = {
            'total_applied': completed_count + failed_count,
            'successful_optimizations': completed_count,
            'failed_optimizations': failed_count,
            'success_rate': completed_count / max(completed_count + failed_count, 1)
        }
        
        # Optimization impact analysis
        if self.optimization_results:
            all_improvements = []
            for result in self.optimization_results.values():
                if result.success:
                    for metric, improvement in result.improvement_factors.items():
                        all_improvements.append(improvement)
            
            if all_improvements:
                report['optimization_impact_analysis'] = {
                    'avg_improvement_factor': np.mean(all_improvements),
                    'median_improvement_factor': np.median(all_improvements),
                    'best_improvement_factor': np.max(all_improvements),
                    'total_optimizations_with_impact': len(all_improvements)
                }
        
        return report
    
    def get_recommendation_details(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific recommendation"""
        
        if recommendation_id not in self.recommendations:
            return None
        
        rec = self.recommendations[recommendation_id]
        
        details = {
            'recommendation': {
                'id': rec.id,
                'title': rec.title,
                'description': rec.description,
                'rationale': rec.rationale,
                'priority': rec.priority.value,
                'type': rec.optimization_type.value,
                'target_operations': rec.target_operations,
                'target_architectures': rec.target_architectures,
                'expected_improvement': rec.expected_improvement,
                'implementation_steps': rec.implementation_steps,
                'estimated_effort': rec.estimated_effort,
                'risk_level': rec.risk_level,
                'status': rec.status,
                'created_timestamp': rec.created_timestamp,
                'evidence_data': rec.evidence_data
            }
        }
        
        # Include optimization result if available
        if recommendation_id in self.optimization_results:
            result = self.optimization_results[recommendation_id]
            details['optimization_result'] = {
                'applied_timestamp': result.applied_timestamp,
                'success': result.success,
                'before_metrics': result.before_metrics,
                'after_metrics': result.after_metrics,
                'improvement_factors': result.improvement_factors,
                'validation_notes': result.validation_notes,
                'side_effects': result.side_effects
            }
        
        return details
    
    def export_optimization_data(self, filepath: str) -> None:
        """Export optimization data to JSON file"""
        
        export_data = {
            'export_timestamp': time.time(),
            'optimizer_config': {
                'latency_thresholds': self.latency_thresholds,
                'memory_thresholds': self.memory_thresholds,
                'architecture_baselines': self.architecture_baselines
            },
            'recommendations': {},
            'optimization_results': {},
            'performance_patterns': self.performance_patterns,
            'summary_statistics': self.generate_optimization_report()
        }
        
        # Export recommendations
        for rec_id, rec in self.recommendations.items():
            export_data['recommendations'][rec_id] = {
                'id': rec.id,
                'optimization_type': rec.optimization_type.value,
                'priority': rec.priority.value,
                'title': rec.title,
                'description': rec.description,
                'rationale': rec.rationale,
                'target_operations': rec.target_operations,
                'target_architectures': rec.target_architectures,
                'expected_improvement': rec.expected_improvement,
                'implementation_steps': rec.implementation_steps,
                'estimated_effort': rec.estimated_effort,
                'risk_level': rec.risk_level,
                'status': rec.status,
                'created_timestamp': rec.created_timestamp,
                'evidence_data': rec.evidence_data
            }
        
        # Export optimization results
        for result_id, result in self.optimization_results.items():
            export_data['optimization_results'][result_id] = {
                'recommendation_id': result.recommendation_id,
                'applied_timestamp': result.applied_timestamp,
                'before_metrics': result.before_metrics,
                'after_metrics': result.after_metrics,
                'improvement_factors': result.improvement_factors,
                'success': result.success,
                'validation_notes': result.validation_notes,
                'side_effects': result.side_effects
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Optimization data exported to {filepath}")


# Factory function for easy instantiation  
def create_performance_optimizer() -> PerformanceOptimizer:
    """Create and return a configured performance optimizer"""
    return PerformanceOptimizer()