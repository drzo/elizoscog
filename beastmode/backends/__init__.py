"""Backend components for hardware acceleration"""

from .gpu_backend import GPUBackend
from .cpu_backend import CPUBackend

__all__ = [
    'GPUBackend',
    'CPUBackend',
]
