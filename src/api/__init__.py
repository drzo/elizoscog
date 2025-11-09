"""
Distributed Cognitive Mesh APIs - Phase 4 Implementation

This package provides the core API infrastructure for distributed cognitive operations,
including REST/WebSocket endpoints, state synchronization, and external system bindings.
"""

from .mesh_api import CognitiveMeshAPI
from .websocket_handler import WebSocketHandler
from .state_manager import DistributedStateManager
from .auth_manager import AuthenticationManager
from .external_bindings import UnityBinding, ROSBinding, WebAgentBinding

__all__ = [
    'CognitiveMeshAPI',
    'WebSocketHandler', 
    'DistributedStateManager',
    'AuthenticationManager',
    'UnityBinding',
    'ROSBinding', 
    'WebAgentBinding'
]

__version__ = "1.0.0"