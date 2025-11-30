"""
GPU Backend - Hardware acceleration for inference

Supports:
- CUDA (NVIDIA)
- ROCm (AMD)
- Metal (Apple)
- Vulkan (Cross-platform)
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """GPU device information"""
    device_id: int
    name: str
    memory_total_mb: int
    memory_available_mb: int
    compute_capability: Optional[str] = None
    backend: str = "unknown"


class GPUBackend:
    """
    GPU acceleration backend with support for multiple frameworks.
    
    Automatically detects available GPU hardware and selects optimal backend.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.devices: List[GPUInfo] = []
        self.backend = None
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize GPU backend"""
        if self.initialized:
            return
        
        # Detect available GPU backends
        backends = []
        
        # Try CUDA
        if await self._detect_cuda():
            backends.append('cuda')
        
        # Try ROCm
        if await self._detect_rocm():
            backends.append('rocm')
        
        # Try Metal
        if await self._detect_metal():
            backends.append('metal')
        
        # Fallback to CPU
        if not backends:
            logger.warning("No GPU detected, using CPU backend")
            self.backend = 'cpu'
        else:
            # Use first available backend
            self.backend = backends[0]
            logger.info(f"Using GPU backend: {self.backend}")
        
        # Enumerate devices
        await self._enumerate_devices()
        
        self.initialized = True
        logger.info(f"GPU backend initialized: {len(self.devices)} device(s)")
    
    async def _detect_cuda(self) -> bool:
        """Detect CUDA support"""
        try:
            import torch
            if torch.cuda.is_available():
                logger.info("CUDA detected")
                return True
        except ImportError:
            pass
        
        return False
    
    async def _detect_rocm(self) -> bool:
        """Detect ROCm support"""
        try:
            import torch
            if hasattr(torch, 'hip') and torch.hip.is_available():
                logger.info("ROCm detected")
                return True
        except (ImportError, AttributeError):
            pass
        
        return False
    
    async def _detect_metal(self) -> bool:
        """Detect Metal support"""
        try:
            import torch
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                logger.info("Metal detected")
                return True
        except (ImportError, AttributeError):
            pass
        
        return False
    
    async def _enumerate_devices(self) -> None:
        """Enumerate available GPU devices"""
        self.devices = []
        
        if self.backend == 'cuda':
            await self._enumerate_cuda_devices()
        elif self.backend == 'rocm':
            await self._enumerate_rocm_devices()
        elif self.backend == 'metal':
            await self._enumerate_metal_devices()
        else:
            # CPU fallback
            self.devices = [
                GPUInfo(
                    device_id=0,
                    name="CPU",
                    memory_total_mb=8192,
                    memory_available_mb=4096,
                    backend="cpu"
                )
            ]
    
    async def _enumerate_cuda_devices(self) -> None:
        """Enumerate CUDA devices"""
        try:
            import torch
            
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                
                device_info = GPUInfo(
                    device_id=i,
                    name=props.name,
                    memory_total_mb=props.total_memory // (1024 * 1024),
                    memory_available_mb=(props.total_memory - torch.cuda.memory_allocated(i)) // (1024 * 1024),
                    compute_capability=f"{props.major}.{props.minor}",
                    backend="cuda"
                )
                
                self.devices.append(device_info)
                logger.info(f"CUDA Device {i}: {device_info.name} ({device_info.memory_total_mb} MB)")
        
        except Exception as e:
            logger.error(f"Error enumerating CUDA devices: {e}")
    
    async def _enumerate_rocm_devices(self) -> None:
        """Enumerate ROCm devices"""
        # Mock implementation - real implementation would use ROCm API
        self.devices = [
            GPUInfo(
                device_id=0,
                name="AMD GPU",
                memory_total_mb=8192,
                memory_available_mb=8192,
                backend="rocm"
            )
        ]
        logger.info("Enumerated ROCm devices")
    
    async def _enumerate_metal_devices(self) -> None:
        """Enumerate Metal devices"""
        # Mock implementation - real implementation would use Metal API
        self.devices = [
            GPUInfo(
                device_id=0,
                name="Apple GPU",
                memory_total_mb=8192,
                memory_available_mb=8192,
                backend="metal"
            )
        ]
        logger.info("Enumerated Metal devices")
    
    def get_device(self, device_id: int = 0) -> Optional[GPUInfo]:
        """Get device by ID"""
        if 0 <= device_id < len(self.devices):
            return self.devices[device_id]
        return None
    
    def get_devices(self) -> List[GPUInfo]:
        """Get all available devices"""
        return self.devices.copy()
    
    def get_memory_info(self, device_id: int = 0) -> Dict[str, int]:
        """Get memory info for device"""
        device = self.get_device(device_id)
        if device:
            return {
                'total_mb': device.memory_total_mb,
                'available_mb': device.memory_available_mb,
                'used_mb': device.memory_total_mb - device.memory_available_mb
            }
        return {}
    
    async def synchronize(self, device_id: int = 0) -> None:
        """Synchronize device"""
        if self.backend == 'cuda':
            try:
                import torch
                torch.cuda.synchronize(device_id)
            except Exception as e:
                logger.error(f"Error synchronizing CUDA device: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown GPU backend"""
        logger.info("Shutting down GPU backend")
        
        # Clear device cache
        if self.backend == 'cuda':
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:
                pass
        
        self.devices.clear()
        self.initialized = False
