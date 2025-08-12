#!/usr/bin/env python3
"""
WebSocket Interfaces for Web Agents
Phase 4 Step 3: WebSocket real-time communication for web-based embodiment
"""

import asyncio
import json
import logging
import ssl
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid
import weakref

# Try to import websockets, fall back to mock if not available
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    from websockets.exceptions import ConnectionClosed, WebSocketException
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("WebSockets library not available, using mock implementations")
    WEBSOCKETS_AVAILABLE = False
    
    # Mock websockets classes
    class WebSocketServerProtocol:
        def __init__(self):
            self.id = str(uuid.uuid4())
            self.remote_address = ('127.0.0.1', 8000)
        
        async def send(self, message):
            logger.info(f"Mock WebSocket send: {message}")
        
        async def recv(self):
            await asyncio.sleep(1)
            return '{"type": "mock", "data": "test"}'
        
        async def close(self):
            pass
    
    class ConnectionClosed(Exception):
        pass
    
    class WebSocketException(Exception):
        pass
    
    class websockets:
        @staticmethod
        def serve(handler, host, port, ssl_context=None):
            return MockWebSocketServer(handler, host, port)
    
    class MockWebSocketServer:
        def __init__(self, handler, host, port):
            self.handler = handler
            self.host = host
            self.port = port
        
        async def __aenter__(self):
            logger.info(f"Mock WebSocket server started on {self.host}:{self.port}")
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            logger.info("Mock WebSocket server stopped")

logger = logging.getLogger(__name__)

class WebSocketMessageType(Enum):
    """WebSocket message types for web agent communication"""
    COGNITIVE_STATE = "cognitive_state"
    USER_INPUT = "user_input"
    AGENT_RESPONSE = "agent_response"
    SENSOR_DATA = "sensor_data"
    ACTION_COMMAND = "action_command"
    REGISTRATION = "registration"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    ENVIRONMENT_UPDATE = "environment_update"

@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    message_type: WebSocketMessageType
    timestamp: float
    client_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class WebSocketClient:
    """WebSocket client information"""
    client_id: str
    websocket: Any  # WebSocketServerProtocol
    user_agent: str
    ip_address: str
    connected_at: datetime
    last_heartbeat: datetime
    agent_data: Dict[str, Any]
    subscriptions: Set[str]

class WebSocketInterface:
    """WebSocket interface for web-based cognitive agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8765)
        self.ssl_enabled = config.get('ssl_enabled', False)
        self.ssl_cert = config.get('ssl_cert', None)
        self.ssl_key = config.get('ssl_key', None)
        
        self.server = None
        self.clients: Dict[str, WebSocketClient] = {}
        self.message_handlers: Dict[WebSocketMessageType, Callable] = {}
        self.cognitive_state = {}
        self.subscription_topics = set()
        
        self.running = False
        self.max_connections = config.get('max_connections', 1000)
        self.heartbeat_interval = config.get('heartbeat_interval', 30)
        self.message_rate_limit = config.get('message_rate_limit', 100)  # messages per minute
        
        # Register default message handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        self.message_handlers[WebSocketMessageType.REGISTRATION] = self._handle_registration
        self.message_handlers[WebSocketMessageType.HEARTBEAT] = self._handle_heartbeat
        self.message_handlers[WebSocketMessageType.USER_INPUT] = self._handle_user_input
        self.message_handlers[WebSocketMessageType.SENSOR_DATA] = self._handle_sensor_data
        self.message_handlers[WebSocketMessageType.ACTION_COMMAND] = self._handle_action_command
    
    async def initialize(self) -> bool:
        """Initialize WebSocket interface"""
        try:
            # Set up SSL context if enabled
            ssl_context = None
            if self.ssl_enabled and self.ssl_cert and self.ssl_key:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(self.ssl_cert, self.ssl_key)
            
            logger.info(f"WebSocket interface configured for {self.host}:{self.port}")
            if self.ssl_enabled:
                logger.info("SSL/TLS encryption enabled")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket interface: {e}")
            return False
    
    async def start(self):
        """Start WebSocket server"""
        self.running = True
        
        try:
            # Create SSL context if needed
            ssl_context = None
            if self.ssl_enabled and self.ssl_cert and self.ssl_key:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(self.ssl_cert, self.ssl_key)
            
            # Start WebSocket server
            if WEBSOCKETS_AVAILABLE:
                self.server = await websockets.serve(
                    self._handle_client,
                    self.host,
                    self.port,
                    ssl=ssl_context,
                    max_size=None,  # Remove message size limit
                    max_queue=None  # Remove queue size limit
                )
            else:
                self.server = await websockets.serve(
                    self._handle_client,
                    self.host,
                    self.port,
                    ssl_context=ssl_context
                )
            
            # Start background tasks
            heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            cleanup_task = asyncio.create_task(self._cleanup_stale_clients())
            
            logger.info(f"WebSocket server started on {self.host}:{self.port}")
            
            # Keep server running
            await asyncio.gather(heartbeat_task, cleanup_task)
            
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")
            self.running = False
    
    async def stop(self):
        """Stop WebSocket server"""
        self.running = False
        
        # Close all client connections
        for client_id, client in list(self.clients.items()):
            try:
                await client.websocket.close()
            except:
                pass
        
        self.clients.clear()
        
        # Close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("WebSocket server stopped")
    
    async def _handle_client(self, websocket, path):
        """Handle new WebSocket client connection"""
        client_id = str(uuid.uuid4())
        
        try:
            # Check connection limit
            if len(self.clients) >= self.max_connections:
                await websocket.close(code=1013, reason="Server at capacity")
                return
            
            # Create client object
            remote_addr = websocket.remote_address if hasattr(websocket, 'remote_address') else ('unknown', 0)
            user_agent = websocket.request_headers.get('User-Agent', 'Unknown') if hasattr(websocket, 'request_headers') else 'Unknown'
            
            client = WebSocketClient(
                client_id=client_id,
                websocket=websocket,
                user_agent=user_agent,
                ip_address=remote_addr[0],
                connected_at=datetime.now(),
                last_heartbeat=datetime.now(),
                agent_data={},
                subscriptions=set()
            )
            
            self.clients[client_id] = client
            
            logger.info(f"WebSocket client connected: {client_id} from {remote_addr[0]}")
            
            # Send welcome message
            welcome_msg = WebSocketMessage(
                message_type=WebSocketMessageType.REGISTRATION,
                timestamp=datetime.now().timestamp(),
                client_id=client_id,
                data={
                    'status': 'connected',
                    'server_capabilities': self._get_server_capabilities(),
                    'client_id': client_id
                },
                metadata={}
            )
            await self._send_message(client_id, welcome_msg)
            
            # Handle client messages
            async for message in websocket:
                try:
                    parsed_message = json.loads(message)
                    await self._process_message(client_id, parsed_message)
                except json.JSONDecodeError as e:
                    error_msg = WebSocketMessage(
                        message_type=WebSocketMessageType.ERROR,
                        timestamp=datetime.now().timestamp(),
                        client_id=client_id,
                        data={'error': 'Invalid JSON', 'details': str(e)},
                        metadata={}
                    )
                    await self._send_message(client_id, error_msg)
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")
        
        except ConnectionClosed:
            logger.info(f"WebSocket client disconnected: {client_id}")
        except WebSocketException as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error handling client {client_id}: {e}")
        finally:
            # Clean up client
            if client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"Cleaned up client: {client_id}")
    
    async def _process_message(self, client_id: str, message_data: Dict[str, Any]):
        """Process incoming message from WebSocket client"""
        try:
            # Parse message
            message_type_str = message_data.get('type')
            if not message_type_str:
                logger.error(f"Message from {client_id} missing type field")
                return
            
            try:
                message_type = WebSocketMessageType(message_type_str)
            except ValueError:
                logger.error(f"Unknown message type from {client_id}: {message_type_str}")
                return
            
            # Create message object
            message = WebSocketMessage(
                message_type=message_type,
                timestamp=message_data.get('timestamp', datetime.now().timestamp()),
                client_id=client_id,
                data=message_data.get('data', {}),
                metadata=message_data.get('metadata', {})
            )
            
            # Update client heartbeat
            if client_id in self.clients:
                self.clients[client_id].last_heartbeat = datetime.now()
            
            # Handle message
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](client_id, message)
            else:
                logger.warning(f"No handler for message type {message_type} from {client_id}")
                
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
    
    async def _handle_registration(self, client_id: str, message: WebSocketMessage):
        """Handle client registration"""
        try:
            agent_data = message.data.get('agent_data', {})
            subscriptions = set(message.data.get('subscriptions', []))
            
            if client_id in self.clients:
                client = self.clients[client_id]
                client.agent_data = agent_data
                client.subscriptions = subscriptions
                
                # Add to subscription topics
                self.subscription_topics.update(subscriptions)
            
            # Send registration confirmation
            response = WebSocketMessage(
                message_type=WebSocketMessageType.REGISTRATION,
                timestamp=datetime.now().timestamp(),
                client_id=client_id,
                data={
                    'status': 'registered',
                    'subscriptions_confirmed': list(subscriptions),
                    'cognitive_state': self.cognitive_state.get(client_id, {})
                },
                metadata={}
            )
            
            await self._send_message(client_id, response)
            
        except Exception as e:
            logger.error(f"Error handling registration from {client_id}: {e}")
    
    async def _handle_heartbeat(self, client_id: str, message: WebSocketMessage):
        """Handle heartbeat message"""
        # Heartbeat is already handled by updating last_heartbeat in _process_message
        response = WebSocketMessage(
            message_type=WebSocketMessageType.HEARTBEAT,
            timestamp=datetime.now().timestamp(),
            client_id=client_id,
            data={'status': 'alive'},
            metadata={}
        )
        
        await self._send_message(client_id, response)
    
    async def _handle_user_input(self, client_id: str, message: WebSocketMessage):
        """Handle user input from web client"""
        try:
            user_input = message.data.get('input', '')
            input_type = message.data.get('input_type', 'text')
            context = message.data.get('context', {})
            
            # Process user input through cognitive system
            # This would integrate with the main cognitive framework
            
            # For now, echo back with processing indication
            response = WebSocketMessage(
                message_type=WebSocketMessageType.AGENT_RESPONSE,
                timestamp=datetime.now().timestamp(),
                client_id=client_id,
                data={
                    'response': f"Processed: {user_input}",
                    'response_type': 'text',
                    'processing_time': 0.1,
                    'confidence': 0.8
                },
                metadata={'original_input': user_input}
            )
            
            await self._send_message(client_id, response)
            
        except Exception as e:
            logger.error(f"Error handling user input from {client_id}: {e}")
    
    async def _handle_sensor_data(self, client_id: str, message: WebSocketMessage):
        """Handle sensor data from web client"""
        try:
            sensor_data = message.data.get('sensor_data', {})
            sensor_type = message.data.get('sensor_type', 'unknown')
            
            # Update cognitive state with sensor data
            if client_id not in self.cognitive_state:
                self.cognitive_state[client_id] = {}
            
            if 'sensors' not in self.cognitive_state[client_id]:
                self.cognitive_state[client_id]['sensors'] = {}
            
            self.cognitive_state[client_id]['sensors'][sensor_type] = {
                'timestamp': message.timestamp,
                'data': sensor_data,
                'metadata': message.metadata
            }
            
            self.cognitive_state[client_id]['last_update'] = datetime.now().timestamp()
            
        except Exception as e:
            logger.error(f"Error handling sensor data from {client_id}: {e}")
    
    async def _handle_action_command(self, client_id: str, message: WebSocketMessage):
        """Handle action command from web client"""
        try:
            action_type = message.data.get('action_type', 'unknown')
            parameters = message.data.get('parameters', {})
            
            # Process action command
            # This would integrate with the action execution system
            
            # Send acknowledgment
            response = WebSocketMessage(
                message_type=WebSocketMessageType.ACTION_COMMAND,
                timestamp=datetime.now().timestamp(),
                client_id=client_id,
                data={
                    'status': 'executed',
                    'action_type': action_type,
                    'result': 'success'
                },
                metadata={}
            )
            
            await self._send_message(client_id, response)
            
        except Exception as e:
            logger.error(f"Error handling action command from {client_id}: {e}")
    
    async def _send_message(self, client_id: str, message: WebSocketMessage) -> bool:
        """Send message to WebSocket client"""
        if client_id not in self.clients:
            logger.error(f"Client {client_id} not connected")
            return False
        
        try:
            client = self.clients[client_id]
            message_data = {
                'type': message.message_type.value,
                'timestamp': message.timestamp,
                'client_id': message.client_id,
                'data': message.data,
                'metadata': message.metadata
            }
            
            await client.websocket.send(json.dumps(message_data))
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {client_id}: {e}")
            return False
    
    async def broadcast_message(self, message: WebSocketMessage, topic: Optional[str] = None) -> List[str]:
        """Broadcast message to all or subscribed clients"""
        sent_to = []
        
        for client_id, client in list(self.clients.items()):
            try:
                # Check if client is subscribed to topic (if specified)
                if topic is None or topic in client.subscriptions:
                    success = await self._send_message(client_id, message)
                    if success:
                        sent_to.append(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
        
        return sent_to
    
    async def send_cognitive_state_update(self, client_id: str, state_data: Dict[str, Any]) -> bool:
        """Send cognitive state update to specific client"""
        message = WebSocketMessage(
            message_type=WebSocketMessageType.COGNITIVE_STATE,
            timestamp=datetime.now().timestamp(),
            client_id=client_id,
            data={'cognitive_state': state_data},
            metadata={}
        )
        
        return await self._send_message(client_id, message)
    
    async def broadcast_cognitive_state(self, state_data: Dict[str, Any]) -> List[str]:
        """Broadcast cognitive state to all subscribed clients"""
        message = WebSocketMessage(
            message_type=WebSocketMessageType.COGNITIVE_STATE,
            timestamp=datetime.now().timestamp(),
            client_id="server",
            data={'cognitive_state': state_data},
            metadata={}
        )
        
        return await self.broadcast_message(message, "cognitive_state")
    
    async def _heartbeat_monitor(self):
        """Monitor client heartbeats and send server heartbeats"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Send heartbeat to all clients
                heartbeat_msg = WebSocketMessage(
                    message_type=WebSocketMessageType.HEARTBEAT,
                    timestamp=current_time.timestamp(),
                    client_id="server",
                    data={'status': 'alive', 'clients_connected': len(self.clients)},
                    metadata={}
                )
                
                await self.broadcast_message(heartbeat_msg)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _cleanup_stale_clients(self):
        """Clean up stale client connections"""
        while self.running:
            try:
                current_time = datetime.now()
                timeout_seconds = self.heartbeat_interval * 3  # 3x heartbeat interval
                
                stale_clients = []
                for client_id, client in self.clients.items():
                    time_since_heartbeat = (current_time - client.last_heartbeat).total_seconds()
                    if time_since_heartbeat > timeout_seconds:
                        stale_clients.append(client_id)
                
                # Remove stale clients
                for client_id in stale_clients:
                    logger.warning(f"Removing stale WebSocket client: {client_id}")
                    try:
                        await self.clients[client_id].websocket.close()
                    except:
                        pass
                    del self.clients[client_id]
                    
                    # Remove from cognitive state
                    if client_id in self.cognitive_state:
                        del self.cognitive_state[client_id]
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in cleanup monitor: {e}")
                await asyncio.sleep(60)
    
    def _get_server_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities for client registration"""
        return {
            'message_types': [mt.value for mt in WebSocketMessageType],
            'max_connections': self.max_connections,
            'heartbeat_interval': self.heartbeat_interval,
            'ssl_enabled': self.ssl_enabled,
            'subscription_topics': list(self.subscription_topics)
        }
    
    def get_cognitive_state(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current cognitive state"""
        if client_id:
            return self.cognitive_state.get(client_id, {})
        return self.cognitive_state
    
    def get_connected_clients(self) -> List[Dict[str, Any]]:
        """Get information about connected clients"""
        client_info = []
        for client_id, client in self.clients.items():
            client_info.append({
                'client_id': client_id,
                'user_agent': client.user_agent,
                'ip_address': client.ip_address,
                'connected_at': client.connected_at.isoformat(),
                'last_heartbeat': client.last_heartbeat.isoformat(),
                'subscriptions': list(client.subscriptions),
                'agent_data': client.agent_data
            })
        return client_info
    
    def register_message_handler(self, message_type: WebSocketMessageType, handler_func: Callable):
        """Register custom message handler"""
        self.message_handlers[message_type] = handler_func


class WebSocketServer:
    """High-level WebSocket server for web agent integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.interface = WebSocketInterface(config)
        self.cognitive_integration = None
        
    async def initialize(self, cognitive_framework=None) -> bool:
        """Initialize WebSocket server with optional cognitive framework integration"""
        self.cognitive_integration = cognitive_framework
        return await self.interface.initialize()
    
    async def start(self):
        """Start WebSocket server"""
        await self.interface.start()
    
    async def stop(self):
        """Stop WebSocket server"""
        await self.interface.stop()
    
    async def send_to_client(self, client_id: str, message_type: str, data: Dict[str, Any]) -> bool:
        """Send message to specific client"""
        try:
            msg_type = WebSocketMessageType(message_type)
            message = WebSocketMessage(
                message_type=msg_type,
                timestamp=datetime.now().timestamp(),
                client_id=client_id,
                data=data,
                metadata={}
            )
            return await self.interface._send_message(client_id, message)
        except ValueError:
            logger.error(f"Invalid message type: {message_type}")
            return False
    
    async def broadcast_to_clients(self, message_type: str, data: Dict[str, Any], topic: Optional[str] = None) -> List[str]:
        """Broadcast message to all or subscribed clients"""
        try:
            msg_type = WebSocketMessageType(message_type)
            message = WebSocketMessage(
                message_type=msg_type,
                timestamp=datetime.now().timestamp(),
                client_id="server",
                data=data,
                metadata={}
            )
            return await self.interface.broadcast_message(message, topic)
        except ValueError:
            logger.error(f"Invalid message type: {message_type}")
            return []
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get WebSocket server statistics"""
        return {
            'connected_clients': len(self.interface.clients),
            'max_connections': self.interface.max_connections,
            'subscription_topics': list(self.interface.subscription_topics),
            'uptime': datetime.now().isoformat(),
            'ssl_enabled': self.interface.ssl_enabled
        }
    
    def register_custom_handler(self, message_type: str, handler_func: Callable):
        """Register custom message handler"""
        try:
            msg_type = WebSocketMessageType(message_type)
            self.interface.register_message_handler(msg_type, handler_func)
        except ValueError:
            logger.error(f"Invalid message type: {message_type}")