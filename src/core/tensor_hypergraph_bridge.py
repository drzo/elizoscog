#!/usr/bin/env python3
"""
Hypergraph Tensor Integration Module
Bridges tensor fragments with the existing hypergraph cognitive architecture
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path

from .tensor_fragments import (
    TensorFragment, TensorShape, TensorFragmentRegistry, 
    AgentStateEncoder, Modality, get_global_registry
)

logger = logging.getLogger(__name__)


@dataclass
class HypergraphNode:
    """Python representation of hypergraph node with tensor encoding"""
    node_id: str
    node_type: str  # 'TensorFragment', 'Agent', 'Transaction', etc.
    content: Dict[str, Any]
    attributes: Dict[str, Any] = field(default_factory=dict)
    tensor_fragments: List[str] = field(default_factory=list)  # Fragment signatures
    hyperedges: List[str] = field(default_factory=list)


@dataclass
class HypergraphEdge:
    """Python representation of hypergraph edge"""
    edge_id: str
    edge_type: str  # 'tensor_similarity', 'agent_interaction', etc.
    connected_nodes: List[str]
    attributes: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    tensor_encoding: Optional[str] = None  # Associated tensor fragment


class TensorHypergraphBridge:
    """Bridge between tensor fragments and hypergraph representation"""
    
    def __init__(self, registry: Optional[TensorFragmentRegistry] = None):
        self.registry = registry or get_global_registry()
        self.nodes: Dict[str, HypergraphNode] = {}
        self.edges: Dict[str, HypergraphEdge] = {}
        self.next_node_id = 0
        self.next_edge_id = 0
        
    def encode_agent_as_tensor_node(self, agent_id: str, agent_state: Dict[str, Any]) -> str:
        """Encode agent state as tensor fragment and create hypergraph node"""
        encoder = AgentStateEncoder(self.registry)
        fragment = encoder.encode_agent_state(agent_id, agent_state)
        
        # Create hypergraph node
        node_id = f"agent_node_{self.next_node_id}"
        self.next_node_id += 1
        
        node = HypergraphNode(
            node_id=node_id,
            node_type="Agent",
            content={
                'agent_id': agent_id,
                'state_summary': self._summarize_state(agent_state),
                'tensor_signature': fragment.signature
            },
            attributes={
                'modality': Modality(fragment.shape.modality).name,
                'autonomy_level': fragment.shape.autonomy_index,
                'cognitive_depth': fragment.shape.depth,
                'context_size': fragment.shape.context,
                'salience': fragment.shape.salience,
                'compression_ratio': fragment.get_compression_ratio()
            },
            tensor_fragments=[fragment.signature]
        )
        
        self.nodes[node_id] = node
        logger.info(f"Created tensor-encoded agent node: {node_id}")
        return node_id
    
    def encode_transaction_as_tensor_node(self, transaction_data: Dict[str, Any]) -> str:
        """Encode financial transaction as tensor fragment and hypergraph node"""
        # Create tensor shape for transaction with minimum dimensions
        amount = float(transaction_data.get('amount', 0))
        salience = max(1, min(15, int(abs(amount) / 100)))  # Ensure minimum 1
        
        shape = TensorShape(
            modality=Modality.FINANCIAL.value,
            depth=5,  # Transaction processing depth
            context=10,  # Transaction context window
            salience=salience,
            autonomy_index=3  # Moderate autonomy for transactions
        )
        
        # Create tensor data from transaction
        data = self._transaction_to_tensor(shape, transaction_data)
        
        fragment = TensorFragment(
            shape=shape,
            data=data,
            metadata={
                'encoding_type': 'financial_transaction',
                'transaction_id': transaction_data.get('id', 'unknown'),
                'amount': transaction_data.get('amount', 0),
                'timestamp': transaction_data.get('timestamp', 'unknown')
            }
        )
        
        signature = self.registry.register_fragment(fragment)
        
        # Create hypergraph node
        node_id = f"transaction_node_{self.next_node_id}"
        self.next_node_id += 1
        
        node = HypergraphNode(
            node_id=node_id,
            node_type="Transaction",
            content={
                'transaction_id': transaction_data.get('id', 'unknown'),
                'amount': transaction_data.get('amount', 0),
                'category': transaction_data.get('category', 'unknown'),
                'tensor_signature': signature
            },
            attributes={
                'modality': 'FINANCIAL',
                'transaction_type': transaction_data.get('type', 'unknown'),
                'compression_ratio': fragment.get_compression_ratio()
            },
            tensor_fragments=[signature]
        )
        
        self.nodes[node_id] = node
        logger.info(f"Created tensor-encoded transaction node: {node_id}")
        return node_id
    
    def create_tensor_similarity_edge(self, node1_id: str, node2_id: str) -> Optional[str]:
        """Create hypergraph edge based on tensor similarity"""
        node1 = self.nodes.get(node1_id)
        node2 = self.nodes.get(node2_id)
        
        if not node1 or not node2:
            return None
        
        # Get tensor fragments for both nodes
        fragments1 = [self.registry.get_fragment(sig) for sig in node1.tensor_fragments]
        fragments2 = [self.registry.get_fragment(sig) for sig in node2.tensor_fragments]
        
        # Remove None values
        fragments1 = [f for f in fragments1 if f is not None]
        fragments2 = [f for f in fragments2 if f is not None]
        
        if not fragments1 or not fragments2:
            return None
        
        # Compute maximum similarity between any pair of fragments
        max_similarity = 0.0
        best_pair = None
        
        from .tensor_fragments import TensorOperations
        
        for f1 in fragments1:
            for f2 in fragments2:
                similarity = TensorOperations.tensor_similarity(f1, f2)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_pair = (f1.signature, f2.signature)
        
        # Create edge if similarity is significant
        if max_similarity > 0.1:  # Threshold for meaningful similarity
            edge_id = f"similarity_edge_{self.next_edge_id}"
            self.next_edge_id += 1
            
            edge = HypergraphEdge(
                edge_id=edge_id,
                edge_type="tensor_similarity",
                connected_nodes=[node1_id, node2_id],
                attributes={
                    'similarity_score': max_similarity,
                    'fragment_pair': best_pair,
                    'similarity_type': 'tensor_cosine'
                },
                weight=max_similarity
            )
            
            self.edges[edge_id] = edge
            
            # Update nodes to reference this edge
            node1.hyperedges.append(edge_id)
            node2.hyperedges.append(edge_id)
            
            logger.info(f"Created similarity edge {edge_id} with similarity {max_similarity:.3f}")
            return edge_id
        
        return None
    
    def create_cognitive_processing_edge(self, processor_node: str, target_nodes: List[str]) -> str:
        """Create hypergraph edge for cognitive processing relationships"""
        edge_id = f"cognitive_edge_{self.next_edge_id}"
        self.next_edge_id += 1
        
        all_nodes = [processor_node] + target_nodes
        
        edge = HypergraphEdge(
            edge_id=edge_id,
            edge_type="cognitive_processing",
            connected_nodes=all_nodes,
            attributes={
                'processor': processor_node,
                'targets': target_nodes,
                'processing_type': 'tensor_analysis'
            },
            weight=len(target_nodes) * 0.5  # Weight based on number of targets
        )
        
        self.edges[edge_id] = edge
        
        # Update all connected nodes
        for node_id in all_nodes:
            if node_id in self.nodes:
                self.nodes[node_id].hyperedges.append(edge_id)
        
        logger.info(f"Created cognitive processing edge: {edge_id}")
        return edge_id
    
    def export_for_scheme_hypergraph(self) -> Dict[str, Any]:
        """Export hypergraph structure for integration with Scheme implementation"""
        nodes_export = {}
        edges_export = {}
        
        for node_id, node in self.nodes.items():
            nodes_export[node_id] = {
                'id': node.node_id,
                'type': node.node_type,
                'content': node.content,
                'attributes': node.attributes,
                'tensor_fragments': node.tensor_fragments,
                'hyperedges': node.hyperedges
            }
        
        for edge_id, edge in self.edges.items():
            edges_export[edge_id] = {
                'id': edge.edge_id,
                'type': edge.edge_type,
                'nodes': edge.connected_nodes,
                'attributes': edge.attributes,
                'weight': edge.weight,
                'tensor_encoding': edge.tensor_encoding
            }
        
        return {
            'nodes': nodes_export,
            'edges': edges_export,
            'statistics': self.get_hypergraph_statistics(),
            'tensor_statistics': self.registry.get_compression_statistics()
        }
    
    def get_hypergraph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the tensor-enhanced hypergraph"""
        node_types = {}
        edge_types = {}
        
        for node in self.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
        
        for edge in self.edges.values():
            edge_types[edge.edge_type] = edge_types.get(edge.edge_type, 0) + 1
        
        # Calculate tensor encoding efficiency
        tensor_encoded_nodes = sum(1 for node in self.nodes.values() if node.tensor_fragments)
        encoding_efficiency = tensor_encoded_nodes / len(self.nodes) if self.nodes else 0.0
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': node_types,
            'edge_types': edge_types,
            'tensor_encoded_nodes': tensor_encoded_nodes,
            'encoding_efficiency': encoding_efficiency,
            'meets_90_percent_efficiency': encoding_efficiency >= 0.9
        }
    
    def _summarize_state(self, state: Dict[str, Any]) -> str:
        """Create summary of agent state for hypergraph content"""
        key_info = []
        if 'status' in state:
            key_info.append(f"status:{state['status']}")
        if 'goal' in state:
            key_info.append(f"goal:{state['goal']}")
        if 'context' in state:
            key_info.append(f"context_items:{len(state['context'])}")
        return "; ".join(key_info) if key_info else "basic_state"
    
    def _transaction_to_tensor(self, shape: TensorShape, transaction: Dict[str, Any]) -> np.ndarray:
        """Convert transaction data to tensor representation"""
        shape_array = shape.to_array()
        data = np.zeros(shape_array, dtype=np.float32)
        
        # Get tensor dimensions (all should be >= 1 now)
        mod_dim, depth_dim, context_dim, salience_dim, autonomy_dim = shape_array
        
        # Encode transaction amount in a safe position
        amount = float(transaction.get('amount', 0))
        if mod_dim > 0 and depth_dim > 0 and context_dim > 0 and salience_dim > 0 and autonomy_dim > 0:
            data[min(mod_dim-1, 0), 0, 0, 0, 0] = amount / 1000.0  # Normalize amount
            
            # Encode transaction type if available
            if 'type' in transaction:
                type_hash = hash(transaction['type']) % depth_dim
                data[min(mod_dim-1, 0), type_hash, 0, 0, 0] = 1.0
            
            # Add some structured randomness for other dimensions
            for i in range(min(3, depth_dim)):
                for j in range(min(3, context_dim)):
                    safe_mod = min(mod_dim-1, 0)
                    data[safe_mod, i, j, 0, 0] = np.random.random() * 0.1
        
        return data


class TensorHypergraphValidator:
    """Validation and verification for tensor-hypergraph integration"""
    
    @staticmethod
    def validate_tensor_encoding_fidelity(bridge: TensorHypergraphBridge, 
                                         original_data: Dict[str, Any],
                                         node_id: str) -> Dict[str, Any]:
        """Validate that tensor encoding preserves agent/state information with >99% fidelity"""
        node = bridge.nodes.get(node_id)
        if not node:
            return {'fidelity': 0.0, 'error': 'Node not found'}
        
        # Check that key information is preserved
        preserved_keys = 0
        total_keys = len(original_data)
        
        for key in original_data:
            if key in str(node.content) or key in str(node.attributes):
                preserved_keys += 1
        
        fidelity = preserved_keys / total_keys if total_keys > 0 else 1.0
        
        # Check tensor fragment integrity
        tensor_integrity = True
        for fragment_sig in node.tensor_fragments:
            fragment = bridge.registry.get_fragment(fragment_sig)
            if not fragment:
                tensor_integrity = False
                break
        
        return {
            'fidelity': fidelity,
            'preserved_keys': preserved_keys,
            'total_keys': total_keys,
            'tensor_integrity': tensor_integrity,
            'meets_99_percent_threshold': fidelity >= 0.99,
            'node_id': node_id
        }
    
    @staticmethod
    def validate_compression_performance(registry: TensorFragmentRegistry) -> Dict[str, Any]:
        """Validate that prime factorization achieves >70% compression ratio"""
        stats = registry.get_compression_statistics()
        return {
            'average_compression_ratio': stats['average_compression'],
            'compressed_fragments': stats['compression_count'],
            'total_fragments': stats['total_fragments'],
            'meets_70_percent_threshold': stats['average_compression'] >= 0.7
        }
    
    @staticmethod
    def validate_shape_support(shape: TensorShape) -> Dict[str, Any]:
        """Validate 5-dimensional tensor shape support"""
        from .tensor_fragments import TensorOperations
        validation = TensorOperations.validate_tensor_shape(shape)
        
        all_valid = all(validation.values())
        
        return {
            'shape_validation': validation,
            'all_dimensions_valid': all_valid,
            'shape_tuple': shape.to_tuple(),
            'supports_5d_tensors': validation['is_5_dimensional']
        }


def create_demo_hypergraph() -> TensorHypergraphBridge:
    """Create demonstration hypergraph with tensor fragments"""
    bridge = TensorHypergraphBridge()
    
    # Create sample agent
    agent_state = {
        'agent_id': 'financial_analyzer_001',
        'status': 'active',
        'goal': 'analyze_spending_patterns', 
        'context': ['account_balance', 'recent_transactions', 'budget_goals'],
        'reasoning_chain': ['load_data', 'identify_patterns', 'generate_insights'],
        'autonomy_level': 0.8,
        'importance': 0.9
    }
    
    agent_node = bridge.encode_agent_as_tensor_node('financial_analyzer_001', agent_state)
    
    # Create sample transaction
    transaction = {
        'id': 'txn_001',
        'amount': 250.75,
        'type': 'expense',
        'category': 'groceries',
        'timestamp': '2024-01-15T10:30:00Z'
    }
    
    txn_node = bridge.encode_transaction_as_tensor_node(transaction)
    
    # Create similarity edge
    bridge.create_tensor_similarity_edge(agent_node, txn_node)
    
    # Create cognitive processing edge
    bridge.create_cognitive_processing_edge(agent_node, [txn_node])
    
    return bridge