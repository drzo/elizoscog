#!/usr/bin/env python3
"""
Unity3D Cognitive Interface Bindings
Phase 4 Step 1: Unity3D integration with bi-directional data flow
"""

import asyncio
import json
import logging
import socket
import struct
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Unity3DMessageType(Enum):
    """Message types for Unity3D communication"""
    COGNITIVE_STATE = "cognitive_state"
    SENSOR_DATA = "sensor_data"
    ACTION_COMMAND = "action_command"
    ENVIRONMENT_STATE = "environment_state"
    AGENT_REGISTRATION = "agent_registration"
    HEARTBEAT = "heartbeat"

@dataclass
class Unity3DSensorData:
    """Unity3D sensor data structure"""
    timestamp: float
    agent_id: str
    sensor_type: str
    position: Dict[str, float]
    rotation: Dict[str, float]
    velocity: Dict[str, float]
    raw_data: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class Unity3DActionCommand:
    """Unity3D action command structure"""
    timestamp: float
    agent_id: str
    action_type: str
    parameters: Dict[str, Any]
    priority: int
    timeout: float

class Unity3DInterface:
    """Unity3D cognitive interface with bi-directional communication"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 12345)
        self.buffer_size = config.get('buffer_size', 8192)
        
        self.server_socket = None
        self.client_connections = {}
        self.message_handlers = {}
        self.sensor_manager = None
        
        self.running = False
        self.cognitive_state = {}
        
        # Register default message handlers
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Register default message type handlers"""
        self.message_handlers[Unity3DMessageType.SENSOR_DATA] = self._handle_sensor_data
        self.message_handlers[Unity3DMessageType.AGENT_REGISTRATION] = self._handle_agent_registration
        self.message_handlers[Unity3DMessageType.HEARTBEAT] = self._handle_heartbeat
        self.message_handlers[Unity3DMessageType.ENVIRONMENT_STATE] = self._handle_environment_state
    
    async def initialize(self) -> bool:
        """Initialize Unity3D interface"""
        try:
            # Create sensor manager
            self.sensor_manager = Unity3DSensorManager(self.config)
            await self.sensor_manager.initialize()
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.server_socket.setblocking(False)
            
            logger.info(f"Unity3D interface listening on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Unity3D interface: {e}")
            return False
    
    async def start(self):
        """Start Unity3D interface server"""
        self.running = True
        
        # Start accepting connections
        accept_task = asyncio.create_task(self._accept_connections())
        
        # Start periodic tasks
        heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        
        await asyncio.gather(accept_task, heartbeat_task)
    
    async def stop(self):
        """Stop Unity3D interface server"""
        self.running = False
        
        # Close all client connections
        for client_id, client_data in self.client_connections.items():
            try:
                client_data['socket'].close()
            except:
                pass
        
        self.client_connections.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
    
    async def _accept_connections(self):
        """Accept incoming Unity3D connections"""
        while self.running:
            try:
                # Use asyncio-compatible socket operations
                loop = asyncio.get_event_loop()
                client_socket, addr = await loop.sock_accept(self.server_socket)
                
                client_id = f"unity3d_{addr[0]}_{addr[1]}_{datetime.now().timestamp()}"
                
                self.client_connections[client_id] = {
                    'socket': client_socket,
                    'address': addr,
                    'last_heartbeat': datetime.now(),
                    'agent_data': {}
                }
                
                # Start handling this client
                asyncio.create_task(self._handle_client(client_id))
                
                logger.info(f"Unity3D client connected: {client_id} from {addr}")
                
            except Exception as e:
                if self.running:  # Only log if we're still supposed to be running
                    logger.error(f"Error accepting Unity3D connection: {e}")
                await asyncio.sleep(0.1)
    
    async def _handle_client(self, client_id: str):
        """Handle messages from a Unity3D client"""
        client_data = self.client_connections[client_id]
        client_socket = client_data['socket']
        
        try:
            while self.running and client_id in self.client_connections:
                # Read message length
                loop = asyncio.get_event_loop()
                length_data = await loop.sock_recv(client_socket, 4)
                
                if len(length_data) != 4:
                    break
                
                message_length = struct.unpack('!I', length_data)[0]
                
                # Read message data
                message_data = b''
                while len(message_data) < message_length:
                    chunk = await loop.sock_recv(client_socket, min(message_length - len(message_data), self.buffer_size))
                    if not chunk:
                        break
                    message_data += chunk
                
                if len(message_data) == message_length:
                    try:
                        message = json.loads(message_data.decode('utf-8'))
                        await self._process_message(client_id, message)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from Unity3D client {client_id}: {e}")
                
        except Exception as e:
            logger.error(f"Error handling Unity3D client {client_id}: {e}")
        finally:
            # Clean up client connection
            try:
                client_socket.close()
            except:
                pass
            if client_id in self.client_connections:
                del self.client_connections[client_id]
            logger.info(f"Unity3D client disconnected: {client_id}")
    
    async def _process_message(self, client_id: str, message: Dict[str, Any]):
        """Process message from Unity3D client"""
        try:
            message_type_str = message.get('type')
            if not message_type_str:
                logger.error(f"Message from {client_id} missing type field")
                return
            
            try:
                message_type = Unity3DMessageType(message_type_str)
            except ValueError:
                logger.error(f"Unknown message type from {client_id}: {message_type_str}")
                return
            
            # Update last activity
            self.client_connections[client_id]['last_heartbeat'] = datetime.now()
            
            # Handle message
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](client_id, message)
            else:
                logger.warning(f"No handler for message type {message_type} from {client_id}")
                
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
    
    async def _handle_sensor_data(self, client_id: str, message: Dict[str, Any]):
        """Handle sensor data from Unity3D"""
        try:
            sensor_data = Unity3DSensorData(
                timestamp=message.get('timestamp', datetime.now().timestamp()),
                agent_id=message.get('agent_id', client_id),
                sensor_type=message.get('sensor_type', 'unknown'),
                position=message.get('position', {'x': 0, 'y': 0, 'z': 0}),
                rotation=message.get('rotation', {'x': 0, 'y': 0, 'z': 0, 'w': 1}),
                velocity=message.get('velocity', {'x': 0, 'y': 0, 'z': 0}),
                raw_data=message.get('data', {}),
                metadata=message.get('metadata', {})
            )
            
            # Process with sensor manager
            await self.sensor_manager.process_sensor_data(sensor_data)
            
            # Update cognitive state
            await self._update_cognitive_state(client_id, sensor_data)
            
        except Exception as e:
            logger.error(f"Error handling sensor data from {client_id}: {e}")
    
    async def _handle_agent_registration(self, client_id: str, message: Dict[str, Any]):
        """Handle agent registration from Unity3D"""
        try:
            agent_data = message.get('agent_data', {})
            self.client_connections[client_id]['agent_data'] = agent_data
            
            # Send registration confirmation
            response = {
                'type': 'registration_confirmed',
                'client_id': client_id,
                'timestamp': datetime.now().timestamp(),
                'cognitive_state': self.cognitive_state.get(client_id, {})
            }
            
            await self._send_message(client_id, response)
            
        except Exception as e:
            logger.error(f"Error handling agent registration from {client_id}: {e}")
    
    async def _handle_heartbeat(self, client_id: str, message: Dict[str, Any]):
        """Handle heartbeat from Unity3D"""
        # Heartbeat is already handled by updating last_heartbeat in _process_message
        pass
    
    async def _handle_environment_state(self, client_id: str, message: Dict[str, Any]):
        """Handle environment state update from Unity3D"""
        try:
            env_state = message.get('environment_state', {})
            
            # Store environment state
            if 'environment_states' not in self.cognitive_state:
                self.cognitive_state['environment_states'] = {}
            
            self.cognitive_state['environment_states'][client_id] = {
                'timestamp': datetime.now().timestamp(),
                'state': env_state
            }
            
        except Exception as e:
            logger.error(f"Error handling environment state from {client_id}: {e}")
    
    async def _update_cognitive_state(self, client_id: str, sensor_data: Unity3DSensorData):
        """Update cognitive state based on sensor data"""
        if client_id not in self.cognitive_state:
            self.cognitive_state[client_id] = {
                'agent_id': sensor_data.agent_id,
                'position': sensor_data.position,
                'rotation': sensor_data.rotation,
                'velocity': sensor_data.velocity,
                'sensors': {},
                'last_update': sensor_data.timestamp
            }
        
        # Update agent state
        state = self.cognitive_state[client_id]
        state['position'] = sensor_data.position
        state['rotation'] = sensor_data.rotation
        state['velocity'] = sensor_data.velocity
        state['last_update'] = sensor_data.timestamp
        
        # Update sensor data
        state['sensors'][sensor_data.sensor_type] = {
            'timestamp': sensor_data.timestamp,
            'data': sensor_data.raw_data,
            'metadata': sensor_data.metadata
        }
    
    async def _send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to Unity3D client"""
        if client_id not in self.client_connections:
            logger.error(f"Client {client_id} not connected")
            return False
        
        try:
            client_socket = self.client_connections[client_id]['socket']
            
            # Serialize message
            message_data = json.dumps(message).encode('utf-8')
            message_length = struct.pack('!I', len(message_data))
            
            # Send message
            loop = asyncio.get_event_loop()
            await loop.sock_sendall(client_socket, message_length + message_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {client_id}: {e}")
            return False
    
    async def send_action_command(self, client_id: str, command: Unity3DActionCommand) -> bool:
        """Send action command to Unity3D client"""
        message = {
            'type': Unity3DMessageType.ACTION_COMMAND.value,
            'timestamp': command.timestamp,
            'agent_id': command.agent_id,
            'action_type': command.action_type,
            'parameters': command.parameters,
            'priority': command.priority,
            'timeout': command.timeout
        }
        
        return await self._send_message(client_id, message)
    
    async def broadcast_cognitive_state(self, state_data: Dict[str, Any]):
        """Broadcast cognitive state to all Unity3D clients"""
        message = {
            'type': Unity3DMessageType.COGNITIVE_STATE.value,
            'timestamp': datetime.now().timestamp(),
            'cognitive_state': state_data
        }
        
        results = []
        for client_id in list(self.client_connections.keys()):
            result = await self._send_message(client_id, message)
            results.append(result)
        
        return all(results)
    
    async def _heartbeat_monitor(self):
        """Monitor client heartbeats and cleanup stale connections"""
        while self.running:
            try:
                current_time = datetime.now()
                timeout_seconds = self.config.get('heartbeat_timeout', 30)
                
                stale_clients = []
                for client_id, client_data in self.client_connections.items():
                    time_since_heartbeat = (current_time - client_data['last_heartbeat']).total_seconds()
                    if time_since_heartbeat > timeout_seconds:
                        stale_clients.append(client_id)
                
                # Remove stale clients
                for client_id in stale_clients:
                    logger.warning(f"Removing stale Unity3D client: {client_id}")
                    try:
                        self.client_connections[client_id]['socket'].close()
                    except:
                        pass
                    del self.client_connections[client_id]
                    
                    # Remove from cognitive state
                    if client_id in self.cognitive_state:
                        del self.cognitive_state[client_id]
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(10)
    
    def get_cognitive_state(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current cognitive state"""
        if client_id:
            return self.cognitive_state.get(client_id, {})
        return self.cognitive_state
    
    def get_connected_clients(self) -> List[str]:
        """Get list of connected Unity3D clients"""
        return list(self.client_connections.keys())


class Unity3DSensorManager:
    """Manager for Unity3D sensor data processing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sensor_processors = {}
        self.sensor_data_buffer = {}
        self.fusion_algorithms = {}
    
    async def initialize(self) -> bool:
        """Initialize sensor manager"""
        try:
            # Initialize default sensor processors
            self._register_default_processors()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Unity3D sensor manager: {e}")
            return False
    
    def _register_default_processors(self):
        """Register default sensor processors"""
        self.sensor_processors['camera'] = self._process_camera_data
        self.sensor_processors['lidar'] = self._process_lidar_data
        self.sensor_processors['imu'] = self._process_imu_data
        self.sensor_processors['gps'] = self._process_gps_data
        self.sensor_processors['audio'] = self._process_audio_data
    
    async def process_sensor_data(self, sensor_data: Unity3DSensorData):
        """Process incoming sensor data"""
        try:
            # Buffer sensor data
            agent_id = sensor_data.agent_id
            if agent_id not in self.sensor_data_buffer:
                self.sensor_data_buffer[agent_id] = {}
            
            self.sensor_data_buffer[agent_id][sensor_data.sensor_type] = sensor_data
            
            # Process with specific processor
            if sensor_data.sensor_type in self.sensor_processors:
                await self.sensor_processors[sensor_data.sensor_type](sensor_data)
            
            # Perform sensor fusion if multiple sensors available
            await self._perform_sensor_fusion(agent_id)
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
    
    async def _process_camera_data(self, sensor_data: Unity3DSensorData):
        """Process camera sensor data"""
        # Extract visual features, object detection, etc.
        pass
    
    async def _process_lidar_data(self, sensor_data: Unity3DSensorData):
        """Process LiDAR sensor data"""
        # Process point cloud data, obstacle detection, etc.
        pass
    
    async def _process_imu_data(self, sensor_data: Unity3DSensorData):
        """Process IMU sensor data"""
        # Process acceleration, gyroscope, magnetometer data
        pass
    
    async def _process_gps_data(self, sensor_data: Unity3DSensorData):
        """Process GPS sensor data"""
        # Process location data, coordinate transforms, etc.
        pass
    
    async def _process_audio_data(self, sensor_data: Unity3DSensorData):
        """Process audio sensor data"""
        # Process audio features, speech recognition, etc.
        pass
    
    async def _perform_sensor_fusion(self, agent_id: str):
        """Perform multi-modal sensor fusion for an agent"""
        if agent_id not in self.sensor_data_buffer:
            return
        
        sensor_data = self.sensor_data_buffer[agent_id]
        
        # Implement basic sensor fusion algorithms
        # This would typically involve Kalman filtering, particle filters, etc.
        
        fused_state = {
            'timestamp': datetime.now().timestamp(),
            'agent_id': agent_id,
            'position_confidence': 0.0,
            'orientation_confidence': 0.0,
            'velocity_confidence': 0.0,
            'environment_features': {}
        }
        
        # Calculate confidence and fused estimates
        # This is a simplified implementation
        if 'gps' in sensor_data and 'imu' in sensor_data:
            fused_state['position_confidence'] = 0.8
            fused_state['velocity_confidence'] = 0.7
        
        if 'imu' in sensor_data:
            fused_state['orientation_confidence'] = 0.9
        
        if 'camera' in sensor_data and 'lidar' in sensor_data:
            fused_state['environment_features']['obstacles'] = True
            fused_state['environment_features']['landmarks'] = True
        
        # Store fused state
        self.sensor_data_buffer[agent_id]['_fused'] = fused_state
    
    def get_sensor_data(self, agent_id: str, sensor_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get sensor data for an agent"""
        if agent_id not in self.sensor_data_buffer:
            return None
        
        if sensor_type:
            return self.sensor_data_buffer[agent_id].get(sensor_type)
        
        return self.sensor_data_buffer[agent_id]
    
    def register_sensor_processor(self, sensor_type: str, processor_func: Callable):
        """Register custom sensor processor"""
        self.sensor_processors[sensor_type] = processor_func
    
    def register_fusion_algorithm(self, name: str, algorithm_func: Callable):
        """Register custom sensor fusion algorithm"""
        self.fusion_algorithms[name] = algorithm_func