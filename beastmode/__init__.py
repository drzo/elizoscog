"""
BeastMode Inference Engine
==========================

The most powerful AI inference accelerator on Earth.

Features:
- Multi-modal inference (text, vision, audio, multimodal)
- GPU/TPU acceleration with dynamic batching
- Advanced optimization (quantization, pruning, distillation)
- Distributed inference with model parallelism
- Intelligent caching and prefetching
- Real-time performance monitoring
- Adaptive optimization based on workload
"""

__version__ = "1.0.0"
__author__ = "BeastMode Team"

from .core.inference_engine import BeastModeEngine
from .core.model_loader import ModelLoader
from .optimizers.quantization import QuantizationOptimizer
from .optimizers.pruning import PruningOptimizer
from .backends.gpu_backend import GPUBackend
from .benchmarks.performance_test import PerformanceBenchmark

__all__ = [
    'BeastModeEngine',
    'ModelLoader',
    'QuantizationOptimizer',
    'PruningOptimizer',
    'GPUBackend',
    'PerformanceBenchmark',
]
