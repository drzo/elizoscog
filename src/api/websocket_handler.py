"""
WebSocket Handler for Real-time Cognitive Mesh Communication

Provides real-time event streaming, notifications, and bidirectional
communication for distributed cognitive operations.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from dataclasses import asdict
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """
    Manages WebSocket connections with subscription-based event routing
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    async def connect(self, websocket: WebSocket, metadata: Dict[str, Any] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_subscriptions[websocket] = set()
        self.connection_metadata[websocket] = metadata or {}
        
        self.logger.info(f"WebSocket connection established. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if websocket in self.connection_subscriptions:
            del self.connection_subscriptions[websocket]
            
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
            
        self.logger.info(f"WebSocket connection closed. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            self.logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str, event_type: str = None):
        """Broadcast a message to all connections or filtered by subscription"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                # Check if connection is subscribed to this event type
                if event_type is None or event_type in self.connection_subscriptions.get(connection, set()):
                    await connection.send_text(message)
            except Exception as e:
                self.logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    def subscribe(self, websocket: WebSocket, event_types: List[str]):
        """Subscribe connection to specific event types"""
        if websocket in self.connection_subscriptions:
            self.connection_subscriptions[websocket].update(event_types)
            self.logger.debug(f"Connection subscribed to events: {event_types}")
    
    def unsubscribe(self, websocket: WebSocket, event_types: List[str]):
        """Unsubscribe connection from specific event types"""
        if websocket in self.connection_subscriptions:
            self.connection_subscriptions[websocket] -= set(event_types)
            self.logger.debug(f"Connection unsubscribed from events: {event_types}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        subscription_counts = {}
        for subscriptions in self.connection_subscriptions.values():
            for event_type in subscriptions:
                subscription_counts[event_type] = subscription_counts.get(event_type, 0) + 1
        
        return {
            "total_connections": len(self.active_connections),
            "subscription_counts": subscription_counts,
            "metadata": {str(id(ws)): meta for ws, meta in self.connection_metadata.items()}
        }


class WebSocketHandler:
    """
    High-level WebSocket handler for cognitive mesh operations
    
    Features:
    - Real-time state event streaming
    - Bidirectional cognitive query processing
    - Connection pooling and management
    - Event subscription filtering
    - Performance monitoring
    """
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.message_handlers: Dict[str, Any] = {}
        self.event_filters: Dict[str, Any] = {}
        self.performance_metrics = {
            "total_messages": 0,
            "total_broadcasts": 0,
            "average_response_time_ms": 0,
            "active_subscriptions": 0
        }
        self.logger = logging.getLogger(__name__)
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self.message_handlers = {
            "ping": self._handle_ping,
            "subscribe": self._handle_subscribe,
            "unsubscribe": self._handle_unsubscribe,
            "cognitive_query": self._handle_cognitive_query,
            "state_query": self._handle_state_query,
            "task_request": self._handle_task_request,
            "heartbeat": self._handle_heartbeat
        }
    
    async def connect(self, websocket: WebSocket, client_metadata: Dict[str, Any] = None):
        """Handle new WebSocket connection"""
        metadata = {
            "connected_at": datetime.now(),
            "client_type": client_metadata.get("client_type", "unknown") if client_metadata else "unknown",
            "capabilities": client_metadata.get("capabilities", []) if client_metadata else [],
            "message_count": 0
        }
        
        await self.connection_manager.connect(websocket, metadata)
        
        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "message": "Connected to Cognitive Mesh WebSocket",
            "timestamp": datetime.now().isoformat(),
            "available_events": list(self.message_handlers.keys()),
            "connection_id": str(id(websocket))
        }
        
        await self.connection_manager.send_personal_message(
            json.dumps(welcome_message),
            websocket
        )
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        self.connection_manager.disconnect(websocket)
    
    async def handle_message(self, websocket: WebSocket, message: str) -> Optional[Dict[str, Any]]:
        """
        Handle incoming WebSocket message
        Returns response message if any
        """
        start_time = datetime.now()
        
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            # Update message count
            if websocket in self.connection_manager.connection_metadata:
                self.connection_manager.connection_metadata[websocket]["message_count"] += 1
            
            self.performance_metrics["total_messages"] += 1
            
            # Route to appropriate handler
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                response = await handler(websocket, data)
                
                # Calculate response time
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Update average response time
                current_avg = self.performance_metrics["average_response_time_ms"]
                total_messages = self.performance_metrics["total_messages"]
                self.performance_metrics["average_response_time_ms"] = (
                    (current_avg * (total_messages - 1) + response_time) / total_messages
                )
                
                if response:
                    response["response_time_ms"] = response_time
                
                return response
            else:
                return {
                    "type": "error",
                    "error": "unknown_message_type",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except json.JSONDecodeError:
            return {
                "type": "error",
                "error": "invalid_json",
                "message": "Invalid JSON format",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
            return {
                "type": "error",
                "error": "processing_error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def broadcast(self, message: str, event_type: str = None):
        """Broadcast message to subscribed connections"""
        self.performance_metrics["total_broadcasts"] += 1
        await self.connection_manager.broadcast(message, event_type)
    
    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast a structured event"""
        event_message = {
            "type": "event",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast(json.dumps(event_message), event_type)
    
    async def subscribe(self, websocket: WebSocket, event_types: List[str]):
        """Subscribe connection to event types"""
        self.connection_manager.subscribe(websocket, event_types)
        self.performance_metrics["active_subscriptions"] = sum(
            len(subs) for subs in self.connection_manager.connection_subscriptions.values()
        )
    
    async def unsubscribe(self, websocket: WebSocket, event_types: List[str]):
        """Unsubscribe connection from event types"""
        self.connection_manager.unsubscribe(websocket, event_types)
        self.performance_metrics["active_subscriptions"] = sum(
            len(subs) for subs in self.connection_manager.connection_subscriptions.values()
        )
    
    # Default message handlers
    async def _handle_ping(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping message"""
        return {
            "type": "pong",
            "timestamp": datetime.now().isoformat(),
            "echo": data.get("echo", "")
        }
    
    async def _handle_subscribe(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription request"""
        event_types = data.get("event_types", [])
        
        if not isinstance(event_types, list):
            return {
                "type": "error",
                "error": "invalid_event_types",
                "message": "event_types must be a list"
            }
        
        await self.subscribe(websocket, event_types)
        
        return {
            "type": "subscribed",
            "event_types": event_types,
            "total_subscriptions": len(self.connection_manager.connection_subscriptions.get(websocket, set()))
        }
    
    async def _handle_unsubscribe(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unsubscription request"""
        event_types = data.get("event_types", [])
        
        if not isinstance(event_types, list):
            return {
                "type": "error",
                "error": "invalid_event_types", 
                "message": "event_types must be a list"
            }
        
        await self.unsubscribe(websocket, event_types)
        
        return {
            "type": "unsubscribed",
            "event_types": event_types,
            "total_subscriptions": len(self.connection_manager.connection_subscriptions.get(websocket, set()))
        }
    
    async def _handle_cognitive_query(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cognitive query over WebSocket"""
        query = data.get("query", "")
        query_type = data.get("query_type", "natural_language")
        parameters = data.get("parameters", {})
        
        # This would integrate with the main cognitive framework
        # For now, return a mock response
        return {
            "type": "cognitive_response",
            "query": query,
            "query_type": query_type,
            "response": f"Processed cognitive query: {query}",
            "confidence": 0.8,
            "processing_node": "current_node"
        }
    
    async def _handle_state_query(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle state query over WebSocket"""
        entity_type = data.get("entity_type", "")
        entity_id = data.get("entity_id", "")
        
        # This would integrate with the state manager
        return {
            "type": "state_response",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "state": {"mock": "state_data"},
            "version": 1
        }
    
    async def _handle_task_request(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle distributed task request over WebSocket"""
        task_type = data.get("task_type", "")
        task_data = data.get("task_data", {})
        priority = data.get("priority", 1)
        
        # Generate task ID
        task_id = f"ws_task_{int(datetime.now().timestamp())}"
        
        return {
            "type": "task_accepted",
            "task_id": task_id,
            "task_type": task_type,
            "status": "queued",
            "priority": priority,
            "estimated_completion": "5s"
        }
    
    async def _handle_heartbeat(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle client heartbeat"""
        return {
            "type": "heartbeat_ack",
            "server_time": datetime.now().isoformat(),
            "connection_uptime": self._get_connection_uptime(websocket)
        }
    
    def _get_connection_uptime(self, websocket: WebSocket) -> str:
        """Get connection uptime"""
        metadata = self.connection_manager.connection_metadata.get(websocket, {})
        connected_at = metadata.get("connected_at")
        
        if connected_at:
            uptime = datetime.now() - connected_at
            return str(uptime)
        
        return "unknown"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get WebSocket handler performance metrics"""
        connection_stats = self.connection_manager.get_stats()
        
        return {
            **self.performance_metrics,
            **connection_stats,
            "handlers": list(self.message_handlers.keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    def add_custom_handler(self, message_type: str, handler: Any):
        """Add custom message handler"""
        self.message_handlers[message_type] = handler
        self.logger.info(f"Added custom handler for message type: {message_type}")
    
    def remove_custom_handler(self, message_type: str):
        """Remove custom message handler"""
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
            self.logger.info(f"Removed custom handler for message type: {message_type}")


class RealtimeEventStreamer:
    """
    Specialized event streaming for real-time cognitive operations
    
    Optimized for sub-100ms event delivery and high-throughput scenarios
    """
    
    def __init__(self, websocket_handler: WebSocketHandler):
        self.websocket_handler = websocket_handler
        self.event_queue = asyncio.Queue()
        self.streaming_task: Optional[asyncio.Task] = None
        self.is_streaming = False
        self.logger = logging.getLogger(__name__)
    
    async def start_streaming(self):
        """Start real-time event streaming"""
        if not self.is_streaming:
            self.is_streaming = True
            self.streaming_task = asyncio.create_task(self._streaming_loop())
            self.logger.info("Real-time event streaming started")
    
    async def stop_streaming(self):
        """Stop real-time event streaming"""
        self.is_streaming = False
        
        if self.streaming_task:
            self.streaming_task.cancel()
            try:
                await self.streaming_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Real-time event streaming stopped")
    
    async def queue_event(self, event_type: str, data: Dict[str, Any], priority: int = 1):
        """Queue an event for streaming"""
        event = {
            "event_type": event_type,
            "data": data,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "queued_at": datetime.now()
        }
        
        await self.event_queue.put(event)
    
    async def _streaming_loop(self):
        """Main streaming loop for real-time event delivery"""
        while self.is_streaming:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
                
                # Calculate queuing delay
                queuing_delay = (datetime.now() - event["queued_at"]).total_seconds() * 1000
                event["queuing_delay_ms"] = queuing_delay
                
                # Stream to WebSocket connections
                await self.websocket_handler.broadcast_event(
                    event["event_type"],
                    event
                )
                
                # Mark task as done
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in streaming loop: {e}")
                await asyncio.sleep(0.001)  # Brief pause on error