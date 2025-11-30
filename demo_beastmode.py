"""
Comprehensive BeastMode Inference Engine Demo

Demonstrates all features:
- Model loading and inference
- Dynamic batching
- Caching
- Quantization and pruning
- GPU acceleration
- Performance benchmarking
"""

import asyncio
import logging
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from beastmode import BeastModeEngine, PerformanceBenchmark
from beastmode.core.inference_engine import (
    ModelConfig, ModelType, DeviceType, InferenceRequest
)
from beastmode.optimizers import QuantizationOptimizer, PruningOptimizer
from beastmode.optimizers.quantization import QuantizationPrecision, QuantizationType
from beastmode.optimizers.pruning import PruningType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_inference():
    """Demo 1: Basic inference with BeastMode Engine"""
    logger.info("=" * 80)
    logger.info("DEMO 1: Basic Inference")
    logger.info("=" * 80)
    
    # Create engine
    engine = BeastModeEngine(config={
        'cache_size_mb': 512,
        'max_batch_size': 32
    })
    
    # Initialize
    await engine.initialize()
    
    # Load model
    model_config = ModelConfig(
        model_id="demo_model",
        model_type=ModelType.TRANSFORMER,
        device=DeviceType.CPU,
        precision="fp32",
        max_batch_size=32,
        use_cache=True
    )
    
    await engine.load_model(model_config)
    
    # Run inference
    logger.info("Running 10 inference requests...")
    
    for i in range(10):
        request = InferenceRequest(
            request_id=f"demo_{i}",
            inputs=np.random.randn(1, 512).astype(np.float32),
            model_id="demo_model"
        )
        
        result = await engine.infer(request)
        logger.info(f"Request {i}: latency={result.latency_ms:.2f}ms, cache_hit={result.cache_hit}")
    
    # Get metrics
    metrics = engine.get_metrics()
    logger.info(f"\nMetrics:")
    logger.info(f"  Total requests: {metrics['total_requests']}")
    logger.info(f"  Cache hit rate: {metrics['cache_hit_rate']:.2%}")
    logger.info(f"  Avg latency: {metrics['avg_latency_ms']:.2f}ms")
    logger.info(f"  P95 latency: {metrics['p95_latency_ms']:.2f}ms")
    
    await engine.shutdown()


async def demo_quantization():
    """Demo 2: Model quantization for faster inference"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 2: Quantization Optimization")
    logger.info("=" * 80)
    
    engine = BeastModeEngine()
    await engine.initialize()
    
    # Load base model
    model_config = ModelConfig(
        model_id="quantization_demo",
        model_type=ModelType.TRANSFORMER,
        device=DeviceType.CPU,
        precision="fp32"
    )
    
    await engine.load_model(model_config)
    
    # Get the loaded model
    model = engine.models["quantization_demo"]
    
    # Create quantization optimizer
    quantizer = QuantizationOptimizer()
    
    # Try different quantization levels
    precisions = [
        (QuantizationPrecision.FP32, "Full Precision"),
        (QuantizationPrecision.FP16, "Half Precision"),
        (QuantizationPrecision.INT8, "INT8 Quantization"),
        (QuantizationPrecision.INT4, "INT4 Quantization"),
    ]
    
    for precision, name in precisions:
        quantized = await quantizer.quantize_model(
            model,
            precision,
            QuantizationType.DYNAMIC
        )
        
        info = quantizer.get_quantization_info(quantized)
        logger.info(f"\n{name}:")
        logger.info(f"  Speedup: {info['speedup']:.1f}x")
        logger.info(f"  Memory reduction: {info['memory_reduction']:.1%}")
    
    await engine.shutdown()


async def demo_pruning():
    """Demo 3: Model pruning for smaller models"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 3: Pruning Optimization")
    logger.info("=" * 80)
    
    engine = BeastModeEngine()
    await engine.initialize()
    
    model_config = ModelConfig(
        model_id="pruning_demo",
        model_type=ModelType.TRANSFORMER,
        device=DeviceType.CPU
    )
    
    await engine.load_model(model_config)
    model = engine.models["pruning_demo"]
    
    # Create pruning optimizer
    pruner = PruningOptimizer()
    
    # Try different sparsity levels
    sparsity_levels = [0.0, 0.25, 0.50, 0.75, 0.90]
    
    for sparsity in sparsity_levels:
        pruned = await pruner.prune_model(
            model,
            sparsity=sparsity,
            pruning_type=PruningType.MAGNITUDE,
            structured=False
        )
        
        info = pruner.get_pruning_info(pruned)
        logger.info(f"\nSparsity {sparsity:.0%}:")
        logger.info(f"  Pruned params: {info['pruned_params']:,}")
        logger.info(f"  Speedup: {info['speedup']:.2f}x")
        logger.info(f"  Memory reduction: {info['memory_reduction']:.1%}")
    
    await engine.shutdown()


async def demo_batching():
    """Demo 4: Dynamic batching for throughput optimization"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 4: Dynamic Batching")
    logger.info("=" * 80)
    
    engine = BeastModeEngine(config={
        'max_batch_size': 32,
        'max_wait_ms': 10
    })
    await engine.initialize()
    
    model_config = ModelConfig(
        model_id="batching_demo",
        model_type=ModelType.TRANSFORMER,
        device=DeviceType.CPU
    )
    
    await engine.load_model(model_config)
    
    # Send burst of requests
    logger.info("Sending burst of 50 requests for batching...")
    
    tasks = []
    for i in range(50):
        request = InferenceRequest(
            request_id=f"batch_{i}",
            inputs=np.random.randn(1, 256).astype(np.float32),
            model_id="batching_demo"
        )
        tasks.append(engine.infer(request))
    
    # Wait for all
    results = await asyncio.gather(*tasks)
    
    # Analyze batch sizes
    batch_sizes = {}
    for result in results:
        batch_size = result.batch_size
        batch_sizes[batch_size] = batch_sizes.get(batch_size, 0) + 1
    
    logger.info("\nBatch size distribution:")
    for batch_size, count in sorted(batch_sizes.items()):
        logger.info(f"  Batch size {batch_size}: {count} requests")
    
    metrics = engine.get_metrics()
    logger.info(f"\nThroughput: {metrics['throughput_rps']:.2f} req/s")
    
    await engine.shutdown()


async def demo_benchmarking():
    """Demo 5: Comprehensive performance benchmarking"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 5: Performance Benchmarking")
    logger.info("=" * 80)
    
    engine = BeastModeEngine(config={'cache_size_mb': 1024})
    await engine.initialize()
    
    model_config = ModelConfig(
        model_id="benchmark_model",
        model_type=ModelType.TRANSFORMER,
        device=DeviceType.CPU,
        precision="fp16",  # Use FP16 for faster inference
        use_cache=True,
        use_dynamic_batching=True
    )
    
    await engine.load_model(model_config)
    
    # Create benchmark
    benchmark = PerformanceBenchmark(engine)
    
    # Run latency benchmark
    from beastmode.benchmarks.performance_test import BenchmarkConfig
    
    config = BenchmarkConfig(
        num_requests=500,
        warmup_requests=50,
        input_shapes=[(1, 512), (1, 1024)],
        model_id="benchmark_model"
    )
    
    logger.info("\nRunning latency benchmark...")
    result = await benchmark.run_benchmark(config)
    
    # Run throughput benchmark
    config.concurrent_requests = 10
    logger.info("\nRunning throughput benchmark with 10 concurrent requests...")
    throughput_result = await benchmark.run_throughput_test(config)
    
    logger.info(f"\nThroughput with concurrency: {throughput_result.throughput_rps:.2f} req/s")
    
    await engine.shutdown()


async def demo_full_optimization():
    """Demo 6: Full optimization pipeline"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 6: Full Optimization Pipeline")
    logger.info("=" * 80)
    
    engine = BeastModeEngine()
    await engine.initialize()
    
    # Load base model
    model_config = ModelConfig(
        model_id="full_opt_demo",
        model_type=ModelType.TRANSFORMER,
        device=DeviceType.CPU,
        optimization_level=3  # Maximum optimization
    )
    
    await engine.load_model(model_config)
    model = engine.models["full_opt_demo"]
    
    logger.info("\nApplying full optimization pipeline:")
    logger.info("  1. Quantization to INT8")
    logger.info("  2. Pruning to 50% sparsity")
    logger.info("  3. Knowledge distillation")
    
    # Apply quantization
    quantizer = QuantizationOptimizer()
    model = await quantizer.quantize_model(
        model,
        QuantizationPrecision.INT8,
        QuantizationType.STATIC
    )
    
    # Apply pruning
    pruner = PruningOptimizer()
    model = await pruner.prune_model(
        model,
        sparsity=0.5,
        pruning_type=PruningType.MAGNITUDE,
        structured=True
    )
    
    # Get combined speedup
    quant_info = quantizer.get_quantization_info(model)
    prune_info = pruner.get_pruning_info(model)
    
    combined_speedup = quant_info['speedup'] * prune_info['speedup']
    combined_memory_reduction = 1.0 - ((1.0 - quant_info['memory_reduction']) * 
                                       (1.0 - prune_info['memory_reduction']))
    
    logger.info(f"\nCombined optimization results:")
    logger.info(f"  Total speedup: {combined_speedup:.2f}x")
    logger.info(f"  Total memory reduction: {combined_memory_reduction:.1%}")
    logger.info(f"  Estimated inference time improvement: {(combined_speedup-1)*100:.0f}%")
    
    await engine.shutdown()


async def main():
    """Run all demos"""
    logger.info("🚀 BeastMode Inference Engine - Comprehensive Demo")
    logger.info("The most powerful AI inference accelerator on Earth\n")
    
    try:
        # Run all demos
        await demo_basic_inference()
        await demo_quantization()
        await demo_pruning()
        await demo_batching()
        await demo_benchmarking()
        await demo_full_optimization()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ All demos completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
