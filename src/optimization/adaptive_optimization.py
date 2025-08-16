#!/usr/bin/env python3
"""
Adaptive Optimization & Continuous Learning Engine - Phase 5 Implementation
Provides continuous benchmarking, self-tuning algorithms, and evolutionary fitness landscapes.
"""

import asyncio
import json
import time
import math
import random
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import uuid
import threading
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)


class AdaptiveStrategy(Enum):
    """Types of adaptive optimization strategies"""
    CONTINUOUS_TUNING = "continuous_tuning"
    EVOLUTIONARY_SEARCH = "evolutionary_search"
    GRADIENT_BASED = "gradient_based"
    HYBRID_ADAPTIVE = "hybrid_adaptive"
    SELF_ORGANIZING = "self_organizing"


class FitnessLandscapeType(Enum):
    """Types of fitness landscape mappings"""
    PERFORMANCE_SURFACE = "performance_surface"
    CONVERGENCE_TRAJECTORY = "convergence_trajectory"
    PARAMETER_SENSITIVITY = "parameter_sensitivity"
    MULTI_OBJECTIVE = "multi_objective"


@dataclass
class AdaptiveParameter:
    """Represents a parameter that can be adaptively optimized"""
    name: str
    current_value: float
    min_value: float
    max_value: float
    adaptation_rate: float = 0.1
    sensitivity_score: float = 0.5
    fitness_contribution: float = 0.0
    history: List[Tuple[float, float, float]] = field(default_factory=list)  # (timestamp, value, fitness)
    
    def update_value(self, new_value: float, fitness: float):
        """Update parameter value with fitness feedback"""
        # Clamp to bounds
        new_value = max(self.min_value, min(self.max_value, new_value))
        
        # Store history
        self.history.append((time.time(), new_value, fitness))
        
        # Update current value with adaptive rate
        self.current_value = (1 - self.adaptation_rate) * self.current_value + self.adaptation_rate * new_value
        
        # Update fitness contribution
        if len(self.history) > 1:
            prev_fitness = self.history[-2][2]
            self.fitness_contribution = fitness - prev_fitness
    
    def get_trend(self) -> str:
        """Get parameter trend over recent history"""
        if len(self.history) < 3:
            return "stable"
        
        recent_values = [h[1] for h in self.history[-3:]]
        if recent_values[-1] > recent_values[0] * 1.05:
            return "increasing"
        elif recent_values[-1] < recent_values[0] * 0.95:
            return "decreasing"
        else:
            return "stable"


@dataclass
class FitnessLandscapePoint:
    """Point in the fitness landscape"""
    coordinates: Dict[str, float]  # Parameter values
    fitness_value: float
    timestamp: float
    generation: int = 0
    evaluation_count: int = 1
    
    def distance_to(self, other: 'FitnessLandscapePoint') -> float:
        """Calculate Euclidean distance to another point"""
        total_distance = 0.0
        for param_name, value in self.coordinates.items():
            if param_name in other.coordinates:
                total_distance += (value - other.coordinates[param_name]) ** 2
        return math.sqrt(total_distance)


@dataclass
class ContinuousBenchmarkConfig:
    """Configuration for continuous benchmarking"""
    benchmark_interval_seconds: float = 30.0
    performance_window_size: int = 100
    regression_threshold: float = 0.1  # 10% performance drop triggers adaptation
    improvement_target: float = 0.05   # 5% improvement target
    adaptation_cooldown: float = 60.0  # Minimum time between adaptations
    
    # Metrics to track
    tracked_metrics: List[str] = field(default_factory=lambda: [
        "latency_ms", "throughput_ops_sec", "memory_usage_mb", "efficiency_score"
    ])


class ContinuousPerformanceBenchmark:
    """Continuous performance benchmarking system"""
    
    def __init__(self, config: ContinuousBenchmarkConfig):
        self.config = config
        self.performance_history: deque = deque(maxlen=config.performance_window_size)
        self.baseline_metrics: Dict[str, float] = {}
        self.running = False
        self.last_adaptation_time = 0.0
        self.benchmark_task = None
        
        # Performance tracking
        self.metric_trends: Dict[str, str] = {}
        self.regression_alerts: List[Dict[str, Any]] = []
        
    async def start_continuous_monitoring(self, benchmark_function: Callable):
        """Start continuous performance monitoring"""
        if self.running:
            logger.warning("Continuous monitoring already running")
            return
        
        self.running = True
        self.benchmark_task = asyncio.create_task(self._monitoring_loop(benchmark_function))
        logger.info("🔄 Started continuous performance monitoring")
    
    async def stop_continuous_monitoring(self):
        """Stop continuous performance monitoring"""
        self.running = False
        if self.benchmark_task:
            self.benchmark_task.cancel()
            try:
                await self.benchmark_task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ Stopped continuous performance monitoring")
    
    async def _monitoring_loop(self, benchmark_function: Callable):
        """Main monitoring loop"""
        while self.running:
            try:
                # Execute benchmark
                start_time = time.time()
                benchmark_result = await self._execute_benchmark(benchmark_function)
                execution_time = time.time() - start_time
                
                # Store performance data
                performance_snapshot = {
                    "timestamp": time.time(),
                    "execution_time": execution_time,
                    **benchmark_result
                }
                
                self.performance_history.append(performance_snapshot)
                
                # Update baselines if this is initial data
                if not self.baseline_metrics and len(self.performance_history) >= 10:
                    self._update_baseline_metrics()
                
                # Check for regressions
                await self._check_performance_regression(performance_snapshot)
                
                # Update trends
                self._update_performance_trends()
                
                await asyncio.sleep(self.config.benchmark_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.benchmark_interval_seconds)
    
    async def _execute_benchmark(self, benchmark_function: Callable) -> Dict[str, float]:
        """Execute a single benchmark iteration"""
        try:
            # Simulate benchmark execution
            result = await benchmark_function() if asyncio.iscoroutinefunction(benchmark_function) else benchmark_function()
            
            # Ensure we have the required metrics
            default_result = {
                "latency_ms": random.uniform(1.0, 10.0),
                "throughput_ops_sec": random.uniform(100.0, 1000.0),
                "memory_usage_mb": random.uniform(50.0, 200.0),
                "efficiency_score": random.uniform(0.5, 1.0)
            }
            
            if isinstance(result, dict):
                default_result.update(result)
            
            return default_result
            
        except Exception as e:
            logger.error(f"Benchmark execution failed: {e}")
            # Return default metrics on failure
            return {
                "latency_ms": 999.0,
                "throughput_ops_sec": 1.0,
                "memory_usage_mb": 1000.0,
                "efficiency_score": 0.1
            }
    
    def _update_baseline_metrics(self):
        """Update baseline performance metrics"""
        if len(self.performance_history) < 10:
            return
        
        # Calculate baseline from recent stable performance
        recent_metrics = list(self.performance_history)[-10:]
        
        for metric in self.config.tracked_metrics:
            values = [m.get(metric, 0.0) for m in recent_metrics]
            self.baseline_metrics[metric] = sum(values) / len(values)
        
        logger.info(f"📊 Updated baseline metrics: {self.baseline_metrics}")
    
    async def _check_performance_regression(self, current_snapshot: Dict[str, Any]):
        """Check for performance regression and trigger adaptation if needed"""
        if not self.baseline_metrics:
            return
        
        regression_detected = False
        regression_details = {}
        
        for metric in self.config.tracked_metrics:
            current_value = current_snapshot.get(metric, 0.0)
            baseline_value = self.baseline_metrics.get(metric, 0.0)
            
            if baseline_value > 0:
                # For latency and memory, lower is better
                if metric in ["latency_ms", "memory_usage_mb"]:
                    regression_ratio = current_value / baseline_value
                    if regression_ratio > (1 + self.config.regression_threshold):
                        regression_detected = True
                        regression_details[metric] = {
                            "current": current_value,
                            "baseline": baseline_value,
                            "regression_ratio": regression_ratio
                        }
                # For throughput and efficiency, higher is better
                else:
                    regression_ratio = baseline_value / current_value if current_value > 0 else float('inf')
                    if regression_ratio > (1 + self.config.regression_threshold):
                        regression_detected = True
                        regression_details[metric] = {
                            "current": current_value,
                            "baseline": baseline_value,
                            "regression_ratio": regression_ratio
                        }
        
        if regression_detected:
            regression_alert = {
                "timestamp": time.time(),
                "details": regression_details,
                "severity": self._calculate_regression_severity(regression_details)
            }
            
            self.regression_alerts.append(regression_alert)
            logger.warning(f"⚠️ Performance regression detected: {regression_details}")
            
            # Trigger adaptation if cooldown period has passed
            if time.time() - self.last_adaptation_time > self.config.adaptation_cooldown:
                await self._trigger_adaptation(regression_alert)
    
    def _calculate_regression_severity(self, regression_details: Dict[str, Any]) -> str:
        """Calculate severity of performance regression"""
        max_regression = max(
            details.get("regression_ratio", 1.0) 
            for details in regression_details.values()
        )
        
        if max_regression > 2.0:
            return "critical"
        elif max_regression > 1.5:
            return "major"
        elif max_regression > 1.2:
            return "minor"
        else:
            return "negligible"
    
    async def _trigger_adaptation(self, regression_alert: Dict[str, Any]):
        """Trigger adaptive optimization in response to regression"""
        self.last_adaptation_time = time.time()
        logger.info("🔧 Triggering adaptive optimization due to performance regression")
        
        # This would integrate with the adaptive optimizer
        # For now, just log the trigger
        adaptation_trigger = {
            "trigger_type": "performance_regression",
            "timestamp": time.time(),
            "regression_details": regression_alert["details"],
            "severity": regression_alert["severity"]
        }
        
        # Here we would call the adaptive optimizer
        # await self.adaptive_optimizer.optimize(adaptation_trigger)
    
    def _update_performance_trends(self):
        """Update performance trend analysis"""
        if len(self.performance_history) < 5:
            return
        
        recent_snapshots = list(self.performance_history)[-5:]
        
        for metric in self.config.tracked_metrics:
            values = [s.get(metric, 0.0) for s in recent_snapshots]
            
            # Simple trend detection
            if values[-1] > values[0] * 1.05:
                trend = "improving" if metric in ["throughput_ops_sec", "efficiency_score"] else "degrading"
            elif values[-1] < values[0] * 0.95:
                trend = "degrading" if metric in ["throughput_ops_sec", "efficiency_score"] else "improving"
            else:
                trend = "stable"
            
            self.metric_trends[metric] = trend
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.performance_history:
            return {"status": "no_data"}
        
        recent_snapshot = self.performance_history[-1]
        
        return {
            "current_metrics": {
                metric: recent_snapshot.get(metric, 0.0) 
                for metric in self.config.tracked_metrics
            },
            "baseline_metrics": self.baseline_metrics.copy(),
            "trends": self.metric_trends.copy(),
            "regression_alerts_count": len(self.regression_alerts),
            "monitoring_duration": time.time() - (self.performance_history[0]["timestamp"] if self.performance_history else time.time()),
            "data_points": len(self.performance_history)
        }


class SelfTuningAlgorithm:
    """Self-tuning algorithm for adaptive parameter optimization"""
    
    def __init__(self, parameters: List[AdaptiveParameter], strategy: AdaptiveStrategy = AdaptiveStrategy.HYBRID_ADAPTIVE):
        self.parameters = {p.name: p for p in parameters}
        self.strategy = strategy
        self.optimization_history: List[Dict[str, Any]] = []
        self.generation_count = 0
        self.best_fitness = -float('inf')
        self.best_parameters = {}
        
        # Algorithm state
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.convergence_threshold = 0.001
        
    async def optimize_parameters(self, fitness_function: Callable) -> Dict[str, Any]:
        """Execute one optimization iteration"""
        self.generation_count += 1
        
        # Generate parameter variations based on strategy
        if self.strategy == AdaptiveStrategy.EVOLUTIONARY_SEARCH:
            return await self._evolutionary_optimization(fitness_function)
        elif self.strategy == AdaptiveStrategy.GRADIENT_BASED:
            return await self._gradient_optimization(fitness_function)
        elif self.strategy == AdaptiveStrategy.HYBRID_ADAPTIVE:
            return await self._hybrid_optimization(fitness_function)
        else:
            return await self._continuous_tuning(fitness_function)
    
    async def _continuous_tuning(self, fitness_function: Callable) -> Dict[str, Any]:
        """Continuous parameter tuning approach"""
        current_config = {name: param.current_value for name, param in self.parameters.items()}
        current_fitness = await self._evaluate_fitness(current_config, fitness_function)
        
        improvements_made = []
        
        # Try small adjustments to each parameter
        for param_name, param in self.parameters.items():
            # Try increasing the parameter
            test_config = current_config.copy()
            adjustment = param.adaptation_rate * (param.max_value - param.min_value)
            test_config[param_name] = min(param.max_value, param.current_value + adjustment)
            
            test_fitness = await self._evaluate_fitness(test_config, fitness_function)
            
            if test_fitness > current_fitness:
                param.update_value(test_config[param_name], test_fitness)
                current_fitness = test_fitness
                improvements_made.append({
                    "parameter": param_name,
                    "old_value": current_config[param_name],
                    "new_value": test_config[param_name],
                    "fitness_improvement": test_fitness - current_fitness
                })
            else:
                # Try decreasing the parameter
                test_config[param_name] = max(param.min_value, param.current_value - adjustment)
                test_fitness = await self._evaluate_fitness(test_config, fitness_function)
                
                if test_fitness > current_fitness:
                    param.update_value(test_config[param_name], test_fitness)
                    current_fitness = test_fitness
                    improvements_made.append({
                        "parameter": param_name,
                        "old_value": current_config[param_name],
                        "new_value": test_config[param_name],
                        "fitness_improvement": test_fitness - current_fitness
                    })
        
        # Update best if improved
        if current_fitness > self.best_fitness:
            self.best_fitness = current_fitness
            self.best_parameters = {name: param.current_value for name, param in self.parameters.items()}
        
        optimization_result = {
            "generation": self.generation_count,
            "strategy": self.strategy.value,
            "current_fitness": current_fitness,
            "best_fitness": self.best_fitness,
            "improvements_made": improvements_made,
            "parameter_values": {name: param.current_value for name, param in self.parameters.items()},
            "convergence_estimate": self._estimate_convergence()
        }
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    async def _evolutionary_optimization(self, fitness_function: Callable) -> Dict[str, Any]:
        """Evolutionary optimization approach"""
        population_size = 10
        mutation_rate = 0.1
        
        # Generate population
        population = []
        for _ in range(population_size):
            individual = {}
            for param_name, param in self.parameters.items():
                # Random value within bounds
                individual[param_name] = random.uniform(param.min_value, param.max_value)
            population.append(individual)
        
        # Evaluate fitness for each individual
        fitness_scores = []
        for individual in population:
            fitness = await self._evaluate_fitness(individual, fitness_function)
            fitness_scores.append(fitness)
        
        # Select best individuals
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        best_individuals = [population[i] for i in sorted_indices[:population_size//2]]
        
        # Update parameters with best individual
        best_individual = best_individuals[0]
        best_fitness = fitness_scores[sorted_indices[0]]
        
        for param_name, value in best_individual.items():
            self.parameters[param_name].update_value(value, best_fitness)
        
        if best_fitness > self.best_fitness:
            self.best_fitness = best_fitness
            self.best_parameters = best_individual.copy()
        
        return {
            "generation": self.generation_count,
            "strategy": self.strategy.value,
            "current_fitness": best_fitness,
            "best_fitness": self.best_fitness,
            "population_size": population_size,
            "parameter_values": best_individual,
            "convergence_estimate": self._estimate_convergence()
        }
    
    async def _gradient_optimization(self, fitness_function: Callable) -> Dict[str, Any]:
        """Gradient-based optimization approach"""
        current_config = {name: param.current_value for name, param in self.parameters.items()}
        current_fitness = await self._evaluate_fitness(current_config, fitness_function)
        
        # Estimate gradients
        gradients = {}
        epsilon = 0.01
        
        for param_name, param in self.parameters.items():
            # Forward difference
            test_config = current_config.copy()
            test_config[param_name] = min(param.max_value, param.current_value + epsilon)
            forward_fitness = await self._evaluate_fitness(test_config, fitness_function)
            
            gradient = (forward_fitness - current_fitness) / epsilon
            gradients[param_name] = gradient
        
        # Update parameters using gradients
        for param_name, param in self.parameters.items():
            gradient = gradients[param_name]
            new_value = param.current_value + self.learning_rate * gradient
            new_value = max(param.min_value, min(param.max_value, new_value))
            param.update_value(new_value, current_fitness)
        
        # Evaluate new configuration
        new_config = {name: param.current_value for name, param in self.parameters.items()}
        new_fitness = await self._evaluate_fitness(new_config, fitness_function)
        
        if new_fitness > self.best_fitness:
            self.best_fitness = new_fitness
            self.best_parameters = new_config.copy()
        
        return {
            "generation": self.generation_count,
            "strategy": self.strategy.value,
            "current_fitness": new_fitness,
            "best_fitness": self.best_fitness,
            "gradients": gradients,
            "parameter_values": new_config,
            "convergence_estimate": self._estimate_convergence()
        }
    
    async def _hybrid_optimization(self, fitness_function: Callable) -> Dict[str, Any]:
        """Hybrid optimization combining multiple strategies"""
        # Alternate between strategies based on generation
        if self.generation_count % 3 == 0:
            return await self._evolutionary_optimization(fitness_function)
        elif self.generation_count % 3 == 1:
            return await self._gradient_optimization(fitness_function)
        else:
            return await self._continuous_tuning(fitness_function)
    
    async def _evaluate_fitness(self, parameter_config: Dict[str, float], fitness_function: Callable) -> float:
        """Evaluate fitness for a parameter configuration"""
        try:
            if asyncio.iscoroutinefunction(fitness_function):
                return await fitness_function(parameter_config)
            else:
                return fitness_function(parameter_config)
        except Exception as e:
            logger.error(f"Fitness evaluation failed: {e}")
            return 0.0
    
    def _estimate_convergence(self) -> float:
        """Estimate how close the algorithm is to convergence"""
        if len(self.optimization_history) < 5:
            return 0.0
        
        recent_fitness = [h["current_fitness"] for h in self.optimization_history[-5:]]
        fitness_variance = sum((f - sum(recent_fitness)/len(recent_fitness))**2 for f in recent_fitness) / len(recent_fitness)
        
        # Lower variance indicates higher convergence
        convergence = max(0.0, 1.0 - math.sqrt(fitness_variance))
        return convergence
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive optimization summary"""
        return {
            "generation_count": self.generation_count,
            "strategy": self.strategy.value,
            "best_fitness": self.best_fitness,
            "best_parameters": self.best_parameters.copy(),
            "current_parameters": {name: param.current_value for name, param in self.parameters.items()},
            "parameter_trends": {name: param.get_trend() for name, param in self.parameters.items()},
            "convergence_estimate": self._estimate_convergence(),
            "optimization_history_length": len(self.optimization_history)
        }


class FitnessLandscapeMapper:
    """Maps and visualizes evolutionary fitness landscapes"""
    
    def __init__(self, parameter_names: List[str]):
        self.parameter_names = parameter_names
        self.landscape_points: List[FitnessLandscapePoint] = []
        self.landscape_grid: Dict[Tuple[float, ...], float] = {}
        self.trajectory_points: List[FitnessLandscapePoint] = []
        
    def add_evaluation_point(self, parameters: Dict[str, float], fitness: float, generation: int = 0):
        """Add a point to the fitness landscape"""
        point = FitnessLandscapePoint(
            coordinates=parameters.copy(),
            fitness_value=fitness,
            timestamp=time.time(),
            generation=generation
        )
        
        self.landscape_points.append(point)
        self.trajectory_points.append(point)
        
        # Update grid representation
        grid_coords = self._discretize_coordinates(parameters)
        if grid_coords in self.landscape_grid:
            # Average with existing value
            existing_fitness = self.landscape_grid[grid_coords]
            self.landscape_grid[grid_coords] = (existing_fitness + fitness) / 2
        else:
            self.landscape_grid[grid_coords] = fitness
    
    def _discretize_coordinates(self, parameters: Dict[str, float], resolution: int = 20) -> Tuple[float, ...]:
        """Discretize parameter coordinates for grid representation"""
        coords = []
        for param_name in self.parameter_names:
            if param_name in parameters:
                # Normalize to 0-1 range and discretize
                normalized = max(0, min(1, parameters[param_name]))
                discretized = round(normalized * resolution) / resolution
                coords.append(discretized)
            else:
                coords.append(0.0)
        return tuple(coords)
    
    def map_fitness_surface(self, parameter_ranges: Dict[str, Tuple[float, float]], resolution: int = 10) -> Dict[str, Any]:
        """Create a fitness surface map"""
        if len(self.parameter_names) != 2:
            logger.warning("Fitness surface mapping currently supports only 2 parameters")
            return {"error": "unsupported_dimension"}
        
        param1, param2 = self.parameter_names[:2]
        range1 = parameter_ranges.get(param1, (0.0, 1.0))
        range2 = parameter_ranges.get(param2, (0.0, 1.0))
        
        surface_data = []
        
        for i in range(resolution + 1):
            row = []
            for j in range(resolution + 1):
                x = range1[0] + (range1[1] - range1[0]) * i / resolution
                y = range2[0] + (range2[1] - range2[0]) * j / resolution
                
                coords = (round(x * resolution) / resolution, round(y * resolution) / resolution)
                fitness = self.landscape_grid.get(coords, 0.0)
                
                row.append({
                    "x": x,
                    "y": y,
                    "fitness": fitness
                })
            surface_data.append(row)
        
        return {
            "parameter_names": [param1, param2],
            "parameter_ranges": [range1, range2],
            "resolution": resolution,
            "surface_data": surface_data,
            "data_points": len(self.landscape_points)
        }
    
    def get_optimization_trajectory(self) -> Dict[str, Any]:
        """Get the optimization trajectory through the fitness landscape"""
        if not self.trajectory_points:
            return {"trajectory": [], "statistics": {}}
        
        trajectory = []
        for point in self.trajectory_points:
            trajectory.append({
                "timestamp": point.timestamp,
                "generation": point.generation,
                "parameters": point.coordinates.copy(),
                "fitness": point.fitness_value
            })
        
        # Calculate trajectory statistics
        fitness_values = [p.fitness_value for p in self.trajectory_points]
        
        statistics = {
            "total_points": len(trajectory),
            "fitness_range": [min(fitness_values), max(fitness_values)],
            "fitness_improvement": fitness_values[-1] - fitness_values[0] if len(fitness_values) > 1 else 0.0,
            "average_fitness": sum(fitness_values) / len(fitness_values),
            "convergence_trend": self._calculate_convergence_trend(fitness_values)
        }
        
        return {
            "trajectory": trajectory,
            "statistics": statistics
        }
    
    def _calculate_convergence_trend(self, fitness_values: List[float]) -> str:
        """Calculate the convergence trend of the optimization"""
        if len(fitness_values) < 3:
            return "insufficient_data"
        
        # Look at the trend in the last half of the data
        mid_point = len(fitness_values) // 2
        early_avg = sum(fitness_values[:mid_point]) / mid_point
        late_avg = sum(fitness_values[mid_point:]) / (len(fitness_values) - mid_point)
        
        improvement_rate = (late_avg - early_avg) / early_avg if early_avg != 0 else 0.0
        
        if improvement_rate > 0.05:
            return "improving"
        elif improvement_rate < -0.05:
            return "degrading"
        else:
            return "converging"
    
    def identify_fitness_peaks(self, threshold_percentile: float = 90) -> List[Dict[str, Any]]:
        """Identify high-fitness regions in the landscape"""
        if not self.landscape_points:
            return []
        
        fitness_values = [p.fitness_value for p in self.landscape_points]
        threshold = sorted(fitness_values)[int(len(fitness_values) * threshold_percentile / 100)]
        
        peaks = []
        for point in self.landscape_points:
            if point.fitness_value >= threshold:
                peaks.append({
                    "parameters": point.coordinates.copy(),
                    "fitness": point.fitness_value,
                    "generation": point.generation,
                    "timestamp": point.timestamp
                })
        
        return sorted(peaks, key=lambda p: p["fitness"], reverse=True)
    
    def get_landscape_summary(self) -> Dict[str, Any]:
        """Get comprehensive fitness landscape summary"""
        if not self.landscape_points:
            return {"status": "no_data"}
        
        fitness_values = [p.fitness_value for p in self.landscape_points]
        
        return {
            "parameter_names": self.parameter_names,
            "total_evaluations": len(self.landscape_points),
            "fitness_statistics": {
                "min": min(fitness_values),
                "max": max(fitness_values),
                "average": sum(fitness_values) / len(fitness_values),
                "range": max(fitness_values) - min(fitness_values)
            },
            "landscape_coverage": len(self.landscape_grid),
            "optimization_progress": self._calculate_convergence_trend(fitness_values),
            "recent_performance": fitness_values[-10:] if len(fitness_values) >= 10 else fitness_values
        }


class AdaptiveOptimizationEngine:
    """Main engine coordinating all adaptive optimization components"""
    
    def __init__(self, 
                 parameters: List[AdaptiveParameter],
                 benchmark_config: Optional[ContinuousBenchmarkConfig] = None,
                 strategy: AdaptiveStrategy = AdaptiveStrategy.HYBRID_ADAPTIVE):
        
        self.parameters = parameters
        self.strategy = strategy
        
        # Initialize components
        self.benchmark_config = benchmark_config or ContinuousBenchmarkConfig()
        self.continuous_benchmark = ContinuousPerformanceBenchmark(self.benchmark_config)
        self.self_tuning_algorithm = SelfTuningAlgorithm(parameters, strategy)
        self.fitness_mapper = FitnessLandscapeMapper([p.name for p in parameters])
        
        # Engine state
        self.running = False
        self.optimization_task = None
        self.adaptation_cycles = 0
        self.total_improvements = 0
        
        # Performance tracking
        self.adaptation_history: List[Dict[str, Any]] = []
        self.effectiveness_metrics: Dict[str, float] = {}
    
    async def start_adaptive_optimization(self, benchmark_function: Callable, fitness_function: Callable):
        """Start the adaptive optimization engine"""
        if self.running:
            logger.warning("Adaptive optimization already running")
            return
        
        self.running = True
        
        # Start continuous monitoring
        await self.continuous_benchmark.start_continuous_monitoring(benchmark_function)
        
        # Start optimization loop
        self.optimization_task = asyncio.create_task(
            self._adaptive_optimization_loop(fitness_function)
        )
        
        logger.info("🚀 Started adaptive optimization engine")
    
    async def stop_adaptive_optimization(self):
        """Stop the adaptive optimization engine"""
        self.running = False
        
        # Stop continuous monitoring
        await self.continuous_benchmark.stop_continuous_monitoring()
        
        # Stop optimization loop
        if self.optimization_task:
            self.optimization_task.cancel()
            try:
                await self.optimization_task
            except asyncio.CancelledError:
                pass
        
        logger.info("⏹️ Stopped adaptive optimization engine")
    
    async def _adaptive_optimization_loop(self, fitness_function: Callable):
        """Main adaptive optimization loop"""
        optimization_interval = 120.0  # Run optimization every 2 minutes
        
        while self.running:
            try:
                # Execute optimization cycle
                await self._execute_optimization_cycle(fitness_function)
                
                # Wait for next cycle
                await asyncio.sleep(optimization_interval)
                
            except Exception as e:
                logger.error(f"Error in adaptive optimization loop: {e}")
                await asyncio.sleep(optimization_interval)
    
    async def _execute_optimization_cycle(self, fitness_function: Callable):
        """Execute one complete optimization cycle"""
        cycle_start = time.time()
        self.adaptation_cycles += 1
        
        logger.info(f"🔄 Starting optimization cycle {self.adaptation_cycles}")
        
        # Check if adaptation is needed
        performance_summary = self.continuous_benchmark.get_performance_summary()
        
        adaptation_needed = self._should_trigger_adaptation(performance_summary)
        
        if adaptation_needed:
            # Execute parameter optimization
            optimization_result = await self.self_tuning_algorithm.optimize_parameters(fitness_function)
            
            # Record landscape point
            current_params = {p.name: p.current_value for p in self.parameters}
            current_fitness = optimization_result.get("current_fitness", 0.0)
            
            self.fitness_mapper.add_evaluation_point(
                current_params, 
                current_fitness, 
                self.adaptation_cycles
            )
            
            # Check for improvements
            if optimization_result.get("current_fitness", 0) > optimization_result.get("best_fitness", 0) * 0.95:
                self.total_improvements += 1
            
            # Record adaptation cycle
            cycle_result = {
                "cycle": self.adaptation_cycles,
                "timestamp": cycle_start,
                "duration": time.time() - cycle_start,
                "optimization_result": optimization_result,
                "performance_summary": performance_summary,
                "adaptation_triggered": True,
                "improvements_made": optimization_result.get("improvements_made", [])
            }
            
            self.adaptation_history.append(cycle_result)
            
            # Update effectiveness metrics
            self._update_effectiveness_metrics()
            
            logger.info(f"✅ Completed optimization cycle {self.adaptation_cycles} "
                       f"(fitness: {current_fitness:.3f}, improvements: {self.total_improvements})")
        else:
            logger.info(f"⏭️ Skipped optimization cycle {self.adaptation_cycles} - no adaptation needed")
    
    def _should_trigger_adaptation(self, performance_summary: Dict[str, Any]) -> bool:
        """Determine if adaptation should be triggered"""
        # Always adapt on the first few cycles
        if self.adaptation_cycles < 3:
            return True
        
        # Check for performance regression
        if performance_summary.get("regression_alerts_count", 0) > 0:
            return True
        
        # Check for degrading trends
        trends = performance_summary.get("trends", {})
        degrading_metrics = [metric for metric, trend in trends.items() if trend == "degrading"]
        
        if len(degrading_metrics) >= 2:
            return True
        
        # Periodic adaptation (every 10 cycles)
        if self.adaptation_cycles % 10 == 0:
            return True
        
        return False
    
    def _update_effectiveness_metrics(self):
        """Update adaptive optimization effectiveness metrics"""
        if len(self.adaptation_history) < 2:
            return
        
        # Calculate improvement rate
        recent_cycles = self.adaptation_history[-10:]
        total_cycles = len(recent_cycles)
        cycles_with_improvements = sum(1 for cycle in recent_cycles if cycle.get("improvements_made", []))
        
        self.effectiveness_metrics.update({
            "improvement_rate": cycles_with_improvements / total_cycles if total_cycles > 0 else 0.0,
            "total_adaptation_cycles": self.adaptation_cycles,
            "total_improvements": self.total_improvements,
            "average_cycle_duration": sum(c.get("duration", 0) for c in recent_cycles) / len(recent_cycles),
            "convergence_estimate": self.self_tuning_algorithm._estimate_convergence()
        })
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the adaptive optimization system"""
        return {
            "engine_status": {
                "running": self.running,
                "adaptation_cycles": self.adaptation_cycles,
                "total_improvements": self.total_improvements,
                "strategy": self.strategy.value
            },
            "performance_monitoring": self.continuous_benchmark.get_performance_summary(),
            "parameter_optimization": self.self_tuning_algorithm.get_optimization_summary(),
            "fitness_landscape": self.fitness_mapper.get_landscape_summary(),
            "effectiveness_metrics": self.effectiveness_metrics.copy(),
            "recent_adaptations": self.adaptation_history[-5:] if self.adaptation_history else []
        }
    
    def validate_adaptive_improvement(self) -> Dict[str, Any]:
        """Validate the effectiveness of adaptive improvements"""
        if len(self.adaptation_history) < 5:
            return {
                "status": "insufficient_data",
                "message": "Need at least 5 adaptation cycles for validation"
            }
        
        # Analyze improvement trends
        fitness_trajectory = []
        for cycle in self.adaptation_history:
            opt_result = cycle.get("optimization_result", {})
            fitness_trajectory.append(opt_result.get("current_fitness", 0.0))
        
        # Calculate validation metrics
        initial_fitness = fitness_trajectory[0]
        final_fitness = fitness_trajectory[-1]
        max_fitness = max(fitness_trajectory)
        
        improvement_percentage = ((final_fitness - initial_fitness) / initial_fitness * 100) if initial_fitness > 0 else 0.0
        stability_score = 1.0 - (abs(final_fitness - max_fitness) / max_fitness) if max_fitness > 0 else 0.0
        
        # Convergence analysis
        recent_variance = sum((f - final_fitness)**2 for f in fitness_trajectory[-5:]) / 5
        convergence_achieved = recent_variance < 0.01
        
        validation_result = {
            "improvement_achieved": improvement_percentage > 5.0,  # At least 5% improvement
            "improvement_percentage": improvement_percentage,
            "stability_achieved": stability_score > 0.8,
            "stability_score": stability_score,
            "convergence_achieved": convergence_achieved,
            "convergence_variance": recent_variance,
            "fitness_trajectory": fitness_trajectory,
            "validation_summary": {
                "overall_success": improvement_percentage > 5.0 and stability_score > 0.8,
                "initial_fitness": initial_fitness,
                "final_fitness": final_fitness,
                "max_fitness": max_fitness,
                "total_cycles": len(self.adaptation_history)
            }
        }
        
        return validation_result


# Factory functions for easy instantiation
def create_adaptive_optimization_engine(
    parameter_configs: List[Dict[str, Any]],
    strategy: AdaptiveStrategy = AdaptiveStrategy.HYBRID_ADAPTIVE,
    benchmark_config: Optional[Dict[str, Any]] = None
) -> AdaptiveOptimizationEngine:
    """Create and configure an adaptive optimization engine"""
    
    # Create adaptive parameters
    parameters = []
    for config in parameter_configs:
        param = AdaptiveParameter(
            name=config["name"],
            current_value=config.get("initial_value", 0.5),
            min_value=config.get("min_value", 0.0),
            max_value=config.get("max_value", 1.0),
            adaptation_rate=config.get("adaptation_rate", 0.1)
        )
        parameters.append(param)
    
    # Create benchmark config
    bench_config = None
    if benchmark_config:
        bench_config = ContinuousBenchmarkConfig(
            benchmark_interval_seconds=benchmark_config.get("interval", 30.0),
            performance_window_size=benchmark_config.get("window_size", 100),
            regression_threshold=benchmark_config.get("regression_threshold", 0.1)
        )
    
    return AdaptiveOptimizationEngine(parameters, bench_config, strategy)


# Example usage and demo functions
async def demo_adaptive_optimization():
    """Demonstrate the adaptive optimization system"""
    logger.info("🎯 Starting Adaptive Optimization Demo")
    
    # Define optimization parameters
    parameter_configs = [
        {"name": "learning_rate", "initial_value": 0.1, "min_value": 0.01, "max_value": 0.5},
        {"name": "batch_size", "initial_value": 32, "min_value": 8, "max_value": 128},
        {"name": "regularization", "initial_value": 0.01, "min_value": 0.001, "max_value": 0.1}
    ]
    
    # Create adaptive optimization engine
    engine = create_adaptive_optimization_engine(
        parameter_configs,
        strategy=AdaptiveStrategy.HYBRID_ADAPTIVE
    )
    
    # Define mock benchmark and fitness functions
    async def mock_benchmark():
        """Mock benchmark function"""
        return {
            "latency_ms": random.uniform(1.0, 10.0),
            "throughput_ops_sec": random.uniform(100.0, 1000.0),
            "memory_usage_mb": random.uniform(50.0, 200.0),
            "efficiency_score": random.uniform(0.5, 1.0)
        }
    
    def mock_fitness(parameters):
        """Mock fitness function that rewards certain parameter combinations"""
        # Simple fitness function that prefers balanced parameters
        lr = parameters.get("learning_rate", 0.1)
        bs = parameters.get("batch_size", 32)
        reg = parameters.get("regularization", 0.01)
        
        # Optimal values are around lr=0.01, bs=64, reg=0.05
        lr_fitness = 1.0 - abs(lr - 0.01) / 0.5
        bs_fitness = 1.0 - abs(bs - 64) / 128
        reg_fitness = 1.0 - abs(reg - 0.05) / 0.1
        
        return (lr_fitness + bs_fitness + reg_fitness) / 3.0
    
    try:
        # Start adaptive optimization
        await engine.start_adaptive_optimization(mock_benchmark, mock_fitness)
        
        # Let it run for a while
        await asyncio.sleep(10)  # Run for 10 seconds in demo
        
        # Get status and validation
        status = engine.get_comprehensive_status()
        validation = engine.validate_adaptive_improvement()
        
        logger.info("📊 Adaptive Optimization Status:")
        logger.info(f"   - Adaptation Cycles: {status['engine_status']['adaptation_cycles']}")
        logger.info(f"   - Total Improvements: {status['engine_status']['total_improvements']}")
        logger.info(f"   - Effectiveness Rate: {status['effectiveness_metrics'].get('improvement_rate', 0):.1%}")
        
        logger.info("🎯 Validation Results:")
        validation_summary = validation.get("validation_summary", {})
        logger.info(f"   - Overall Success: {validation_summary.get('overall_success', False)}")
        logger.info(f"   - Improvement: {validation.get('improvement_percentage', 0):.1f}%")
        logger.info(f"   - Stability: {validation.get('stability_score', 0):.1%}")
        
    finally:
        # Stop the engine
        await engine.stop_adaptive_optimization()
    
    logger.info("✅ Adaptive Optimization Demo Complete")
    return status, validation


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_adaptive_optimization())