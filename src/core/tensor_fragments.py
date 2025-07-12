#!/usr/bin/env python3
"""
Tensor Fragment Architecture with Prime Factorization
Phase 1: Core tensor processing for cognitive hypergraph integration

Implements 5-dimensional tensor shapes: [modality, depth, context, salience, autonomy_index]
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from math import gcd
from functools import reduce

logger = logging.getLogger(__name__)


class Modality(Enum):
    """Tensor modality types for cognitive processing"""
    FINANCIAL = 0
    COGNITIVE = 1  
    TEMPORAL = 2
    SPATIAL = 3
    LINGUISTIC = 4
    LOGICAL = 5
    AGENT = 6
    TRANSACTION = 7


@dataclass
class TensorShape:
    """5-dimensional tensor shape specification"""
    modality: int  # 0-7, maps to Modality enum
    depth: int     # Reasoning depth (0-15)
    context: int   # Context window size (0-31)  
    salience: int  # Importance/attention weight (0-15)
    autonomy_index: int  # Agent autonomy level (0-7)
    
    def __post_init__(self):
        """Validate tensor shape dimensions"""
        if not (0 <= self.modality <= 7):
            raise ValueError(f"Modality must be 0-7, got {self.modality}")
        if not (1 <= self.depth <= 15):  # Ensure minimum 1 for all dimensions
            raise ValueError(f"Depth must be 1-15, got {self.depth}")
        if not (1 <= self.context <= 31):
            raise ValueError(f"Context must be 1-31, got {self.context}")
        if not (1 <= self.salience <= 15):
            raise ValueError(f"Salience must be 1-15, got {self.salience}")
        if not (1 <= self.autonomy_index <= 7):
            raise ValueError(f"Autonomy index must be 1-7, got {self.autonomy_index}")
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array representation"""
        return np.array([self.modality, self.depth, self.context, 
                        self.salience, self.autonomy_index], dtype=np.int32)
    
    def total_size(self) -> int:
        """Calculate total tensor size"""
        return self.modality * self.depth * self.context * self.salience * self.autonomy_index
    
    def to_tuple(self) -> Tuple[int, int, int, int, int]:
        """Convert to tuple for hashing"""
        return (self.modality, self.depth, self.context, self.salience, self.autonomy_index)


@dataclass 
class PrimeFactorization:
    """Prime factorization representation for compression"""
    factors: List[int] = field(default_factory=list)
    exponents: List[int] = field(default_factory=list)
    original_value: int = 0
    compression_ratio: float = 0.0
    
    @classmethod
    def factorize(cls, n: int) -> 'PrimeFactorization':
        """Compute prime factorization of integer"""
        if n <= 1:
            return cls([], [], n, 0.0)
            
        factors = []
        exponents = []
        original = n
        
        # Check for factor 2
        if n % 2 == 0:
            factors.append(2)
            exp = 0
            while n % 2 == 0:
                exp += 1
                n //= 2
            exponents.append(exp)
        
        # Check for odd factors from 3 onwards
        i = 3
        while i * i <= n:
            if n % i == 0:
                factors.append(i)
                exp = 0
                while n % i == 0:
                    exp += 1
                    n //= i
                exponents.append(exp)
            i += 2
        
        # If n is a prime greater than 2
        if n > 2:
            factors.append(n)
            exponents.append(1)
        
        # Calculate compression ratio
        original_bits = original.bit_length()
        compressed_bits = sum(f.bit_length() + e.bit_length() for f, e in zip(factors, exponents))
        
        # Improved compression ratio calculation
        if original_bits > 0 and compressed_bits > 0:
            # More conservative calculation that avoids negative ratios
            if compressed_bits < original_bits:
                compression_ratio = (original_bits - compressed_bits) / original_bits
            else:
                compression_ratio = 0.0  # No compression achieved
        else:
            compression_ratio = 0.0
        
        return cls(factors, exponents, original, compression_ratio)
    
    def reconstruct(self) -> int:
        """Reconstruct original value from factorization"""
        if not self.factors:
            return self.original_value
        return reduce(lambda x, y: x * y, 
                     [f ** e for f, e in zip(self.factors, self.exponents)], 1)


@dataclass
class TensorFragment:
    """Core tensor fragment with prime factorization encoding"""
    shape: TensorShape
    data: np.ndarray
    factorization: Optional[PrimeFactorization] = None
    signature: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    hypergraph_refs: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize tensor fragment with validation and compression"""
        self._validate_data()
        self._compute_signature()
        self._compute_factorization()
    
    def _validate_data(self):
        """Validate tensor data against shape"""
        expected_shape = self.shape.to_array()
        expected_size = np.prod(expected_shape)
        actual_size = self.data.size
        
        if self.data.shape != tuple(expected_shape):
            if actual_size == expected_size:
                # Same total size, just reshape
                logger.warning(f"Reshaping tensor from {self.data.shape} to {tuple(expected_shape)}")
                self.data = self.data.reshape(expected_shape)
            else:
                # Different total size, need to adjust
                if actual_size > expected_size:
                    # Truncate data
                    self.data = self.data.flatten()[:expected_size].reshape(expected_shape)
                else:
                    # Pad data
                    flat_data = self.data.flatten()
                    padded_data = np.zeros(expected_size, dtype=self.data.dtype)
                    padded_data[:len(flat_data)] = flat_data
                    self.data = padded_data.reshape(expected_shape)
                logger.warning(f"Adjusted tensor size from {actual_size} to {expected_size}")
    
    def _compute_signature(self):
        """Compute unique signature for tensor fragment"""
        shape_str = str(self.shape.to_tuple())
        data_hash = hashlib.sha256(self.data.tobytes()).hexdigest()[:16]
        self.signature = f"tensor_{shape_str}_{data_hash}"
    
    def _compute_factorization(self):
        """Compute prime factorization for cognitive compression"""
        # Use tensor size for factorization
        tensor_size = self.shape.total_size()
        if tensor_size > 1:
            self.factorization = PrimeFactorization.factorize(tensor_size)
    
    def encode_for_hypergraph(self) -> Dict[str, Any]:
        """Encode tensor fragment for hypergraph node representation"""
        return {
            'type': 'TensorFragment',
            'shape': self.shape.to_tuple(),
            'signature': self.signature,
            'modality': Modality(self.shape.modality).name,
            'factorization': {
                'factors': self.factorization.factors if self.factorization else [],
                'exponents': self.factorization.exponents if self.factorization else [],
                'compression_ratio': self.factorization.compression_ratio if self.factorization else 0.0
            },
            'metadata': self.metadata,
            'hypergraph_refs': self.hypergraph_refs
        }
    
    def get_compression_ratio(self) -> float:
        """Get compression ratio from prime factorization"""
        return self.factorization.compression_ratio if self.factorization else 0.0


class TensorFragmentRegistry:
    """Registry for managing tensor fragments and their relationships"""
    
    def __init__(self):
        self.fragments: Dict[str, TensorFragment] = {}
        self.shape_index: Dict[Tuple, List[str]] = {}
        self.modality_index: Dict[Modality, List[str]] = {}
        self.compression_stats = {
            'total_fragments': 0,
            'average_compression': 0.0,
            'compression_count': 0
        }
    
    def register_fragment(self, fragment: TensorFragment) -> str:
        """Register a tensor fragment and update indices"""
        signature = fragment.signature
        self.fragments[signature] = fragment
        
        # Update shape index
        shape_tuple = fragment.shape.to_tuple()
        if shape_tuple not in self.shape_index:
            self.shape_index[shape_tuple] = []
        self.shape_index[shape_tuple].append(signature)
        
        # Update modality index  
        modality = Modality(fragment.shape.modality)
        if modality not in self.modality_index:
            self.modality_index[modality] = []
        self.modality_index[modality].append(signature)
        
        # Update compression stats
        self._update_compression_stats(fragment)
        
        logger.info(f"Registered tensor fragment: {signature}")
        return signature
    
    def get_fragment(self, signature: str) -> Optional[TensorFragment]:
        """Retrieve tensor fragment by signature"""
        return self.fragments.get(signature)
    
    def find_by_shape(self, shape: TensorShape) -> List[TensorFragment]:
        """Find all fragments with given shape"""
        shape_tuple = shape.to_tuple()
        signatures = self.shape_index.get(shape_tuple, [])
        return [self.fragments[sig] for sig in signatures]
    
    def find_by_modality(self, modality: Modality) -> List[TensorFragment]:
        """Find all fragments with given modality"""
        signatures = self.modality_index.get(modality, [])
        return [self.fragments[sig] for sig in signatures]
    
    def _update_compression_stats(self, fragment: TensorFragment):
        """Update compression statistics"""
        self.compression_stats['total_fragments'] += 1
        
        if fragment.factorization and fragment.factorization.compression_ratio > 0:
            count = self.compression_stats['compression_count']
            avg = self.compression_stats['average_compression']
            new_ratio = fragment.factorization.compression_ratio
            
            # Update running average
            self.compression_stats['average_compression'] = (avg * count + new_ratio) / (count + 1)
            self.compression_stats['compression_count'] += 1
    
    def get_compression_statistics(self) -> Dict[str, float]:
        """Get compression performance statistics"""
        return self.compression_stats.copy()


class AgentStateEncoder:
    """Encode agent states as tensor fragments"""
    
    def __init__(self, registry: TensorFragmentRegistry):
        self.registry = registry
        
    def encode_agent_state(self, agent_id: str, state_data: Dict[str, Any]) -> TensorFragment:
        """Encode agent state as tensor fragment"""
        # Determine tensor shape based on agent characteristics
        modality = self._determine_modality(state_data)
        depth = max(1, min(15, len(state_data.get('reasoning_chain', []))))
        context = max(1, min(31, len(state_data.get('context_history', []))))
        salience = max(1, min(15, int(state_data.get('importance', 1) * 15)))
        autonomy = max(1, min(7, int(state_data.get('autonomy_level', 0.5) * 7)))
        
        shape = TensorShape(modality, depth, context, salience, autonomy)
        
        # Create tensor data from state
        data = self._create_tensor_data(shape, state_data)
        
        # Create fragment with metadata
        fragment = TensorFragment(
            shape=shape,
            data=data,
            metadata={
                'agent_id': agent_id,
                'encoding_type': 'agent_state',
                'state_keys': list(state_data.keys()),
                'timestamp': str(np.datetime64('now'))
            }
        )
        
        # Register fragment
        signature = self.registry.register_fragment(fragment)
        logger.info(f"Encoded agent {agent_id} state as tensor fragment {signature}")
        
        return fragment
    
    def _determine_modality(self, state_data: Dict[str, Any]) -> int:
        """Determine modality based on state data characteristics"""
        if 'financial' in str(state_data).lower():
            return Modality.FINANCIAL.value
        elif 'agent' in str(state_data).lower():
            return Modality.AGENT.value  
        elif 'reasoning' in str(state_data).lower():
            return Modality.COGNITIVE.value
        elif 'time' in str(state_data).lower():
            return Modality.TEMPORAL.value
        else:
            return Modality.COGNITIVE.value  # Default
    
    def _create_tensor_data(self, shape: TensorShape, state_data: Dict[str, Any]) -> np.ndarray:
        """Create tensor data from state information"""
        shape_array = shape.to_array()
        total_size = np.prod(shape_array)
        
        # Create base tensor with small random values
        data = np.random.random(shape_array) * 0.1
        
        # Encode specific state information into tensor
        if 'values' in state_data:
            values = np.array(state_data['values'])
            # Flatten and fit into tensor
            flat_data = data.flatten()
            n_values = min(len(values), len(flat_data))
            flat_data[:n_values] = values[:n_values]
            data = flat_data.reshape(shape_array)
        
        return data.astype(np.float32)


class TensorOperations:
    """Optimized tensor operations for cognitive processing"""
    
    @staticmethod
    def tensor_similarity(t1: TensorFragment, t2: TensorFragment) -> float:
        """Compute similarity between tensor fragments"""
        if t1.shape.to_tuple() != t2.shape.to_tuple():
            return 0.0
        
        # Compute cosine similarity
        flat1 = t1.data.flatten()
        flat2 = t2.data.flatten()
        
        dot_product = np.dot(flat1, flat2)
        norm1 = np.linalg.norm(flat1)
        norm2 = np.linalg.norm(flat2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        # Handle floating point precision issues
        return float(np.clip(similarity, 0.0, 1.0))
    
    @staticmethod
    def compress_tensor_sequence(fragments: List[TensorFragment]) -> Dict[str, Any]:
        """Compress sequence of tensor fragments using prime factorization"""
        total_compression = 0.0
        compressed_count = 0
        
        for fragment in fragments:
            if fragment.factorization:
                total_compression += fragment.factorization.compression_ratio
                compressed_count += 1
        
        avg_compression = total_compression / compressed_count if compressed_count > 0 else 0.0
        
        return {
            'sequence_length': len(fragments),
            'compressed_fragments': compressed_count,
            'average_compression_ratio': avg_compression,
            'meets_70_percent_threshold': avg_compression >= 0.7
        }
    
    @staticmethod
    def validate_tensor_shape(shape: TensorShape) -> Dict[str, bool]:
        """Validate tensor shape meets specifications"""
        return {
            'valid_modality': 0 <= shape.modality <= 7,
            'valid_depth': 0 <= shape.depth <= 15,
            'valid_context': 0 <= shape.context <= 31,
            'valid_salience': 0 <= shape.salience <= 15,
            'valid_autonomy': 0 <= shape.autonomy_index <= 7,
            'is_5_dimensional': True  # By construction
        }


# Factory functions for creating standard tensor configurations

def create_financial_tensor(depth: int = 8, context: int = 16, salience: int = 10) -> TensorShape:
    """Create standard financial processing tensor shape"""
    return TensorShape(
        modality=Modality.FINANCIAL.value,
        depth=min(15, depth),
        context=min(31, context),
        salience=min(15, salience),
        autonomy_index=5  # Standard autonomy for financial agents
    )

def create_cognitive_tensor(depth: int = 12, context: int = 20, autonomy: int = 7) -> TensorShape:
    """Create standard cognitive processing tensor shape"""
    return TensorShape(
        modality=Modality.COGNITIVE.value,
        depth=min(15, depth),
        context=min(31, context),
        salience=12,  # High salience for cognitive processing
        autonomy_index=min(7, autonomy)
    )

def create_agent_tensor(agent_type: str = "financial", autonomy: int = 5) -> TensorShape:
    """Create tensor shape for agent encoding"""
    modality = Modality.FINANCIAL.value if agent_type == "financial" else Modality.AGENT.value
    return TensorShape(
        modality=modality,
        depth=10,
        context=15,
        salience=8,
        autonomy_index=min(7, autonomy)
    )


# Global registry instance
_global_registry = TensorFragmentRegistry()

def get_global_registry() -> TensorFragmentRegistry:
    """Get the global tensor fragment registry"""
    return _global_registry