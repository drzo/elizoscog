#!/usr/bin/env python3
"""
Custom Kernel Compilation Pipeline
Phase 3 Implementation: Dynamic GGML Kernel Compilation and Optimization

Provides automated kernel compilation, optimization, and runtime loading
for symbolic operations across multiple hardware architectures.
"""

import asyncio
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import tempfile
import subprocess
import os
import platform
import hashlib
from pathlib import Path

from .ggml_symbolic_kernels import (
    KernelArchitecture, SymbolicOperation, KernelCompilationConfig
)

logger = logging.getLogger(__name__)


class OptimizationPass(Enum):
    """Available optimization passes for kernel compilation"""
    DEAD_CODE_ELIMINATION = "dead_code_elimination"
    CONSTANT_FOLDING = "constant_folding"
    LOOP_UNROLLING = "loop_unrolling"
    VECTORIZATION = "vectorization"
    MEMORY_COALESCING = "memory_coalescing"
    INSTRUCTION_SCHEDULING = "instruction_scheduling"
    REGISTER_ALLOCATION = "register_allocation"
    SYMBOLIC_SIMPLIFICATION = "symbolic_simplification"


class CompilerBackend(Enum):
    """Supported compiler backends"""
    GCC = "gcc"
    CLANG = "clang"
    NVCC = "nvcc"
    ICC = "icc"
    CUSTOM = "custom"


@dataclass
class CompilationResult:
    """Result of kernel compilation"""
    success: bool
    kernel_id: str
    binary_path: Optional[str] = None
    compile_time_seconds: float = 0.0
    binary_size_bytes: int = 0
    optimization_passes: List[OptimizationPass] = field(default_factory=list)
    performance_estimate: Dict[str, float] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KernelTemplate:
    """Template for generating kernel code"""
    template_id: str
    operation: SymbolicOperation
    architecture: KernelArchitecture
    code_template: str
    parameter_types: Dict[str, str]
    includes: List[str] = field(default_factory=list)
    optimizations: List[OptimizationPass] = field(default_factory=list)


class CodeGenerator:
    """Generates optimized kernel code for different architectures"""
    
    def __init__(self):
        self.templates: Dict[str, KernelTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize kernel code templates"""
        
        # CPU x86_64 symbolic addition template
        cpu_add_template = KernelTemplate(
            template_id="cpu_symbol_add",
            operation=SymbolicOperation.SYMBOL_ADD,
            architecture=KernelArchitecture.CPU_X86_64,
            code_template="""
#include <immintrin.h>
#include <omp.h>
#include <math.h>

extern "C" {
    void symbolic_add_kernel(
        const float* input1, const float* input2, float* output,
        const int size, const int threads
    ) {
        #pragma omp parallel for num_threads(threads) if(size > 1000)
        for (int i = 0; i < size; i += 8) {
            if (i + 8 <= size) {
                // Vectorized addition using AVX2
                __m256 a = _mm256_load_ps(&input1[i]);
                __m256 b = _mm256_load_ps(&input2[i]);
                __m256 result = _mm256_add_ps(a, b);
                _mm256_store_ps(&output[i], result);
            } else {
                // Handle remaining elements
                for (int j = i; j < size; j++) {
                    output[j] = input1[j] + input2[j];
                }
            }
        }
    }
    
    void symbolic_metadata_merge(
        const char** symbols1, const char** symbols2, char** output_symbols,
        const int symbol_count
    ) {
        // Merge symbolic metadata
        for (int i = 0; i < symbol_count; i++) {
            // Simple concatenation for now
            sprintf(output_symbols[i], "%s+%s", symbols1[i], symbols2[i]);
        }
    }
}
            """,
            parameter_types={
                "input1": "const float*",
                "input2": "const float*", 
                "output": "float*",
                "size": "int",
                "threads": "int"
            },
            includes=["immintrin.h", "omp.h", "math.h"],
            optimizations=[
                OptimizationPass.VECTORIZATION,
                OptimizationPass.LOOP_UNROLLING,
                OptimizationPass.INSTRUCTION_SCHEDULING
            ]
        )
        self.templates["cpu_symbol_add"] = cpu_add_template
        
        # CPU pattern recognition template
        cpu_pattern_template = KernelTemplate(
            template_id="cpu_pattern_recognition",
            operation=SymbolicOperation.PATTERN_RECOGNITION,
            architecture=KernelArchitecture.CPU_X86_64,
            code_template="""
#include <math.h>
#include <string.h>
#include <fftw3.h>

extern "C" {
    void pattern_recognition_kernel(
        const float* input, float* patterns, float* features,
        const int size, const float threshold
    ) {
        // Statistical features
        float mean = 0.0f, variance = 0.0f;
        for (int i = 0; i < size; i++) {
            mean += input[i];
        }
        mean /= size;
        
        for (int i = 0; i < size; i++) {
            float diff = input[i] - mean;
            variance += diff * diff;
        }
        variance /= size;
        
        features[0] = mean;
        features[1] = sqrt(variance);
        features[2] = variance;
        
        // Peak detection
        int peak_count = 0;
        for (int i = 1; i < size - 1; i++) {
            if (input[i] > input[i-1] && input[i] > input[i+1] && input[i] > threshold) {
                peak_count++;
            }
        }
        features[3] = (float)peak_count;
        
        // Autocorrelation for periodicity
        if (size >= 16) {
            float max_autocorr = 0.0f;
            int best_lag = 0;
            
            for (int lag = 1; lag < min(size/2, 32); lag++) {
                float autocorr = 0.0f;
                for (int i = 0; i < size - lag; i++) {
                    autocorr += input[i] * input[i + lag];
                }
                autocorr /= (size - lag);
                
                if (autocorr > max_autocorr) {
                    max_autocorr = autocorr;
                    best_lag = lag;
                }
            }
            
            features[4] = max_autocorr;
            features[5] = (float)best_lag;
        }
        
        // Symmetry detection
        float symmetry = 0.0f;
        for (int i = 0; i < size/2; i++) {
            symmetry += fabsf(input[i] - input[size - 1 - i]);
        }
        symmetry = 1.0f - (symmetry / (size/2));
        features[6] = symmetry;
        
        // Store pattern indicators
        patterns[0] = (peak_count > 2) ? 1.0f : 0.0f;  // Has peaks
        patterns[1] = (max_autocorr > 0.5f) ? 1.0f : 0.0f;  // Is periodic
        patterns[2] = (symmetry > 0.8f) ? 1.0f : 0.0f;  // Is symmetric
        patterns[3] = (variance < 0.1f) ? 1.0f : 0.0f;  // Is constant-like
    }
}
            """,
            parameter_types={
                "input": "const float*",
                "patterns": "float*",
                "features": "float*",
                "size": "int",
                "threshold": "float"
            },
            includes=["math.h", "string.h"],
            optimizations=[
                OptimizationPass.LOOP_UNROLLING,
                OptimizationPass.INSTRUCTION_SCHEDULING,
                OptimizationPass.CONSTANT_FOLDING
            ]
        )
        self.templates["cpu_pattern_recognition"] = cpu_pattern_template
        
        # GPU CUDA symbolic operations template
        gpu_template = KernelTemplate(
            template_id="gpu_symbolic_ops",
            operation=SymbolicOperation.SYMBOL_ADD,
            architecture=KernelArchitecture.GPU_CUDA,
            code_template="""
#include <cuda_runtime.h>
#include <cublas_v2.h>

__global__ void symbolic_add_cuda_kernel(
    const float* input1, const float* input2, float* output, int size
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    
    for (int i = idx; i < size; i += stride) {
        output[i] = input1[i] + input2[i];
    }
}

__global__ void symbolic_multiply_cuda_kernel(
    const float* input1, const float* input2, float* output, int size
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    
    for (int i = idx; i < size; i += stride) {
        output[i] = input1[i] * input2[i];
    }
}

__global__ void pattern_recognition_cuda_kernel(
    const float* input, float* features, int size, float threshold
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx == 0) {
        // Compute basic statistics
        float sum = 0.0f;
        for (int i = 0; i < size; i++) {
            sum += input[i];
        }
        features[0] = sum / size;  // mean
        
        float variance = 0.0f;
        for (int i = 0; i < size; i++) {
            float diff = input[i] - features[0];
            variance += diff * diff;
        }
        features[1] = variance / size;
        
        // Peak counting
        int peaks = 0;
        for (int i = 1; i < size - 1; i++) {
            if (input[i] > input[i-1] && input[i] > input[i+1] && input[i] > threshold) {
                peaks++;
            }
        }
        features[2] = (float)peaks;
    }
}

extern "C" {
    int launch_symbolic_add_cuda(
        const float* d_input1, const float* d_input2, float* d_output,
        int size, cudaStream_t stream
    ) {
        int blockSize = 256;
        int numBlocks = (size + blockSize - 1) / blockSize;
        
        symbolic_add_cuda_kernel<<<numBlocks, blockSize, 0, stream>>>(
            d_input1, d_input2, d_output, size
        );
        
        return cudaGetLastError() == cudaSuccess ? 0 : -1;
    }
    
    int launch_pattern_recognition_cuda(
        const float* d_input, float* d_features,
        int size, float threshold, cudaStream_t stream
    ) {
        pattern_recognition_cuda_kernel<<<1, 1, 0, stream>>>(
            d_input, d_features, size, threshold
        );
        
        return cudaGetLastError() == cudaSuccess ? 0 : -1;
    }
}
            """,
            parameter_types={
                "d_input1": "const float*",
                "d_input2": "const float*",
                "d_output": "float*",
                "size": "int",
                "stream": "cudaStream_t"
            },
            includes=["cuda_runtime.h", "cublas_v2.h"],
            optimizations=[
                OptimizationPass.MEMORY_COALESCING,
                OptimizationPass.REGISTER_ALLOCATION,
                OptimizationPass.INSTRUCTION_SCHEDULING
            ]
        )
        self.templates["gpu_symbolic_ops"] = gpu_template
        
        logger.info(f"Initialized {len(self.templates)} kernel templates")
    
    def generate_kernel_code(self, operation: SymbolicOperation,
                           architecture: KernelArchitecture,
                           config: KernelCompilationConfig) -> Optional[str]:
        """Generate optimized kernel code for operation and architecture"""
        
        # Find matching template
        template = None
        for temp in self.templates.values():
            if temp.operation == operation and temp.architecture == architecture:
                template = temp
                break
        
        if not template:
            logger.warning(f"No template found for {operation} on {architecture}")
            return None
        
        # Apply optimizations to template
        optimized_code = template.code_template
        
        # Apply optimization passes
        if config.vectorization and OptimizationPass.VECTORIZATION in template.optimizations:
            optimized_code = self._apply_vectorization_pass(optimized_code, config)
        
        if config.parallel_threads > 1:
            optimized_code = self._apply_parallelization_pass(optimized_code, config)
        
        # Add compiler directives based on optimization level
        if config.optimization_level == "O3":
            optimized_code = f"#pragma GCC optimize(\"O3\")\n{optimized_code}"
        elif config.optimization_level == "O2":
            optimized_code = f"#pragma GCC optimize(\"O2\")\n{optimized_code}"
        
        return optimized_code
    
    def _apply_vectorization_pass(self, code: str, config: KernelCompilationConfig) -> str:
        """Apply vectorization optimizations"""
        # Add vectorization hints
        if "for (" in code and config.vectorization:
            code = code.replace("for (", "#pragma GCC ivdep\n        for (")
        return code
    
    def _apply_parallelization_pass(self, code: str, config: KernelCompilationConfig) -> str:
        """Apply parallelization optimizations"""
        # Add OpenMP pragmas for parallel loops
        if "#pragma omp parallel for" not in code and "for (" in code:
            if config.parallel_threads > 1:
                code = code.replace(
                    "for (int i = 0;", 
                    f"#pragma omp parallel for num_threads({config.parallel_threads})\n        for (int i = 0;"
                )
        return code


class KernelCompiler:
    """Compiles generated kernel code to optimized binaries"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ggml_kernels_")
        self.compiled_kernels: Dict[str, str] = {}  # kernel_id -> binary_path
        self.compilation_cache: Dict[str, CompilationResult] = {}
    
    async def compile_kernel(self, kernel_code: str, 
                           operation: SymbolicOperation,
                           architecture: KernelArchitecture,
                           config: KernelCompilationConfig) -> CompilationResult:
        """Compile kernel code to optimized binary"""
        start_time = time.perf_counter()
        
        # Generate unique kernel ID
        code_hash = hashlib.md5(kernel_code.encode()).hexdigest()[:8]
        kernel_id = f"{operation.name.lower()}_{architecture.value}_{code_hash}"
        
        # Check compilation cache
        cache_key = f"{kernel_id}_{config.optimization_level}"
        if cache_key in self.compilation_cache:
            logger.debug(f"Using cached compilation for {kernel_id}")
            return self.compilation_cache[cache_key]
        
        result = CompilationResult(
            success=False,
            kernel_id=kernel_id,
            compile_time_seconds=0.0
        )
        
        try:
            # Write source code to temporary file
            source_file = os.path.join(self.temp_dir, f"{kernel_id}.cpp")
            binary_file = os.path.join(self.temp_dir, f"{kernel_id}.so")
            
            with open(source_file, 'w') as f:
                f.write(kernel_code)
            
            # Select compiler and flags based on architecture
            if architecture in [KernelArchitecture.CPU_X86_64, KernelArchitecture.CPU_ARM64]:
                success = await self._compile_cpu_kernel(
                    source_file, binary_file, config
                )
            elif architecture == KernelArchitecture.GPU_CUDA:
                success = await self._compile_cuda_kernel(
                    source_file, binary_file, config
                )
            elif architecture == KernelArchitecture.GPU_OPENCL:
                success = await self._compile_opencl_kernel(
                    source_file, binary_file, config
                )
            elif architecture in [KernelArchitecture.TPU_V4, KernelArchitecture.TPU_V5]:
                success = await self._compile_tpu_kernel(
                    source_file, binary_file, config, architecture
                )
            else:
                logger.warning(f"Architecture {architecture} not fully supported, using CPU fallback")
                success = await self._compile_cpu_kernel(
                    source_file, binary_file, config
                )
            
            if success and os.path.exists(binary_file):
                result.success = True
                result.binary_path = binary_file
                result.binary_size_bytes = os.path.getsize(binary_file)
                self.compiled_kernels[kernel_id] = binary_file
                
                # Estimate performance
                result.performance_estimate = await self._estimate_performance(
                    binary_file, operation, architecture
                )
            
        except Exception as e:
            result.error_messages.append(str(e))
            logger.error(f"Kernel compilation failed: {e}")
        
        result.compile_time_seconds = time.perf_counter() - start_time
        
        # Cache result
        self.compilation_cache[cache_key] = result
        
        logger.info(f"Compiled kernel {kernel_id}: success={result.success}, "
                   f"time={result.compile_time_seconds:.3f}s")
        
        return result
    
    async def _compile_cpu_kernel(self, source_file: str, binary_file: str,
                                config: KernelCompilationConfig) -> bool:
        """Compile CPU kernel using GCC/Clang"""
        try:
            # Determine available compiler
            compiler = "g++"
            if subprocess.run(["which", "clang++"], capture_output=True).returncode == 0:
                compiler = "clang++"
            
            # Build compilation command
            cmd = [
                compiler,
                "-shared",
                "-fPIC",
                f"-{config.optimization_level}",
                "-march=native",
                "-mtune=native",
                source_file,
                "-o", binary_file
            ]
            
            # Add architecture-specific flags
            if config.vectorization:
                cmd.extend(["-mavx2", "-mfma"])
            
            if config.parallel_threads > 0:
                cmd.extend(["-fopenmp"])
            
            if config.use_fast_math:
                cmd.extend(["-ffast-math", "-fno-math-errno"])
            
            if config.debug_symbols:
                cmd.extend(["-g", "-O0"])
            
            # Memory alignment
            if config.memory_alignment > 0:
                cmd.extend([f"-falign-functions={config.memory_alignment}"])
            
            # Run compilation
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.debug(f"CPU kernel compiled successfully: {binary_file}")
                return True
            else:
                logger.error(f"CPU compilation failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"CPU compilation error: {e}")
            return False
    
    async def _compile_cuda_kernel(self, source_file: str, binary_file: str,
                                 config: KernelCompilationConfig) -> bool:
        """Compile CUDA kernel using NVCC"""
        try:
            # Check if NVCC is available
            if subprocess.run(["which", "nvcc"], capture_output=True).returncode != 0:
                logger.warning("NVCC not found, skipping CUDA compilation")
                return False
            
            # Build NVCC command
            cmd = [
                "nvcc",
                "--shared",
                "--compiler-options", "-fPIC",
                f"-{config.optimization_level}",
                "--use_fast_math" if config.use_fast_math else "--ftz=false",
                "-arch=sm_70",  # Modern GPU architecture
                source_file,
                "-o", binary_file
            ]
            
            if config.debug_symbols:
                cmd.extend(["-g", "-G"])
            
            # Run compilation
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.debug(f"CUDA kernel compiled successfully: {binary_file}")
                return True
            else:
                logger.error(f"CUDA compilation failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"CUDA compilation error: {e}")
            return False
    
    async def _compile_opencl_kernel(self, source_file: str, binary_file: str,
                                   config: KernelCompilationConfig) -> bool:
        """Compile kernel for OpenCL GPU execution"""
        try:
            # Check if OpenCL compiler is available
            result = await asyncio.create_subprocess_exec(
                'which', 'clang', 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            if result.returncode != 0:
                logger.warning("OpenCL compiler not found, using fallback compilation")
                return await self._compile_cpu_kernel(source_file, binary_file, config)
            
            # OpenCL compilation command (simplified - would need proper OpenCL SDK)
            compile_cmd = [
                'clang',
                '-cl-std=CL2.0',
                '-O3',
                '-DOPENCL_KERNEL',
                '-c',
                source_file,
                '-o', binary_file
            ]
            
            if config.optimization_level == OptimizationLevel.AGGRESSIVE:
                compile_cmd.extend(['-cl-fast-relaxed-math', '-cl-unsafe-math-optimizations'])
            
            logger.info(f"🔧 Compiling OpenCL kernel: {' '.join(compile_cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *compile_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ OpenCL kernel compiled successfully")
                return True
            else:
                logger.error(f"OpenCL compilation failed: {stderr.decode()}")
                return False
            
        except Exception as e:
            logger.error(f"OpenCL compilation error: {e}")
            return False
    
    async def _compile_tpu_kernel(self, source_file: str, binary_file: str,
                                config: KernelCompilationConfig, 
                                architecture: KernelArchitecture) -> bool:
        """Compile kernel for TPU execution"""
        try:
            # Check if TPU compiler (XLA) is available
            result = await asyncio.create_subprocess_exec(
                'which', 'xla_compile', 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            
            if result.returncode != 0:
                logger.warning("TPU compiler not found, using CPU fallback")
                return await self._compile_cpu_kernel(source_file, binary_file, config)
            
            # TPU compilation parameters based on version
            tpu_params = []
            if architecture == KernelArchitecture.TPU_V4:
                tpu_params = ['--tpu_version=v4', '--matrix_unit_size=8192']
            elif architecture == KernelArchitecture.TPU_V5:
                tpu_params = ['--tpu_version=v5', '--matrix_unit_size=16384']
            
            # XLA compilation command (simplified)
            compile_cmd = [
                'xla_compile',
                '--target=tpu',
                '--optimization_level=3',
                *tpu_params,
                source_file,
                '--output', binary_file
            ]
            
            logger.info(f"🔧 Compiling TPU kernel: {' '.join(compile_cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *compile_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ TPU kernel compiled successfully for {architecture.value}")
                return True
            else:
                logger.error(f"TPU compilation failed: {stderr.decode()}")
                # Fallback to CPU compilation
                logger.info("Falling back to CPU compilation")
                return await self._compile_cpu_kernel(source_file, binary_file, config)
            
        except Exception as e:
            logger.error(f"TPU compilation error: {e}")
            # Fallback to CPU compilation
            return await self._compile_cpu_kernel(source_file, binary_file, config)
    
    async def _estimate_performance(self, binary_file: str,
                                  operation: SymbolicOperation,
                                  architecture: KernelArchitecture) -> Dict[str, float]:
        """Estimate performance characteristics of compiled kernel"""
        
        estimates = {
            'estimated_flops': 0.0,
            'estimated_memory_bandwidth': 0.0,
            'estimated_latency_ms': 0.0
        }
        
        try:
            # Get binary size for rough complexity estimate
            binary_size = os.path.getsize(binary_file)
            
            # Operation-specific estimates
            if operation == SymbolicOperation.SYMBOL_ADD:
                estimates['estimated_flops'] = 1.0  # One add per element
                estimates['estimated_memory_bandwidth'] = 3.0  # Read 2, write 1
                estimates['estimated_latency_ms'] = 0.1
            elif operation == SymbolicOperation.PATTERN_RECOGNITION:
                estimates['estimated_flops'] = 10.0  # Complex pattern analysis
                estimates['estimated_memory_bandwidth'] = 2.0  # Mostly reads
                estimates['estimated_latency_ms'] = 1.0
            
            # Architecture-specific adjustments
            if architecture == KernelArchitecture.GPU_CUDA:
                estimates['estimated_latency_ms'] *= 0.1  # GPU parallelism
                estimates['estimated_memory_bandwidth'] *= 10.0  # High bandwidth
            elif architecture in [KernelArchitecture.CPU_X86_64, KernelArchitecture.CPU_ARM64]:
                estimates['estimated_latency_ms'] *= 1.0  # Baseline
            
            # Binary size factor (larger = more complex, potentially slower)
            size_factor = min(2.0, binary_size / 10000.0)
            estimates['estimated_latency_ms'] *= size_factor
            
        except Exception as e:
            logger.warning(f"Performance estimation failed: {e}")
        
        return estimates
    
    def cleanup(self):
        """Clean up temporary compilation files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")


class KernelCompilationPipeline:
    """Complete pipeline for kernel compilation and optimization"""
    
    def __init__(self):
        self.code_generator = CodeGenerator()
        self.compiler = KernelCompiler()
        self.compilation_history: List[CompilationResult] = []
        self.performance_profiles: Dict[str, Dict[str, float]] = {}
    
    async def compile_optimized_kernel(self, operation: SymbolicOperation,
                                     architecture: KernelArchitecture,
                                     config: Optional[KernelCompilationConfig] = None) -> CompilationResult:
        """Complete pipeline: generate code, optimize, and compile"""
        
        if config is None:
            config = KernelCompilationConfig(architecture=architecture)
        
        logger.info(f"Starting compilation pipeline for {operation.name} on {architecture.value}")
        
        # Generate optimized kernel code
        kernel_code = self.code_generator.generate_kernel_code(operation, architecture, config)
        
        if not kernel_code:
            return CompilationResult(
                success=False,
                kernel_id=f"failed_{operation.name}_{architecture.value}",
                error_messages=["Failed to generate kernel code"]
            )
        
        # Compile kernel
        result = await self.compiler.compile_kernel(kernel_code, operation, architecture, config)
        
        # Store in history
        self.compilation_history.append(result)
        
        # Update performance profiles
        if result.success and result.performance_estimate:
            profile_key = f"{operation.name}_{architecture.value}"
            self.performance_profiles[profile_key] = result.performance_estimate
        
        logger.info(f"Compilation pipeline completed: {result.kernel_id}, success={result.success}")
        return result
    
    async def batch_compile_operations(self, operations: List[SymbolicOperation],
                                     architectures: List[KernelArchitecture],
                                     config: Optional[KernelCompilationConfig] = None) -> List[CompilationResult]:
        """Compile multiple operations for multiple architectures"""
        
        logger.info(f"Batch compiling {len(operations)} operations for {len(architectures)} architectures")
        
        tasks = []
        for operation in operations:
            for architecture in architectures:
                arch_config = config or KernelCompilationConfig(architecture=architecture)
                task = self.compile_optimized_kernel(operation, architecture, arch_config)
                tasks.append(task)
        
        # Execute all compilations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and collect valid results
        valid_results = []
        for result in results:
            if isinstance(result, CompilationResult):
                valid_results.append(result)
            else:
                logger.error(f"Compilation task failed: {result}")
        
        successful_compilations = sum(1 for r in valid_results if r.success)
        logger.info(f"Batch compilation completed: {successful_compilations}/{len(valid_results)} successful")
        
        return valid_results
    
    def get_compilation_report(self) -> Dict[str, Any]:
        """Get comprehensive compilation report"""
        
        total_compilations = len(self.compilation_history)
        successful_compilations = sum(1 for r in self.compilation_history if r.success)
        
        # Calculate average compile times
        compile_times = [r.compile_time_seconds for r in self.compilation_history if r.success]
        avg_compile_time = np.mean(compile_times) if compile_times else 0.0
        
        # Binary size statistics
        binary_sizes = [r.binary_size_bytes for r in self.compilation_history if r.success and r.binary_size_bytes > 0]
        avg_binary_size = np.mean(binary_sizes) if binary_sizes else 0.0
        
        # Performance estimates
        estimated_latencies = []
        for result in self.compilation_history:
            if result.success and result.performance_estimate:
                if 'estimated_latency_ms' in result.performance_estimate:
                    estimated_latencies.append(result.performance_estimate['estimated_latency_ms'])
        
        avg_estimated_latency = np.mean(estimated_latencies) if estimated_latencies else 0.0
        
        return {
            'total_compilations': total_compilations,
            'successful_compilations': successful_compilations,
            'success_rate': successful_compilations / max(1, total_compilations),
            'avg_compile_time_seconds': avg_compile_time,
            'avg_binary_size_bytes': avg_binary_size,
            'avg_estimated_latency_ms': avg_estimated_latency,
            'performance_profiles': dict(self.performance_profiles),
            'compilation_history': [
                {
                    'kernel_id': r.kernel_id,
                    'success': r.success,
                    'compile_time': r.compile_time_seconds,
                    'binary_size': r.binary_size_bytes,
                    'operation': r.metadata.get('operation', 'unknown')
                }
                for r in self.compilation_history[-10:]  # Last 10 compilations
            ]
        }
    
    async def benchmark_compiled_kernels(self) -> Dict[str, Dict[str, float]]:
        """Benchmark all successfully compiled kernels"""
        
        benchmark_results = {}
        
        for result in self.compilation_history:
            if result.success and result.binary_path and os.path.exists(result.binary_path):
                # Simple benchmark: measure binary load time as proxy
                start_time = time.perf_counter()
                
                try:
                    # Simulate kernel loading (actual loading would be architecture-specific)
                    with open(result.binary_path, 'rb') as f:
                        data = f.read(1024)  # Read first KB
                    
                    load_time = time.perf_counter() - start_time
                    
                    benchmark_results[result.kernel_id] = {
                        'load_time_ms': load_time * 1000,
                        'binary_size_kb': result.binary_size_bytes / 1024,
                        'estimated_latency_ms': result.performance_estimate.get('estimated_latency_ms', 0.0)
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to benchmark kernel {result.kernel_id}: {e}")
        
        return benchmark_results
    
    def cleanup(self):
        """Clean up compilation artifacts"""
        self.compiler.cleanup()


# Global compilation pipeline instance
_compilation_pipeline = None

def get_compilation_pipeline() -> KernelCompilationPipeline:
    """Get global kernel compilation pipeline instance"""
    global _compilation_pipeline
    if _compilation_pipeline is None:
        _compilation_pipeline = KernelCompilationPipeline()
    return _compilation_pipeline


# Convenience functions
async def compile_kernel_for_operation(operation: SymbolicOperation,
                                     architecture: KernelArchitecture = KernelArchitecture.CPU_X86_64,
                                     optimization_level: str = "O2") -> CompilationResult:
    """Compile optimized kernel for specific operation"""
    pipeline = get_compilation_pipeline()
    config = KernelCompilationConfig(
        architecture=architecture,
        optimization_level=optimization_level,
        vectorization=True,
        use_fast_math=True
    )
    return await pipeline.compile_optimized_kernel(operation, architecture, config)


async def compile_all_symbolic_operations(architectures: Optional[List[KernelArchitecture]] = None) -> List[CompilationResult]:
    """Compile all symbolic operations for specified architectures"""
    if architectures is None:
        architectures = [KernelArchitecture.CPU_X86_64]
    
    operations = [
        SymbolicOperation.SYMBOL_ADD,
        SymbolicOperation.SYMBOL_MULTIPLY,
        SymbolicOperation.TENSOR_TO_SYMBOL,
        SymbolicOperation.SYMBOL_TO_TENSOR,
        SymbolicOperation.ATOM_EMBEDDING,
        SymbolicOperation.PATTERN_RECOGNITION
    ]
    
    pipeline = get_compilation_pipeline()
    return await pipeline.batch_compile_operations(operations, architectures)