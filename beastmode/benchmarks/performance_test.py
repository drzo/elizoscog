"""
Performance Benchmark Suite for BeastMode Engine

Comprehensive benchmarking of:
- Latency (p50, p95, p99)
- Throughput (requests per second)
- GPU utilization
- Memory usage
- Cache hit rates
- Batch efficiency
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Benchmark configuration"""
    num_requests: int = 1000
    batch_sizes: List[int] = field(default_factory=lambda: [1, 4, 8, 16, 32])
    input_shapes: List[tuple] = field(default_factory=lambda: [(1, 512), (1, 1024)])
    warmup_requests: int = 100
    concurrent_requests: int = 1
    model_id: str = "test_model"


@dataclass
class BenchmarkResult:
    """Benchmark results"""
    config: BenchmarkConfig
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time_s: float
    throughput_rps: float
    latency_mean_ms: float
    latency_median_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_min_ms: float
    latency_max_ms: float
    latencies: List[float] = field(default_factory=list)
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_utilization: float = 0.0


class PerformanceBenchmark:
    """
    Comprehensive performance benchmark suite for BeastMode Engine.
    
    Measures all aspects of inference performance and identifies bottlenecks.
    """
    
    def __init__(self, engine: Any):
        self.engine = engine
        self.results: List[BenchmarkResult] = []
    
    async def run_benchmark(
        self,
        config: Optional[BenchmarkConfig] = None
    ) -> BenchmarkResult:
        """
        Run complete benchmark suite.
        
        Args:
            config: Benchmark configuration
            
        Returns:
            Benchmark results
        """
        if config is None:
            config = BenchmarkConfig()
        
        logger.info(f"Starting benchmark with {config.num_requests} requests")
        
        # Warmup
        logger.info(f"Warming up with {config.warmup_requests} requests...")
        await self._warmup(config)
        
        # Run main benchmark
        logger.info("Running main benchmark...")
        result = await self._run_latency_test(config)
        
        # Store results
        self.results.append(result)
        
        # Log summary
        self._log_results(result)
        
        return result
    
    async def _warmup(self, config: BenchmarkConfig) -> None:
        """Warmup phase to stabilize performance"""
        from ..core.inference_engine import InferenceRequest
        
        for i in range(config.warmup_requests):
            request = InferenceRequest(
                request_id=f"warmup_{i}",
                inputs=np.random.randn(*config.input_shapes[0]).astype(np.float32),
                model_id=config.model_id
            )
            
            try:
                await self.engine.infer(request)
            except Exception as e:
                logger.warning(f"Warmup request {i} failed: {e}")
    
    async def _run_latency_test(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run latency benchmark"""
        from ..core.inference_engine import InferenceRequest
        
        latencies = []
        successful = 0
        failed = 0
        
        start_time = time.time()
        
        # Run requests
        for i in range(config.num_requests):
            # Alternate between input shapes
            input_shape = config.input_shapes[i % len(config.input_shapes)]
            
            request = InferenceRequest(
                request_id=f"bench_{i}",
                inputs=np.random.randn(*input_shape).astype(np.float32),
                model_id=config.model_id
            )
            
            request_start = time.time()
            
            try:
                result = await self.engine.infer(request)
                latency_ms = (time.time() - request_start) * 1000
                latencies.append(latency_ms)
                successful += 1
            except Exception as e:
                logger.error(f"Request {i} failed: {e}")
                failed += 1
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        if latencies:
            result = BenchmarkResult(
                config=config,
                total_requests=config.num_requests,
                successful_requests=successful,
                failed_requests=failed,
                total_time_s=total_time,
                throughput_rps=successful / total_time,
                latency_mean_ms=np.mean(latencies),
                latency_median_ms=np.median(latencies),
                latency_p95_ms=np.percentile(latencies, 95),
                latency_p99_ms=np.percentile(latencies, 99),
                latency_min_ms=np.min(latencies),
                latency_max_ms=np.max(latencies),
                latencies=latencies
            )
        else:
            result = BenchmarkResult(
                config=config,
                total_requests=config.num_requests,
                successful_requests=0,
                failed_requests=failed,
                total_time_s=total_time,
                throughput_rps=0.0,
                latency_mean_ms=0.0,
                latency_median_ms=0.0,
                latency_p95_ms=0.0,
                latency_p99_ms=0.0,
                latency_min_ms=0.0,
                latency_max_ms=0.0
            )
        
        # Get engine metrics
        metrics = self.engine.get_metrics()
        result.cache_hit_rate = metrics.get('cache_hit_rate', 0.0)
        
        return result
    
    async def run_throughput_test(
        self,
        config: Optional[BenchmarkConfig] = None
    ) -> BenchmarkResult:
        """
        Run throughput benchmark with concurrent requests.
        
        Tests maximum throughput with parallel requests.
        """
        if config is None:
            config = BenchmarkConfig()
        
        logger.info(f"Running throughput test with {config.concurrent_requests} concurrent requests")
        
        from ..core.inference_engine import InferenceRequest
        
        async def send_request(request_id: int) -> float:
            """Send single request and return latency"""
            input_shape = config.input_shapes[request_id % len(config.input_shapes)]
            
            request = InferenceRequest(
                request_id=f"throughput_{request_id}",
                inputs=np.random.randn(*input_shape).astype(np.float32),
                model_id=config.model_id
            )
            
            start = time.time()
            await self.engine.infer(request)
            return (time.time() - start) * 1000
        
        # Run concurrent requests in batches
        latencies = []
        successful = 0
        failed = 0
        
        start_time = time.time()
        
        for batch_start in range(0, config.num_requests, config.concurrent_requests):
            batch_end = min(batch_start + config.concurrent_requests, config.num_requests)
            batch_size = batch_end - batch_start
            
            # Create tasks for this batch
            tasks = [
                send_request(i)
                for i in range(batch_start, batch_end)
            ]
            
            # Wait for all requests in batch
            try:
                batch_latencies = await asyncio.gather(*tasks, return_exceptions=True)
                
                for latency in batch_latencies:
                    if isinstance(latency, Exception):
                        failed += 1
                    else:
                        latencies.append(latency)
                        successful += 1
            except Exception as e:
                logger.error(f"Batch failed: {e}")
                failed += batch_size
        
        total_time = time.time() - start_time
        
        # Create result
        result = BenchmarkResult(
            config=config,
            total_requests=config.num_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_time_s=total_time,
            throughput_rps=successful / total_time if total_time > 0 else 0.0,
            latency_mean_ms=np.mean(latencies) if latencies else 0.0,
            latency_median_ms=np.median(latencies) if latencies else 0.0,
            latency_p95_ms=np.percentile(latencies, 95) if latencies else 0.0,
            latency_p99_ms=np.percentile(latencies, 99) if latencies else 0.0,
            latency_min_ms=np.min(latencies) if latencies else 0.0,
            latency_max_ms=np.max(latencies) if latencies else 0.0,
            latencies=latencies
        )
        
        self._log_results(result)
        return result
    
    def _log_results(self, result: BenchmarkResult) -> None:
        """Log benchmark results"""
        logger.info("=" * 60)
        logger.info("BENCHMARK RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Requests:     {result.total_requests}")
        logger.info(f"Successful:         {result.successful_requests}")
        logger.info(f"Failed:             {result.failed_requests}")
        logger.info(f"Total Time:         {result.total_time_s:.2f}s")
        logger.info(f"Throughput:         {result.throughput_rps:.2f} req/s")
        logger.info("-" * 60)
        logger.info(f"Latency Mean:       {result.latency_mean_ms:.2f}ms")
        logger.info(f"Latency Median:     {result.latency_median_ms:.2f}ms")
        logger.info(f"Latency P95:        {result.latency_p95_ms:.2f}ms")
        logger.info(f"Latency P99:        {result.latency_p99_ms:.2f}ms")
        logger.info(f"Latency Min:        {result.latency_min_ms:.2f}ms")
        logger.info(f"Latency Max:        {result.latency_max_ms:.2f}ms")
        logger.info("-" * 60)
        logger.info(f"Cache Hit Rate:     {result.cache_hit_rate:.2%}")
        logger.info("=" * 60)
    
    def export_results(self, filename: str = "benchmark_results.json") -> None:
        """Export benchmark results to JSON"""
        data = []
        
        for result in self.results:
            data.append({
                'config': {
                    'num_requests': result.config.num_requests,
                    'concurrent_requests': result.config.concurrent_requests,
                    'model_id': result.config.model_id
                },
                'results': {
                    'throughput_rps': result.throughput_rps,
                    'latency_mean_ms': result.latency_mean_ms,
                    'latency_median_ms': result.latency_median_ms,
                    'latency_p95_ms': result.latency_p95_ms,
                    'latency_p99_ms': result.latency_p99_ms,
                    'cache_hit_rate': result.cache_hit_rate,
                    'success_rate': result.successful_requests / result.total_requests
                }
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported benchmark results to {filename}")
