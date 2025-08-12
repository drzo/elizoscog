#!/usr/bin/env python3
"""
Performance Profiling and Resource Management for ElizaOS-OpenCog-GnuCash Microservices

This module provides:
- Automated performance profiling
- Memory leak detection
- CPU optimization monitoring  
- Resource utilization tracking
- AI-driven performance optimization
"""

import asyncio
import time
import psutil
import logging
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from memory_profiler import profile
import functools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    response_time_ms: float
    requests_per_second: float
    active_connections: int
    error_rate: float
    service_name: str
    

@dataclass
class ResourceLimits:
    """Resource limits configuration"""
    max_memory_mb: int = 1024
    max_cpu_percent: float = 80.0
    max_response_time_ms: float = 1000.0
    max_error_rate: float = 0.05
    memory_alert_threshold: float = 0.85
    cpu_alert_threshold: float = 0.70


class PerformanceProfiler:
    """
    Advanced performance profiler with AI-driven optimization
    """
    
    def __init__(self, service_name: str, resource_limits: Optional[ResourceLimits] = None):
        self.service_name = service_name
        self.resource_limits = resource_limits or ResourceLimits()
        self.metrics_history: List[PerformanceMetrics] = []
        self.profiling_active = False
        self.profiling_thread = None
        self.optimization_rules = {}
        
        # Performance counters
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.last_metrics_time = time.time()
        
        # Memory leak detection
        self.memory_baseline = None
        self.memory_leak_threshold = 50  # MB growth over baseline
        
        logger.info(f"Performance profiler initialized for service: {service_name}")
    
    def start_profiling(self, interval: float = 30.0):
        """Start continuous performance profiling"""
        if self.profiling_active:
            logger.warning("Profiling already active")
            return
        
        self.profiling_active = True
        self.profiling_thread = threading.Thread(
            target=self._profiling_loop,
            args=(interval,),
            daemon=True
        )
        self.profiling_thread.start()
        logger.info(f"Performance profiling started with {interval}s interval")
    
    def stop_profiling(self):
        """Stop performance profiling"""
        self.profiling_active = False
        if self.profiling_thread and self.profiling_thread.is_alive():
            self.profiling_thread.join(timeout=5)
        logger.info("Performance profiling stopped")
    
    def _profiling_loop(self, interval: float):
        """Main profiling loop"""
        while self.profiling_active:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 1000 metrics to prevent memory issues
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-500:]
                
                # Check for performance issues
                self._analyze_performance(metrics)
                
                # Memory leak detection
                self._detect_memory_leaks(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in profiling loop: {e}")
                time.sleep(interval)
    
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        current_time = time.time()
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)
        memory_percent = memory.percent
        
        # Calculate request metrics
        time_window = current_time - self.last_metrics_time
        rps = self.request_count / max(time_window, 1.0)
        avg_response_time = (self.total_response_time / max(self.request_count, 1)) if self.request_count > 0 else 0
        error_rate = self.error_count / max(self.request_count, 1) if self.request_count > 0 else 0
        
        # Get network connections (approximation for active connections)
        try:
            connections = len(psutil.net_connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            connections = 0
        
        metrics = PerformanceMetrics(
            timestamp=current_time,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            response_time_ms=avg_response_time,
            requests_per_second=rps,
            active_connections=connections,
            error_rate=error_rate,
            service_name=self.service_name
        )
        
        # Reset counters
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.last_metrics_time = current_time
        
        return metrics
    
    def record_request(self, response_time_ms: float, success: bool = True):
        """Record a request for metrics calculation"""
        self.request_count += 1
        self.total_response_time += response_time_ms
        if not success:
            self.error_count += 1
    
    def _analyze_performance(self, metrics: PerformanceMetrics):
        """Analyze performance metrics and trigger alerts"""
        alerts = []
        
        # Check CPU usage
        if metrics.cpu_percent > self.resource_limits.max_cpu_percent:
            alerts.append({
                "type": "cpu_high",
                "severity": "warning" if metrics.cpu_percent < 90 else "critical",
                "message": f"High CPU usage: {metrics.cpu_percent:.1f}%",
                "threshold": self.resource_limits.max_cpu_percent
            })
        
        # Check memory usage
        if metrics.memory_mb > self.resource_limits.max_memory_mb:
            alerts.append({
                "type": "memory_high",
                "severity": "warning" if metrics.memory_mb < self.resource_limits.max_memory_mb * 1.2 else "critical",
                "message": f"High memory usage: {metrics.memory_mb:.1f} MB",
                "threshold": self.resource_limits.max_memory_mb
            })
        
        # Check response time
        if metrics.response_time_ms > self.resource_limits.max_response_time_ms:
            alerts.append({
                "type": "response_time_high", 
                "severity": "warning" if metrics.response_time_ms < 2000 else "critical",
                "message": f"Slow response time: {metrics.response_time_ms:.1f}ms",
                "threshold": self.resource_limits.max_response_time_ms
            })
        
        # Check error rate
        if metrics.error_rate > self.resource_limits.max_error_rate:
            alerts.append({
                "type": "error_rate_high",
                "severity": "critical",
                "message": f"High error rate: {metrics.error_rate:.1%}",
                "threshold": self.resource_limits.max_error_rate
            })
        
        # Log alerts
        for alert in alerts:
            if alert["severity"] == "critical":
                logger.error(f"CRITICAL ALERT [{self.service_name}]: {alert['message']}")
            else:
                logger.warning(f"WARNING [{self.service_name}]: {alert['message']}")
    
    def _detect_memory_leaks(self, metrics: PerformanceMetrics):
        """Detect potential memory leaks"""
        if self.memory_baseline is None:
            self.memory_baseline = metrics.memory_mb
            logger.info(f"Memory baseline established: {self.memory_baseline:.1f} MB")
            return
        
        memory_growth = metrics.memory_mb - self.memory_baseline
        
        if memory_growth > self.memory_leak_threshold:
            logger.warning(
                f"MEMORY LEAK DETECTED [{self.service_name}]: "
                f"Growth of {memory_growth:.1f} MB over baseline "
                f"(threshold: {self.memory_leak_threshold} MB)"
            )
            
            # Update baseline if growth is sustained
            if len(self.metrics_history) >= 10:
                recent_memory = [m.memory_mb for m in self.metrics_history[-10:]]
                if all(mem > self.memory_baseline + self.memory_leak_threshold for mem in recent_memory):
                    logger.info(f"Updating memory baseline due to sustained growth")
                    self.memory_baseline = min(recent_memory)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics_history:
            return {"error": "No metrics collected yet"}
        
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_mb for m in recent_metrics] 
        response_times = [m.response_time_ms for m in recent_metrics if m.response_time_ms > 0]
        rps_values = [m.requests_per_second for m in recent_metrics if m.requests_per_second > 0]
        
        report = {
            "service_name": self.service_name,
            "report_timestamp": time.time(),
            "metrics_collected": len(self.metrics_history),
            "performance_summary": {
                "cpu_usage": {
                    "current": cpu_values[-1] if cpu_values else 0,
                    "average": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    "max": max(cpu_values) if cpu_values else 0,
                    "threshold": self.resource_limits.max_cpu_percent
                },
                "memory_usage": {
                    "current_mb": memory_values[-1] if memory_values else 0,
                    "average_mb": sum(memory_values) / len(memory_values) if memory_values else 0,
                    "max_mb": max(memory_values) if memory_values else 0,
                    "baseline_mb": self.memory_baseline,
                    "growth_mb": (memory_values[-1] - self.memory_baseline) if memory_values and self.memory_baseline else 0,
                    "threshold_mb": self.resource_limits.max_memory_mb
                },
                "response_time": {
                    "current_ms": response_times[-1] if response_times else 0,
                    "average_ms": sum(response_times) / len(response_times) if response_times else 0,
                    "max_ms": max(response_times) if response_times else 0,
                    "threshold_ms": self.resource_limits.max_response_time_ms
                },
                "throughput": {
                    "current_rps": rps_values[-1] if rps_values else 0,
                    "average_rps": sum(rps_values) / len(rps_values) if rps_values else 0,
                    "max_rps": max(rps_values) if rps_values else 0
                }
            },
            "recent_metrics": [asdict(m) for m in recent_metrics[-5:]],  # Last 5 metrics
            "optimization_recommendations": self._generate_optimization_recommendations()
        }
        
        return report
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate AI-driven optimization recommendations"""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        # CPU optimization recommendations
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        if avg_cpu > 70:
            recommendations.append("Consider implementing CPU optimization: reduce computational complexity or add caching")
            if avg_cpu > 85:
                recommendations.append("URGENT: Consider horizontal scaling - CPU usage consistently high")
        
        # Memory optimization recommendations  
        if self.memory_baseline and recent_metrics:
            memory_growth = recent_metrics[-1].memory_mb - self.memory_baseline
            if memory_growth > 30:
                recommendations.append("Investigate potential memory leaks - implement memory profiling")
                recommendations.append("Consider implementing object pooling or garbage collection tuning")
        
        # Response time optimization
        avg_response_time = sum(m.response_time_ms for m in recent_metrics if m.response_time_ms > 0) / max(len([m for m in recent_metrics if m.response_time_ms > 0]), 1)
        if avg_response_time > 500:
            recommendations.append("Optimize response times: implement caching, database query optimization, or async processing")
            if avg_response_time > 1000:
                recommendations.append("CRITICAL: Response times exceed 1s - consider load balancing or service decomposition")
        
        # Throughput optimization
        avg_rps = sum(m.requests_per_second for m in recent_metrics if m.requests_per_second > 0) / max(len([m for m in recent_metrics if m.requests_per_second > 0]), 1)
        if avg_rps < 5:
            recommendations.append("Low throughput detected - consider connection pooling or async request handling")
        
        # Error rate recommendations
        avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
        if avg_error_rate > 0.01:  # > 1%
            recommendations.append("High error rate detected - implement better error handling and retry mechanisms")
        
        return recommendations


class CognitiveResourceManager:
    """
    AI-driven resource management with cognitive load balancing
    """
    
    def __init__(self):
        self.service_profilers: Dict[str, PerformanceProfiler] = {}
        self.resource_allocation_rules = {}
        self.cognitive_models = {}
        logger.info("Cognitive Resource Manager initialized")
    
    def register_service(self, service_name: str, resource_limits: Optional[ResourceLimits] = None) -> PerformanceProfiler:
        """Register a service for performance monitoring"""
        profiler = PerformanceProfiler(service_name, resource_limits)
        self.service_profilers[service_name] = profiler
        profiler.start_profiling()
        logger.info(f"Service registered for monitoring: {service_name}")
        return profiler
    
    def get_system_performance_report(self) -> Dict[str, Any]:
        """Generate system-wide performance report"""
        system_report = {
            "timestamp": time.time(),
            "services_monitored": len(self.service_profilers),
            "system_summary": {
                "total_cpu_usage": 0,
                "total_memory_usage": 0,
                "average_response_time": 0,
                "total_throughput": 0,
                "services_with_issues": 0
            },
            "service_reports": {},
            "cognitive_recommendations": []
        }
        
        total_cpu = 0
        total_memory = 0
        total_response_times = []
        total_rps = 0
        services_with_issues = 0
        
        for service_name, profiler in self.service_profilers.items():
            service_report = profiler.get_performance_report()
            system_report["service_reports"][service_name] = service_report
            
            if "error" not in service_report:
                perf_summary = service_report["performance_summary"]
                total_cpu += perf_summary["cpu_usage"]["current"]
                total_memory += perf_summary["memory_usage"]["current_mb"]
                
                if perf_summary["response_time"]["current_ms"] > 0:
                    total_response_times.append(perf_summary["response_time"]["current_ms"])
                
                total_rps += perf_summary["throughput"]["current_rps"]
                
                # Check for issues
                if (perf_summary["cpu_usage"]["current"] > 70 or 
                    perf_summary["memory_usage"]["current_mb"] > 800 or
                    perf_summary["response_time"]["current_ms"] > 1000):
                    services_with_issues += 1
        
        # Update system summary
        system_report["system_summary"]["total_cpu_usage"] = total_cpu
        system_report["system_summary"]["total_memory_usage"] = total_memory
        system_report["system_summary"]["average_response_time"] = sum(total_response_times) / max(len(total_response_times), 1)
        system_report["system_summary"]["total_throughput"] = total_rps
        system_report["system_summary"]["services_with_issues"] = services_with_issues
        
        # Generate cognitive recommendations
        system_report["cognitive_recommendations"] = self._generate_cognitive_recommendations(system_report)
        
        return system_report
    
    def _generate_cognitive_recommendations(self, system_report: Dict[str, Any]) -> List[str]:
        """Generate AI-driven system optimization recommendations"""
        recommendations = []
        summary = system_report["system_summary"]
        
        # System-level recommendations
        if summary["services_with_issues"] > 0:
            recommendations.append(f"System Alert: {summary['services_with_issues']} service(s) experiencing performance issues")
        
        if summary["total_cpu_usage"] > 200:  # Assuming 4-core system
            recommendations.append("System CPU usage high - consider vertical scaling or load distribution")
        
        if summary["total_memory_usage"] > 6000:  # 6GB threshold
            recommendations.append("System memory usage high - implement memory optimization strategies")
        
        if summary["average_response_time"] > 800:
            recommendations.append("System-wide response time degradation - investigate bottlenecks")
        
        # Cognitive load balancing recommendations
        service_loads = []
        for service_name, report in system_report["service_reports"].items():
            if "error" not in report:
                load_score = (
                    report["performance_summary"]["cpu_usage"]["current"] * 0.4 +
                    (report["performance_summary"]["memory_usage"]["current_mb"] / 10) * 0.3 +
                    (report["performance_summary"]["response_time"]["current_ms"] / 10) * 0.3
                )
                service_loads.append((service_name, load_score))
        
        # Sort by load and provide recommendations
        service_loads.sort(key=lambda x: x[1], reverse=True)
        
        if len(service_loads) > 1:
            high_load_service = service_loads[0]
            low_load_service = service_loads[-1]
            
            if high_load_service[1] > low_load_service[1] * 2:
                recommendations.append(
                    f"Load imbalance detected: {high_load_service[0]} is heavily loaded "
                    f"while {low_load_service[0]} has capacity - consider request redistribution"
                )
        
        return recommendations
    
    def cleanup(self):
        """Clean up all profilers"""
        for profiler in self.service_profilers.values():
            profiler.stop_profiling()
        logger.info("Cognitive Resource Manager cleanup completed")


def performance_profile(func):
    """
    Decorator for profiling function performance
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            raise
        finally:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            # Try to find associated profiler
            if hasattr(func, '__self__') and hasattr(func.__self__, 'profiler'):
                func.__self__.profiler.record_request(response_time, success)
            
            logger.debug(f"Function {func.__name__} executed in {response_time:.2f}ms (success: {success})")
        
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            raise
        finally:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            # Try to find associated profiler
            if hasattr(func, '__self__') and hasattr(func.__self__, 'profiler'):
                func.__self__.profiler.record_request(response_time, success)
            
            logger.debug(f"Function {func.__name__} executed in {response_time:.2f}ms (success: {success})")
        
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Global resource manager instance
global_resource_manager = CognitiveResourceManager()


async def main():
    """
    Demo of performance profiling and resource management
    """
    print("=" * 60)
    print("⚡ ElizaOS-OpenCog-GnuCash Performance Profiling Demo")
    print("=" * 60)
    
    # Register sample services
    profiler1 = global_resource_manager.register_service(
        "financial-service",
        ResourceLimits(max_memory_mb=1024, max_cpu_percent=70)
    )
    
    profiler2 = global_resource_manager.register_service(
        "reasoning-service", 
        ResourceLimits(max_memory_mb=2048, max_cpu_percent=80)
    )
    
    # Simulate some load
    print("\n📊 Simulating service load for 30 seconds...")
    
    for i in range(10):
        # Simulate requests
        profiler1.record_request(random.uniform(50, 200), random.choice([True, True, True, False]))
        profiler2.record_request(random.uniform(100, 500), random.choice([True, True, True, True, False]))
        
        await asyncio.sleep(3)
        
        if i % 3 == 0:
            print(f"   Progress: {((i+1)/10)*100:.0f}% - Collecting metrics...")
    
    # Generate reports
    print("\n📋 Generating Performance Reports...")
    system_report = global_resource_manager.get_system_performance_report()
    
    print(f"\n🎯 System Performance Summary:")
    summary = system_report["system_summary"]
    print(f"   Services monitored: {system_report['services_monitored']}")
    print(f"   Total CPU usage: {summary['total_cpu_usage']:.1f}%")
    print(f"   Total memory usage: {summary['total_memory_usage']:.1f} MB")
    print(f"   Average response time: {summary['average_response_time']:.1f}ms")
    print(f"   Total throughput: {summary['total_throughput']:.1f} RPS")
    print(f"   Services with issues: {summary['services_with_issues']}")
    
    print(f"\n🧠 Cognitive Recommendations ({len(system_report.get('cognitive_recommendations', []))}):")
    for i, rec in enumerate(system_report.get('cognitive_recommendations', [])[:3], 1):
        print(f"   {i}. {rec}")
    
    # Cleanup
    global_resource_manager.cleanup()
    print("\n✅ Performance profiling demo completed!")


if __name__ == "__main__":
    import random
    asyncio.run(main())