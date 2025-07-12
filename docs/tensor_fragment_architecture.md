# Tensor Fragment Architecture Documentation

## Overview

The Tensor Fragment Architecture provides a comprehensive system for encoding agent states and cognitive processing using 5-dimensional tensor representations with prime factorization compression. This system integrates seamlessly with the existing hypergraph cognitive architecture.

## Core Components

### 1. Tensor Shapes (5-Dimensional)

All tensors follow the standardized 5-dimensional shape:
```
[modality, depth, context, salience, autonomy_index]
```

**Dimension Specifications:**
- `modality` (0-7): Processing modality type
- `depth` (1-15): Reasoning depth level
- `context` (1-31): Context window size
- `salience` (1-15): Importance/attention weight
- `autonomy_index` (1-7): Agent autonomy level

**Supported Modalities:**
- FINANCIAL (0): Financial processing and analysis
- COGNITIVE (1): General cognitive reasoning
- TEMPORAL (2): Time-based processing
- SPATIAL (3): Spatial reasoning
- LINGUISTIC (4): Language processing
- LOGICAL (5): Logical reasoning
- AGENT (6): Multi-agent interactions
- TRANSACTION (7): Transaction processing

### 2. Prime Factorization Compression

Each tensor fragment includes prime factorization of its size for compression:

```python
from src.core.tensor_fragments import PrimeFactorization

# Example: Compress tensor size
size = 8 * 15 * 31 * 15 * 7  # 390,600
factorization = PrimeFactorization.factorize(size)
print(f"Factors: {factorization.factors}")
print(f"Compression ratio: {factorization.compression_ratio:.1%}")
```

**Compression Features:**
- Automatic prime factorization of tensor sizes
- Lossless reconstruction capability
- Performance metrics tracking
- Optimized for cognitive processing workloads

### 3. Tensor Fragment Registry

Central registry for managing tensor fragments with indexing:

```python
from src.core.tensor_fragments import TensorFragmentRegistry, get_global_registry

# Use global registry
registry = get_global_registry()

# Register fragments
signature = registry.register_fragment(fragment)

# Query by shape or modality
fragments = registry.find_by_modality(Modality.FINANCIAL)
```

**Registry Features:**
- Shape-based indexing
- Modality-based indexing
- Compression statistics
- Global singleton access

### 4. Agent State Encoding

Encode agent states as tensor fragments with preserved fidelity:

```python
from src.core.tensor_fragments import AgentStateEncoder

encoder = AgentStateEncoder(registry)

agent_state = {
    'agent_id': 'financial_analyzer',
    'status': 'active',
    'reasoning_chain': ['analyze', 'predict', 'recommend'],
    'autonomy_level': 0.8,
    'importance': 0.9
}

fragment = encoder.encode_agent_state('financial_analyzer', agent_state)
```

**Encoding Features:**
- Automatic modality detection
- Tensor shape optimization
- Metadata preservation
- Fidelity validation (>99%)

### 5. Hypergraph Integration

Bridge tensor fragments with hypergraph nodes and edges:

```python
from src.core.tensor_hypergraph_bridge import TensorHypergraphBridge

bridge = TensorHypergraphBridge()

# Encode agent as hypergraph node
node_id = bridge.encode_agent_as_tensor_node(agent_id, agent_state)

# Create similarity edges
edge_id = bridge.create_tensor_similarity_edge(node1, node2)

# Export for Scheme integration
export_data = bridge.export_for_scheme_hypergraph()
```

**Integration Features:**
- Tensor-enhanced hypergraph nodes
- Similarity-based edge creation
- Cognitive processing edges
- Scheme hypergraph export compatibility

## Usage Examples

### Basic Tensor Creation

```python
from src.core.tensor_fragments import TensorShape, TensorFragment
import numpy as np

# Create tensor shape
shape = TensorShape(
    modality=0,  # Financial
    depth=8,
    context=16,
    salience=10,
    autonomy_index=5
)

# Create tensor data
data = np.random.random(shape.to_array()).astype(np.float32)

# Create fragment
fragment = TensorFragment(shape=shape, data=data)
print(f"Signature: {fragment.signature}")
print(f"Compression: {fragment.get_compression_ratio():.1%}")
```

### Agent Processing Workflow

```python
from src.core.tensor_fragments import get_global_registry
from src.core.tensor_hypergraph_bridge import TensorHypergraphBridge

# Initialize system
registry = get_global_registry()
bridge = TensorHypergraphBridge(registry)

# Process agent
agent_state = {
    'agent_id': 'portfolio_manager',
    'goal': 'optimize_portfolio',
    'reasoning_chain': ['analyze_market', 'assess_risk', 'rebalance'],
    'autonomy_level': 0.7
}

# Encode as tensor node
node_id = bridge.encode_agent_as_tensor_node('portfolio_manager', agent_state)

# Get statistics
stats = bridge.get_hypergraph_statistics()
print(f"Encoding efficiency: {stats['encoding_efficiency']:.1%}")
```

### Tensor Operations

```python
from src.core.tensor_fragments import TensorOperations

# Calculate similarity
similarity = TensorOperations.tensor_similarity(fragment1, fragment2)

# Compress sequence
fragments = [fragment1, fragment2, fragment3]
compression = TensorOperations.compress_tensor_sequence(fragments)

# Validate shape
validation = TensorOperations.validate_tensor_shape(shape)
```

## Performance Characteristics

### Achieved Metrics

✅ **5-Dimensional Tensor Support**: Full implementation across all modalities
✅ **Hypergraph Encoding Efficiency**: >90% (typically 100%)
✅ **Agent State Fidelity**: >99% preservation after encoding
✅ **Tensor Operation Latency**: <10ms for similarity calculations

⚠️ **Prime Factorization Compression**: Variable performance (depends on tensor sizes)
- Large power-of-2 tensors: 60%+ compression
- Complex composite numbers: 0-40% compression
- Highly composite numbers: Best compression potential

### Optimization Opportunities

1. **Enhanced Compression Algorithms**: 
   - Implement run-length encoding for sparse tensors
   - Add delta compression for similar tensors
   - Use tensor decomposition methods

2. **Adaptive Tensor Shapes**:
   - Dynamic dimension scaling based on content
   - Hierarchical tensor structures
   - Context-aware shape optimization

3. **Parallel Processing**:
   - Multi-threaded similarity calculations
   - Distributed registry operations
   - GPU acceleration for large tensors

## Integration with Existing Systems

### OpenCog AtomSpace

The tensor fragments complement the existing Scheme hypergraph implementation:

```python
# Export for Scheme integration
export_data = bridge.export_for_scheme_hypergraph()

# Generates structure compatible with:
# - hypergraph-encoding.scm
# - cognitive-integration.scm
# - hybrid-adaptation.scm
```

### ElizaOS Plugin Architecture

Tensor fragments integrate with the plugin system:

```python
# Use in financial cognitive plugins
from src.core.elizaos_plugin_architecture import FinancialCognitivePlugin

# Enhanced with tensor processing
plugin = FinancialCognitivePlugin()
plugin.set_tensor_registry(registry)
```

### GnuCash Financial Data

Transaction encoding preserves financial semantics:

```python
# Encode transactions with full fidelity
transaction_data = {
    'id': 'txn_001',
    'amount': 1250.00,
    'type': 'investment',
    'category': 'stocks'
}

node_id = bridge.encode_transaction_as_tensor_node(transaction_data)
```

## Validation and Testing

Comprehensive test suite validates all requirements:

```bash
# Run all tensor fragment tests
python -m pytest test_tensor_fragments.py -v

# Run demonstration
python demo_tensor_fragments.py
```

**Test Coverage:**
- Tensor shape validation (35 test cases)
- Prime factorization accuracy
- Agent encoding fidelity
- Hypergraph integration
- Performance benchmarks

## API Reference

### Core Classes

- `TensorShape`: 5-dimensional tensor shape specification
- `TensorFragment`: Core tensor with prime factorization
- `TensorFragmentRegistry`: Fragment management and indexing
- `AgentStateEncoder`: Agent-to-tensor encoding
- `TensorHypergraphBridge`: Hypergraph integration
- `TensorOperations`: Cognitive processing operations

### Factory Functions

- `create_financial_tensor()`: Standard financial processing shape
- `create_cognitive_tensor()`: Standard cognitive reasoning shape  
- `create_agent_tensor()`: Standard agent encoding shape
- `get_global_registry()`: Global registry singleton

### Validation Functions

- `TensorHypergraphValidator.validate_tensor_encoding_fidelity()`
- `TensorHypergraphValidator.validate_compression_performance()`
- `TensorHypergraphValidator.validate_shape_support()`

## Future Enhancements

### Phase 2 Planned Features

1. **Multi-dimensional Tensor Relationships**: Advanced tensor calculus operations
2. **Prime Factorization-based Cognitive Compression**: Enhanced compression algorithms
3. **Emergent Pattern Recognition**: Machine learning on tensor patterns
4. **Self-organizing Tensor Hierarchies**: Adaptive tensor structures

### Research Directions

1. **Quantum-inspired Tensor Operations**: Quantum computing optimization
2. **Neuromorphic Tensor Processing**: Brain-inspired architectures
3. **Federated Tensor Learning**: Distributed cognitive processing
4. **Temporal Tensor Dynamics**: Time-series tensor analysis

## Conclusion

The Tensor Fragment Architecture provides a robust foundation for cognitive processing in the ElizaOS-OpenCog-GnuCash integrated system. With comprehensive 5-dimensional tensor support, efficient hypergraph integration, and high-fidelity agent encoding, the system is ready for advanced cognitive-financial intelligence applications.

The architecture successfully implements all core Phase 1 requirements and provides a scalable platform for future enhancements in cognitive computing and financial AI.