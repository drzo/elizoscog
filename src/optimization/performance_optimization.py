"""
Phase 4: Optimization and Scaling - Performance Optimization Module

Implements critical path profiling, caching strategies, and distributed processing
for the ElizaOS-OpenCog-GnuCash integration framework.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import pickle
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance measurement data"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    memory_before: int
    memory_after: int
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None


class PerformanceProfiler:
    """Profiles and optimizes critical paths in the integration framework"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics: List[PerformanceMetric] = []
        self.operation_stats = defaultdict(list)
        self.performance_targets = {
            'simple_query': 0.100,  # 100ms target
            'complex_reasoning': 2.000,  # 2s target
            'financial_analysis': 1.000,  # 1s target
            'cross_ecosystem_call': 0.500  # 500ms target
        }
        
    async def profile_operation(self, operation_name: str, operation_func: Callable, *args, **kwargs):
        """Profile a specific operation and collect metrics"""
        start_time = time.perf_counter()
        memory_before = self._get_memory_usage()
        cpu_before = self._get_cpu_usage()
        
        try:
            if asyncio.iscoroutinefunction(operation_func):
                result = await operation_func(*args, **kwargs)
            else:
                result = operation_func(*args, **kwargs)
            
            end_time = time.perf_counter()
            memory_after = self._get_memory_usage()
            duration = end_time - start_time
            
            metric = PerformanceMetric(
                operation=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_percent=self._get_cpu_usage() - cpu_before,
                success=True
            )
            
            self.metrics.append(metric)
            self.operation_stats[operation_name].append(duration)
            
            # Check against performance targets
            if operation_name in self.performance_targets:
                target = self.performance_targets[operation_name]
                if duration > target:
                    logger.warning(f"Performance target missed for {operation_name}: {duration:.3f}s > {target:.3f}s")
            
            return result
            
        except Exception as e:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            metric = PerformanceMetric(
                operation=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                memory_before=memory_before,
                memory_after=self._get_memory_usage(),
                cpu_percent=self._get_cpu_usage() - cpu_before,
                success=False,
                error_message=str(e)
            )
            
            self.metrics.append(metric)
            raise
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'total_operations': len(self.metrics),
            'successful_operations': sum(1 for m in self.metrics if m.success),
            'failed_operations': sum(1 for m in self.metrics if not m.success),
            'operation_statistics': {},
            'performance_targets': self.performance_targets,
            'recommendations': []
        }
        
        # Calculate statistics per operation type
        for operation, durations in self.operation_stats.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                min_duration = min(durations)
                max_duration = max(durations)
                
                report['operation_statistics'][operation] = {
                    'count': len(durations),
                    'average_duration': avg_duration,
                    'min_duration': min_duration,
                    'max_duration': max_duration,
                    'target_met': avg_duration <= self.performance_targets.get(operation, float('inf'))
                }
                
                # Generate recommendations
                if operation in self.performance_targets:
                    target = self.performance_targets[operation]
                    if avg_duration > target:
                        report['recommendations'].append({
                            'operation': operation,
                            'current_avg': avg_duration,
                            'target': target,
                            'improvement_needed': f"{((avg_duration/target - 1) * 100):.1f}%",
                            'suggestion': self._get_optimization_suggestion(operation, avg_duration, target)
                        })
        
        return report
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage (mock implementation)"""
        # In real implementation, use psutil or similar
        import os
        return os.getpid() % 1000000  # Mock memory usage
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage (mock implementation)"""
        # In real implementation, use psutil
        return time.time() % 100  # Mock CPU usage
    
    def _get_optimization_suggestion(self, operation: str, current: float, target: float) -> str:
        """Generate optimization suggestions based on performance data"""
        suggestions = {
            'simple_query': "Consider implementing query result caching",
            'complex_reasoning': "Consider distributing reasoning across multiple cores",
            'financial_analysis': "Consider pre-computing common financial patterns",
            'cross_ecosystem_call': "Consider connection pooling and async batching"
        }
        return suggestions.get(operation, "Consider general performance optimization techniques")


class CachingStrategy:
    """Advanced caching system for cross-ecosystem integration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.cache_layers = {}
        self.cache_stats = defaultdict(lambda: {'hits': 0, 'misses': 0, 'evictions': 0})
        self.ttl_defaults = {
            'financial_data': 300,  # 5 minutes
            'reasoning_results': 1800,  # 30 minutes
            'user_preferences': 3600,  # 1 hour
            'market_data': 60  # 1 minute
        }
        
        # Initialize cache layers
        self._initialize_cache_layers()
    
    def _initialize_cache_layers(self):
        """Initialize different cache layers with different strategies"""
        # L1: In-memory cache for hot data
        self.cache_layers['l1_memory'] = {
            'data': {},
            'access_times': {},
            'max_size': self.config.get('l1_max_size', 1000),
            'strategy': 'lru'
        }
        
        # L2: Persistent cache for warm data
        self.cache_layers['l2_persistent'] = {
            'data': {},
            'access_times': {},
            'max_size': self.config.get('l2_max_size', 10000),
            'strategy': 'lfu',
            'persist_path': Path(self.config.get('cache_dir', '/tmp/elizoscog_cache'))
        }
        
        # Create cache directory
        if 'l2_persistent' in self.cache_layers:
            self.cache_layers['l2_persistent']['persist_path'].mkdir(parents=True, exist_ok=True)
    
    async def get(self, key: str, category: str = 'default') -> Optional[Any]:
        """Get value from cache with multi-layer lookup"""
        cache_key = self._get_cache_key(key, category)
        
        # Check L1 cache first
        if cache_key in self.cache_layers['l1_memory']['data']:
            self._update_access_time('l1_memory', cache_key)
            self.cache_stats[category]['hits'] += 1
            return self.cache_layers['l1_memory']['data'][cache_key]['value']
        
        # Check L2 cache
        l2_value = await self._get_from_l2(cache_key)
        if l2_value is not None:
            # Promote to L1
            await self.set(key, l2_value, category, promote_to_l1=True)
            self.cache_stats[category]['hits'] += 1
            return l2_value
        
        self.cache_stats[category]['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, category: str = 'default', 
                  ttl: Optional[int] = None, promote_to_l1: bool = True) -> bool:
        """Set value in cache with TTL and layer management"""
        cache_key = self._get_cache_key(key, category)
        ttl = ttl or self.ttl_defaults.get(category, 3600)
        
        cache_entry = {
            'value': value,
            'created_at': time.time(),
            'ttl': ttl,
            'category': category
        }
        
        # Store in L1 if requested and space available
        if promote_to_l1:
            if len(self.cache_layers['l1_memory']['data']) >= self.cache_layers['l1_memory']['max_size']:
                self._evict_from_l1()
            
            self.cache_layers['l1_memory']['data'][cache_key] = cache_entry
            self._update_access_time('l1_memory', cache_key)
        
        # Always store in L2
        await self._set_in_l2(cache_key, cache_entry)
        
        return True
    
    def _get_cache_key(self, key: str, category: str) -> str:
        """Generate consistent cache key"""
        combined = f"{category}:{key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _update_access_time(self, layer: str, cache_key: str):
        """Update access time for LRU/LFU algorithms"""
        self.cache_layers[layer]['access_times'][cache_key] = time.time()
    
    def _evict_from_l1(self):
        """Evict least recently used item from L1 cache"""
        if not self.cache_layers['l1_memory']['access_times']:
            return
        
        # Find LRU item
        lru_key = min(
            self.cache_layers['l1_memory']['access_times'],
            key=self.cache_layers['l1_memory']['access_times'].get
        )
        
        # Remove from L1
        category = self.cache_layers['l1_memory']['data'][lru_key]['category']
        del self.cache_layers['l1_memory']['data'][lru_key]
        del self.cache_layers['l1_memory']['access_times'][lru_key]
        
        self.cache_stats[category]['evictions'] += 1
    
    async def _get_from_l2(self, cache_key: str) -> Optional[Any]:
        """Get value from L2 persistent cache"""
        try:
            cache_file = self.cache_layers['l2_persistent']['persist_path'] / f"{cache_key}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                
                # Check TTL
                if time.time() - entry['created_at'] <= entry['ttl']:
                    return entry['value']
                else:
                    # Expired, remove file
                    cache_file.unlink()
            
            return None
        except Exception as e:
            logger.warning(f"Error reading from L2 cache: {e}")
            return None
    
    async def _set_in_l2(self, cache_key: str, entry: Dict[str, Any]) -> bool:
        """Set value in L2 persistent cache"""
        try:
            cache_file = self.cache_layers['l2_persistent']['persist_path'] / f"{cache_key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
            return True
        except Exception as e:
            logger.warning(f"Error writing to L2 cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        stats = dict(self.cache_stats)
        
        # Add cache sizes
        stats['cache_sizes'] = {
            'l1_memory': len(self.cache_layers['l1_memory']['data']),
            'l2_persistent': len(list(self.cache_layers['l2_persistent']['persist_path'].glob('*.pkl')))
        }
        
        # Calculate hit rates
        for category in stats:
            if category != 'cache_sizes' and stats[category]['hits'] + stats[category]['misses'] > 0:
                total_requests = stats[category]['hits'] + stats[category]['misses']
                stats[category]['hit_rate'] = stats[category]['hits'] / total_requests
        
        return stats


class DistributedProcessingEngine:
    """Distributed processing engine for computational-heavy operations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_workers = self.config.get('max_workers', 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}
        
    async def process_distributed(self, operation_type: str, tasks: List[Dict[str, Any]], 
                                 execution_mode: str = 'thread') -> List[Any]:
        """Process tasks in parallel using distributed execution"""
        
        if execution_mode == 'thread':
            executor = self.thread_pool
        elif execution_mode == 'process':
            executor = self.process_pool
        else:
            raise ValueError(f"Unknown execution mode: {execution_mode}")
        
        # Create futures for all tasks
        futures = []
        for i, task in enumerate(tasks):
            future = asyncio.get_event_loop().run_in_executor(
                executor, 
                self._execute_task, 
                operation_type, 
                task, 
                i
            )
            futures.append(future)
        
        # Wait for all tasks to complete
        try:
            results = await asyncio.gather(*futures, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed: {result}")
                    processed_results.append({'error': str(result), 'task_id': i})
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Distributed processing failed: {e}")
            raise
    
    def _execute_task(self, operation_type: str, task: Dict[str, Any], task_id: int) -> Any:
        """Execute individual task (runs in separate thread/process)"""
        try:
            if operation_type == 'financial_analysis':
                return self._execute_financial_analysis(task)
            elif operation_type == 'reasoning_operation':
                return self._execute_reasoning_operation(task)
            elif operation_type == 'pattern_recognition':
                return self._execute_pattern_recognition(task)
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")
                
        except Exception as e:
            logger.error(f"Task {task_id} execution failed: {e}")
            raise
    
    def _execute_financial_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute financial analysis task"""
        # Simulate computational work
        import time
        time.sleep(0.1)  # Simulate processing time
        
        return {
            'task_type': 'financial_analysis',
            'result': f"Analysis complete for {task.get('data_type', 'unknown')}",
            'confidence': 0.85,
            'processing_time': 0.1
        }
    
    def _execute_reasoning_operation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reasoning operation task"""
        # Simulate reasoning computation
        import time
        time.sleep(0.2)  # Simulate processing time
        
        return {
            'task_type': 'reasoning_operation',
            'conclusion': f"Reasoning complete for {task.get('premise', 'unknown')}",
            'confidence': 0.75,
            'processing_time': 0.2
        }
    
    def _execute_pattern_recognition(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pattern recognition task"""
        # Simulate pattern analysis
        import time
        time.sleep(0.15)  # Simulate processing time
        
        return {
            'task_type': 'pattern_recognition',
            'patterns_found': ['pattern_1', 'pattern_2'],
            'confidence': 0.90,
            'processing_time': 0.15
        }
    
    async def get_system_load(self) -> Dict[str, Any]:
        """Get current system load metrics"""
        return {
            'thread_pool_active': self.thread_pool._threads.__len__() if hasattr(self.thread_pool, '_threads') else 0,
            'process_pool_active': len(self.process_pool._processes) if hasattr(self.process_pool, '_processes') else 0,
            'queue_size': self.task_queue.qsize(),
            'active_tasks': len(self.active_tasks)
        }
    
    async def shutdown(self):
        """Gracefully shutdown the processing engine"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)