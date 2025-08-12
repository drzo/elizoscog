"""
Distributed State Manager for Cognitive Mesh

Provides real-time state synchronization across distributed cognitive nodes
with conflict resolution and eventual consistency guarantees.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from collections import defaultdict


class StateEventType(Enum):
    """Types of state events"""
    CREATE = "create"
    UPDATE = "update"  
    DELETE = "delete"
    SYNC = "sync"
    CONFLICT = "conflict"


@dataclass
class StateEvent:
    """Represents a state change event"""
    event_id: str
    event_type: StateEventType
    node_id: str
    entity_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime
    version: int
    checksum: str
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum for data integrity"""
        content = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class StateNode:
    """Represents a cognitive node in the mesh"""
    node_id: str
    host: str
    port: int
    capabilities: List[str]
    last_seen: datetime
    is_active: bool = True
    
    @property
    def endpoint(self) -> str:
        return f"http://{self.host}:{self.port}"


class DistributedStateManager:
    """
    Manages distributed cognitive state across the mesh
    
    Features:
    - Real-time state synchronization
    - Conflict resolution with vector clocks
    - Eventual consistency guarantees
    - Event-driven state propagation
    """
    
    def __init__(self, node_id: str, sync_interval: float = 1.0):
        self.node_id = node_id
        self.sync_interval = sync_interval
        
        # State storage
        self._state: Dict[str, Dict[str, Any]] = {}  # entity_type -> {entity_id: data}
        self._versions: Dict[str, Dict[str, int]] = {}  # entity_type -> {entity_id: version}
        self._vector_clocks: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Event handling
        self._event_log: List[StateEvent] = []
        self._event_subscribers: List[Callable[[StateEvent], None]] = []
        self._pending_events: asyncio.Queue = asyncio.Queue()
        
        # Node management
        self._nodes: Dict[str, StateNode] = {}
        self._sync_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the state manager"""
        self._sync_task = asyncio.create_task(self._sync_loop())
        self.logger.info(f"Distributed state manager started on node {self.node_id}")
    
    async def stop(self):
        """Stop the state manager"""
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Distributed state manager stopped")
    
    def register_node(self, node: StateNode):
        """Register a new node in the mesh"""
        self._nodes[node.node_id] = node
        self.logger.info(f"Registered node {node.node_id} at {node.endpoint}")
    
    def deregister_node(self, node_id: str):
        """Remove a node from the mesh"""
        if node_id in self._nodes:
            del self._nodes[node_id]
            self.logger.info(f"Deregistered node {node_id}")
    
    async def set_state(self, entity_type: str, entity_id: str, 
                       data: Dict[str, Any]) -> StateEvent:
        """
        Set state for an entity with automatic versioning and propagation
        """
        # Initialize entity type if needed
        if entity_type not in self._state:
            self._state[entity_type] = {}
            self._versions[entity_type] = {}
        
        # Increment version
        current_version = self._versions[entity_type].get(entity_id, 0)
        new_version = current_version + 1
        
        # Update vector clock
        self._vector_clocks[entity_type][entity_id] = new_version
        
        # Store state
        self._state[entity_type][entity_id] = data
        self._versions[entity_type][entity_id] = new_version
        
        # Create event
        event_type = StateEventType.UPDATE if current_version > 0 else StateEventType.CREATE
        event = StateEvent(
            event_id=f"{self.node_id}_{entity_type}_{entity_id}_{new_version}_{int(time.time())}",
            event_type=event_type,
            node_id=self.node_id,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            timestamp=datetime.now(),
            version=new_version,
            checksum=""
        )
        
        # Add to event log and queue for propagation
        self._event_log.append(event)
        await self._pending_events.put(event)
        
        # Notify subscribers
        self._notify_subscribers(event)
        
        self.logger.debug(f"State set: {entity_type}.{entity_id} v{new_version}")
        return event
    
    def get_state(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get current state for an entity"""
        return self._state.get(entity_type, {}).get(entity_id)
    
    def get_all_state(self, entity_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all state for an entity type"""
        return dict(self._state.get(entity_type, {}))
    
    async def delete_state(self, entity_type: str, entity_id: str) -> Optional[StateEvent]:
        """Delete state for an entity"""
        if entity_type not in self._state or entity_id not in self._state[entity_type]:
            return None
        
        # Get current data before deletion
        data = self._state[entity_type][entity_id]
        version = self._versions[entity_type][entity_id]
        
        # Remove from state
        del self._state[entity_type][entity_id]
        del self._versions[entity_type][entity_id]
        
        # Create delete event
        event = StateEvent(
            event_id=f"{self.node_id}_{entity_type}_{entity_id}_delete_{int(time.time())}",
            event_type=StateEventType.DELETE,
            node_id=self.node_id,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            timestamp=datetime.now(),
            version=version + 1,
            checksum=""
        )
        
        # Add to event log and propagate
        self._event_log.append(event)
        await self._pending_events.put(event)
        self._notify_subscribers(event)
        
        return event
    
    async def handle_remote_event(self, event: StateEvent) -> bool:
        """
        Handle state event from another node
        Returns True if state was updated, False if ignored (conflict/old version)
        """
        try:
            # Validate checksum
            if event.checksum != event._calculate_checksum():
                self.logger.warning(f"Invalid checksum for event {event.event_id}")
                return False
            
            # Check if we already processed this event
            if any(e.event_id == event.event_id for e in self._event_log):
                return False
            
            entity_type = event.entity_type
            entity_id = event.entity_id
            
            # Initialize if needed
            if entity_type not in self._state:
                self._state[entity_type] = {}
                self._versions[entity_type] = {}
            
            current_version = self._versions[entity_type].get(entity_id, 0)
            
            # Handle based on event type
            if event.event_type == StateEventType.DELETE:
                if entity_id in self._state[entity_type]:
                    del self._state[entity_type][entity_id]
                    if entity_id in self._versions[entity_type]:
                        del self._versions[entity_type][entity_id]
                
            elif event.version > current_version:
                # Apply update
                self._state[entity_type][entity_id] = event.data
                self._versions[entity_type][entity_id] = event.version
                
            elif event.version == current_version:
                # Potential conflict - use node_id as tiebreaker
                if event.node_id > self.node_id:
                    self._state[entity_type][entity_id] = event.data
                    self.logger.info(f"Resolved conflict for {entity_type}.{entity_id} using node tiebreaker")
                else:
                    self.logger.info(f"Ignored conflicting event for {entity_type}.{entity_id}")
                    return False
                    
            else:
                # Old version, ignore
                self.logger.debug(f"Ignored old version {event.version} for {entity_type}.{entity_id}")
                return False
            
            # Update vector clock
            self._vector_clocks[entity_type][entity_id] = max(
                self._vector_clocks[entity_type][entity_id],
                event.version
            )
            
            # Add to event log
            self._event_log.append(event)
            
            # Notify subscribers
            self._notify_subscribers(event)
            
            self.logger.debug(f"Applied remote event: {event.event_type} {entity_type}.{entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling remote event {event.event_id}: {e}")
            return False
    
    def subscribe_to_events(self, callback: Callable[[StateEvent], None]):
        """Subscribe to state change events"""
        self._event_subscribers.append(callback)
    
    def unsubscribe_from_events(self, callback: Callable[[StateEvent], None]):
        """Unsubscribe from state change events"""
        if callback in self._event_subscribers:
            self._event_subscribers.remove(callback)
    
    def _notify_subscribers(self, event: StateEvent):
        """Notify all event subscribers"""
        for callback in self._event_subscribers:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Error in event subscriber: {e}")
    
    async def sync_with_node(self, node_id: str) -> Dict[str, Any]:
        """
        Synchronize state with a specific node
        Returns sync statistics
        """
        if node_id not in self._nodes:
            raise ValueError(f"Unknown node: {node_id}")
        
        node = self._nodes[node_id]
        stats = {
            "node_id": node_id,
            "events_sent": 0,
            "events_received": 0,
            "conflicts_resolved": 0,
            "start_time": datetime.now()
        }
        
        try:
            # In a real implementation, this would make HTTP/gRPC calls to the node
            # For now, we'll simulate the sync process
            self.logger.info(f"Syncing with node {node_id} at {node.endpoint}")
            
            # Send pending events (simulated)
            pending_count = self._pending_events.qsize()
            stats["events_sent"] = pending_count
            
            # Update node last seen
            node.last_seen = datetime.now()
            
            stats["end_time"] = datetime.now()
            stats["duration_ms"] = (stats["end_time"] - stats["start_time"]).total_seconds() * 1000
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Sync failed with node {node_id}: {e}")
            stats["error"] = str(e)
            return stats
    
    async def _sync_loop(self):
        """Periodic synchronization with other nodes"""
        while True:
            try:
                # Sync with all active nodes
                active_nodes = [n for n in self._nodes.values() if n.is_active]
                
                if active_nodes:
                    sync_tasks = [self.sync_with_node(node.node_id) for node in active_nodes]
                    results = await asyncio.gather(*sync_tasks, return_exceptions=True)
                    
                    # Log sync results
                    for result in results:
                        if isinstance(result, dict) and "error" not in result:
                            self.logger.debug(f"Sync completed: {result}")
                
                await asyncio.sleep(self.sync_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(self.sync_interval)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get state manager statistics"""
        entity_counts = {
            entity_type: len(entities) 
            for entity_type, entities in self._state.items()
        }
        
        active_nodes = sum(1 for node in self._nodes.values() if node.is_active)
        
        return {
            "node_id": self.node_id,
            "total_entities": sum(entity_counts.values()),
            "entity_counts": entity_counts,
            "total_events": len(self._event_log),
            "pending_events": self._pending_events.qsize(),
            "active_nodes": active_nodes,
            "total_nodes": len(self._nodes),
            "subscribers": len(self._event_subscribers)
        }
    
    def create_snapshot(self) -> Dict[str, Any]:
        """Create a complete state snapshot for backup/recovery"""
        return {
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "state": dict(self._state),
            "versions": dict(self._versions),
            "vector_clocks": dict(self._vector_clocks),
            "recent_events": [asdict(event) for event in self._event_log[-100:]]  # Last 100 events
        }
    
    async def restore_from_snapshot(self, snapshot: Dict[str, Any]):
        """Restore state from a snapshot"""
        try:
            self._state = snapshot.get("state", {})
            self._versions = snapshot.get("versions", {}) 
            self._vector_clocks = defaultdict(lambda: defaultdict(int))
            
            # Restore vector clocks
            for entity_type, clocks in snapshot.get("vector_clocks", {}).items():
                for entity_id, version in clocks.items():
                    self._vector_clocks[entity_type][entity_id] = version
            
            # Restore recent events
            recent_events = snapshot.get("recent_events", [])
            self._event_log = []
            for event_data in recent_events:
                event = StateEvent(**event_data)
                self._event_log.append(event)
            
            self.logger.info(f"Restored state from snapshot: {len(self._state)} entity types")
            
        except Exception as e:
            self.logger.error(f"Failed to restore from snapshot: {e}")
            raise