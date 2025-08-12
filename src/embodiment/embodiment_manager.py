#!/usr/bin/env python3
"""
Embodiment Manager - Coordination and State Management
Phase 4 Step 6: Multi-platform embodiment synchronization and state management
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .unity_bindings import Unity3DInterface, Unity3DSensorData, Unity3DActionCommand
from .ros_bindings import ROSInterface, ROSSensorData, ROSMotionCommand
from .websocket_bindings import WebSocketInterface, WebSocketMessage, WebSocketMessageType

logger = logging.getLogger(__name__)

class EmbodimentPlatform(Enum):
    """Supported embodiment platforms"""
    UNITY3D = "unity3d"
    ROS = "ros"
    WEBSOCKET = "websocket"

class EmbodimentState(Enum):
    """Embodiment state types"""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    SYNCHRONIZING = "synchronizing"

@dataclass
class AgentState:
    """Agent state across all platforms"""
    agent_id: str
    platforms: Set[EmbodimentPlatform]
    position: Dict[str, float]
    orientation: Dict[str, float]
    velocity: Dict[str, float]
    cognitive_state: Dict[str, Any]
    sensor_data: Dict[str, Any]
    last_update: float
    status: EmbodimentState

@dataclass
class SensorFusionResult:
    """Result of multi-modal sensor fusion"""
    timestamp: float
    confidence_scores: Dict[str, float]
    fused_position: Dict[str, float]
    fused_orientation: Dict[str, float]
    fused_velocity: Dict[str, float]
    environment_features: Dict[str, Any]
    anomalies: List[str]

@dataclass
class ActionSynchronization:
    """Synchronized action across platforms"""
    action_id: str
    timestamp: float
    platforms: Set[EmbodimentPlatform]
    action_type: str
    parameters: Dict[str, Any]
    status: str
    results: Dict[EmbodimentPlatform, Any]

class EmbodimentManager:
    """Central manager for multi-platform embodiment coordination"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, AgentState] = {}
        self.platform_interfaces: Dict[EmbodimentPlatform, Any] = {}
        
        # Sensor fusion and synchronization
        self.sensor_fusion_algorithms = {}
        self.synchronization_buffer = {}
        self.action_queue = {}
        
        # State management
        self.global_cognitive_state = {}
        self.platform_states = {}
        self.sync_handlers = {}
        
        # Monitoring and performance
        self.performance_metrics = {}
        self.error_counts = {}
        self.last_sync_times = {}
        
        self.running = False
        self.sync_interval = config.get('sync_interval', 0.1)  # 10 Hz synchronization
        self.max_sync_delay = config.get('max_sync_delay', 0.5)  # Maximum acceptable delay
        
    async def initialize(self) -> bool:
        """Initialize embodiment manager and all platform interfaces"""
        try:
            # Initialize platform interfaces
            await self._initialize_platform_interfaces()
            
            # Register default fusion algorithms
            self._register_default_fusion_algorithms()
            
            # Register default synchronization handlers
            self._register_default_sync_handlers()
            
            logger.info("Embodiment manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize embodiment manager: {e}")
            return False
    
    async def _initialize_platform_interfaces(self):
        """Initialize all configured platform interfaces"""
        # Initialize Unity3D interface
        if self.config.get('unity3d', {}).get('enabled', False):
            unity_config = self.config['unity3d']
            unity_interface = Unity3DInterface(unity_config)
            
            if await unity_interface.initialize():
                self.platform_interfaces[EmbodimentPlatform.UNITY3D] = unity_interface
                self.platform_states[EmbodimentPlatform.UNITY3D] = EmbodimentState.ACTIVE
                logger.info("Unity3D interface initialized")
            else:
                logger.error("Failed to initialize Unity3D interface")
        
        # Initialize ROS interface
        if self.config.get('ros', {}).get('enabled', False):
            ros_config = self.config['ros']
            ros_interface = ROSInterface(ros_config)
            
            if await ros_interface.initialize():
                self.platform_interfaces[EmbodimentPlatform.ROS] = ros_interface
                self.platform_states[EmbodimentPlatform.ROS] = EmbodimentState.ACTIVE
                logger.info("ROS interface initialized")
            else:
                logger.error("Failed to initialize ROS interface")
        
        # Initialize WebSocket interface
        if self.config.get('websocket', {}).get('enabled', False):
            websocket_config = self.config['websocket']
            websocket_interface = WebSocketInterface(websocket_config)
            
            if await websocket_interface.initialize():
                self.platform_interfaces[EmbodimentPlatform.WEBSOCKET] = websocket_interface
                self.platform_states[EmbodimentPlatform.WEBSOCKET] = EmbodimentState.ACTIVE
                logger.info("WebSocket interface initialized")
            else:
                logger.error("Failed to initialize WebSocket interface")
    
    def _register_default_fusion_algorithms(self):
        """Register default sensor fusion algorithms"""
        self.sensor_fusion_algorithms['position'] = self._fuse_position_data
        self.sensor_fusion_algorithms['orientation'] = self._fuse_orientation_data
        self.sensor_fusion_algorithms['velocity'] = self._fuse_velocity_data
        self.sensor_fusion_algorithms['environment'] = self._fuse_environment_data
    
    def _register_default_sync_handlers(self):
        """Register default synchronization handlers"""
        self.sync_handlers['cognitive_state'] = self._sync_cognitive_state_handler
        self.sync_handlers['sensor_data'] = self._sync_sensor_data_handler  
        self.sync_handlers['actions'] = self._sync_actions_handler
        self.sync_handlers['environment'] = self._sync_environment_state_handler
    
    async def _sync_cognitive_state_handler(self, data):
        """Default cognitive state synchronization handler"""
        pass
    
    async def _sync_sensor_data_handler(self, data):
        """Default sensor data synchronization handler"""
        pass
    
    async def _sync_actions_handler(self, data):
        """Default actions synchronization handler"""
        pass
    
    async def _sync_environment_state_handler(self, data):
        """Default environment state synchronization handler"""
        pass
    
    async def start(self):
        """Start embodiment manager and all platform interfaces"""
        self.running = True
        
        # Start platform interfaces
        platform_tasks = []
        
        if EmbodimentPlatform.UNITY3D in self.platform_interfaces:
            platform_tasks.append(
                asyncio.create_task(self.platform_interfaces[EmbodimentPlatform.UNITY3D].start())
            )
        
        if EmbodimentPlatform.ROS in self.platform_interfaces:
            platform_tasks.append(
                asyncio.create_task(self.platform_interfaces[EmbodimentPlatform.ROS].start())
            )
        
        if EmbodimentPlatform.WEBSOCKET in self.platform_interfaces:
            platform_tasks.append(
                asyncio.create_task(self.platform_interfaces[EmbodimentPlatform.WEBSOCKET].start())
            )
        
        # Start synchronization tasks
        sync_tasks = [
            asyncio.create_task(self._synchronization_loop()),
            asyncio.create_task(self._sensor_fusion_loop()),
            asyncio.create_task(self._performance_monitoring_loop()),
            asyncio.create_task(self._error_recovery_loop())
        ]
        
        logger.info("Embodiment manager started")
        
        # Wait for all tasks
        await asyncio.gather(*platform_tasks, *sync_tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop embodiment manager and all platform interfaces"""
        self.running = False
        
        # Stop platform interfaces
        for platform, interface in self.platform_interfaces.items():
            try:
                await interface.stop()
                logger.info(f"Stopped {platform.value} interface")
            except Exception as e:
                logger.error(f"Error stopping {platform.value} interface: {e}")
        
        logger.info("Embodiment manager stopped")
    
    async def register_agent(self, agent_id: str, platforms: Set[EmbodimentPlatform], 
                           initial_state: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new agent across specified platforms"""
        try:
            # Create agent state
            agent_state = AgentState(
                agent_id=agent_id,
                platforms=platforms,
                position={'x': 0.0, 'y': 0.0, 'z': 0.0},
                orientation={'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
                velocity={'x': 0.0, 'y': 0.0, 'z': 0.0},
                cognitive_state=initial_state or {},
                sensor_data={},
                last_update=datetime.now().timestamp(),
                status=EmbodimentState.INITIALIZING
            )
            
            self.agents[agent_id] = agent_state
            
            # Initialize agent on each platform
            for platform in platforms:
                if platform in self.platform_interfaces:
                    await self._initialize_agent_on_platform(agent_id, platform)
            
            agent_state.status = EmbodimentState.ACTIVE
            
            logger.info(f"Registered agent {agent_id} on platforms: {[p.value for p in platforms]}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering agent {agent_id}: {e}")
            return False
    
    async def _initialize_agent_on_platform(self, agent_id: str, platform: EmbodimentPlatform):
        """Initialize agent on specific platform"""
        try:
            interface = self.platform_interfaces[platform]
            
            if platform == EmbodimentPlatform.UNITY3D:
                # Unity3D initialization handled by client registration
                pass
            elif platform == EmbodimentPlatform.ROS:
                # Register robot with ROS interface
                robot_config = {'robot_id': agent_id}
                await interface.register_robot(agent_id, robot_config)
            elif platform == EmbodimentPlatform.WEBSOCKET:
                # WebSocket initialization handled by client connection
                pass
                
        except Exception as e:
            logger.error(f"Error initializing agent {agent_id} on {platform.value}: {e}")
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent from all platforms"""
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not registered")
                return False
            
            agent_state = self.agents[agent_id]
            
            # Remove from platforms
            for platform in agent_state.platforms:
                await self._remove_agent_from_platform(agent_id, platform)
            
            # Clean up state
            del self.agents[agent_id]
            if agent_id in self.synchronization_buffer:
                del self.synchronization_buffer[agent_id]
            if agent_id in self.action_queue:
                del self.action_queue[agent_id]
            
            logger.info(f"Unregistered agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False
    
    async def _remove_agent_from_platform(self, agent_id: str, platform: EmbodimentPlatform):
        """Remove agent from specific platform"""
        try:
            # Platform-specific cleanup would go here
            pass
        except Exception as e:
            logger.error(f"Error removing agent {agent_id} from {platform.value}: {e}")
    
    async def update_agent_state(self, agent_id: str, platform: EmbodimentPlatform, 
                                state_update: Dict[str, Any]):
        """Update agent state from specific platform"""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not registered")
            return
        
        try:
            agent_state = self.agents[agent_id]
            
            # Update state based on platform data
            if 'position' in state_update:
                agent_state.position.update(state_update['position'])
            if 'orientation' in state_update:
                agent_state.orientation.update(state_update['orientation'])
            if 'velocity' in state_update:
                agent_state.velocity.update(state_update['velocity'])
            if 'sensor_data' in state_update:
                agent_state.sensor_data[platform.value] = state_update['sensor_data']
            
            agent_state.last_update = datetime.now().timestamp()
            
            # Store in synchronization buffer for fusion
            if agent_id not in self.synchronization_buffer:
                self.synchronization_buffer[agent_id] = {}
            
            self.synchronization_buffer[agent_id][platform] = {
                'timestamp': agent_state.last_update,
                'state_update': state_update
            }
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id} state from {platform.value}: {e}")
    
    async def send_action_to_agent(self, agent_id: str, action_type: str, 
                                  parameters: Dict[str, Any], 
                                  target_platforms: Optional[Set[EmbodimentPlatform]] = None) -> str:
        """Send synchronized action to agent across platforms"""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not registered")
            return None
        
        try:
            agent_state = self.agents[agent_id]
            platforms = target_platforms or agent_state.platforms
            
            # Create action synchronization
            action_id = str(uuid.uuid4())
            action_sync = ActionSynchronization(
                action_id=action_id,
                timestamp=datetime.now().timestamp(),
                platforms=platforms,
                action_type=action_type,
                parameters=parameters,
                status='pending',
                results={}
            )
            
            # Queue action
            if agent_id not in self.action_queue:
                self.action_queue[agent_id] = []
            
            self.action_queue[agent_id].append(action_sync)
            
            # Execute action on each platform
            await self._execute_synchronized_action(agent_id, action_sync)
            
            return action_id
            
        except Exception as e:
            logger.error(f"Error sending action to agent {agent_id}: {e}")
            return None
    
    async def _execute_synchronized_action(self, agent_id: str, action_sync: ActionSynchronization):
        """Execute action synchronously across platforms"""
        try:
            execution_tasks = []
            
            for platform in action_sync.platforms:
                if platform in self.platform_interfaces:
                    task = asyncio.create_task(
                        self._execute_action_on_platform(agent_id, platform, action_sync)
                    )
                    execution_tasks.append(task)
            
            # Wait for all platforms to complete
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Process results
            success_count = 0
            for i, result in enumerate(results):
                platform = list(action_sync.platforms)[i]
                if isinstance(result, Exception):
                    action_sync.results[platform] = {'status': 'error', 'error': str(result)}
                else:
                    action_sync.results[platform] = result
                    if result.get('status') == 'success':
                        success_count += 1
            
            # Update action status
            if success_count == len(action_sync.platforms):
                action_sync.status = 'completed'
            elif success_count > 0:
                action_sync.status = 'partial_success'
            else:
                action_sync.status = 'failed'
            
            logger.info(f"Action {action_sync.action_id} completed with status: {action_sync.status}")
            
        except Exception as e:
            logger.error(f"Error executing synchronized action: {e}")
            action_sync.status = 'error'
    
    async def _execute_action_on_platform(self, agent_id: str, platform: EmbodimentPlatform, 
                                        action_sync: ActionSynchronization) -> Dict[str, Any]:
        """Execute action on specific platform"""
        try:
            interface = self.platform_interfaces[platform]
            
            if platform == EmbodimentPlatform.UNITY3D:
                # Convert to Unity3D action command
                command = Unity3DActionCommand(
                    timestamp=action_sync.timestamp,
                    agent_id=agent_id,
                    action_type=action_sync.action_type,
                    parameters=action_sync.parameters,
                    priority=1,
                    timeout=5.0
                )
                
                # Find Unity3D client for agent
                clients = interface.get_connected_clients()
                target_client = None
                for client_id in clients:
                    state = interface.get_cognitive_state(client_id)
                    if state.get('agent_id') == agent_id:
                        target_client = client_id
                        break
                
                if target_client:
                    success = await interface.send_action_command(target_client, command)
                    return {'status': 'success' if success else 'failed'}
                else:
                    return {'status': 'error', 'error': 'No Unity3D client found for agent'}
            
            elif platform == EmbodimentPlatform.ROS:
                # Convert to ROS motion command
                if action_sync.action_type == 'move':
                    command = ROSMotionCommand(
                        timestamp=action_sync.timestamp,
                        robot_id=agent_id,
                        command_type='velocity',
                        linear_velocity=action_sync.parameters.get('linear_velocity', {'x': 0, 'y': 0, 'z': 0}),
                        angular_velocity=action_sync.parameters.get('angular_velocity', {'x': 0, 'y': 0, 'z': 0}),
                        duration=action_sync.parameters.get('duration', 1.0),
                        frame_id='base_link'
                    )
                    
                    success = await interface.send_motion_command(agent_id, command)
                    return {'status': 'success' if success else 'failed'}
                else:
                    return {'status': 'error', 'error': f'Unsupported action type: {action_sync.action_type}'}
            
            elif platform == EmbodimentPlatform.WEBSOCKET:
                # Send action via WebSocket
                message_data = {
                    'action_type': action_sync.action_type,
                    'parameters': action_sync.parameters,
                    'agent_id': agent_id
                }
                
                # Find WebSocket client for agent
                clients = interface.get_connected_clients()
                target_client = None
                for client_info in clients:
                    if client_info.get('agent_data', {}).get('agent_id') == agent_id:
                        target_client = client_info['client_id']
                        break
                
                if target_client:
                    message = WebSocketMessage(
                        message_type=WebSocketMessageType.ACTION_COMMAND,
                        timestamp=action_sync.timestamp,
                        client_id=target_client,
                        data=message_data,
                        metadata={}
                    )
                    success = await interface._send_message(target_client, message)
                    return {'status': 'success' if success else 'failed'}
                else:
                    return {'status': 'error', 'error': 'No WebSocket client found for agent'}
            
            return {'status': 'error', 'error': f'Unknown platform: {platform}'}
            
        except Exception as e:
            logger.error(f"Error executing action on {platform.value}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _synchronization_loop(self):
        """Main synchronization loop"""
        while self.running:
            try:
                current_time = datetime.now().timestamp()
                
                # Process synchronization for each agent
                for agent_id, agent_state in self.agents.items():
                    if agent_id in self.synchronization_buffer:
                        await self._synchronize_agent_state(agent_id)
                
                # Update last sync time
                self.last_sync_times['main'] = current_time
                
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Error in synchronization loop: {e}")
                await asyncio.sleep(self.sync_interval)
    
    async def _synchronize_agent_state(self, agent_id: str):
        """Synchronize agent state across all platforms"""
        try:
            if agent_id not in self.synchronization_buffer:
                return
            
            agent_state = self.agents[agent_id]
            sync_data = self.synchronization_buffer[agent_id]
            
            # Check if synchronization is needed
            current_time = datetime.now().timestamp()
            time_since_update = current_time - agent_state.last_update
            
            if time_since_update < self.sync_interval:
                return  # Too soon to sync
            
            # Perform sensor fusion
            fusion_result = await self._perform_sensor_fusion(agent_id, sync_data)
            
            # Update agent state with fused data
            if fusion_result:
                agent_state.position = fusion_result.fused_position
                agent_state.orientation = fusion_result.fused_orientation
                agent_state.velocity = fusion_result.fused_velocity
            
            # Synchronize state across platforms
            await self._broadcast_synchronized_state(agent_id, agent_state)
            
            # Clear synchronization buffer
            self.synchronization_buffer[agent_id] = {}
            
        except Exception as e:
            logger.error(f"Error synchronizing agent {agent_id}: {e}")
    
    async def _perform_sensor_fusion(self, agent_id: str, sync_data: Dict) -> Optional[SensorFusionResult]:
        """Perform multi-modal sensor fusion"""
        try:
            current_time = datetime.now().timestamp()
            
            # Collect sensor data from all platforms
            platform_data = {}
            for platform, data in sync_data.items():
                if 'state_update' in data and 'sensor_data' in data['state_update']:
                    platform_data[platform] = data['state_update']['sensor_data']
            
            if not platform_data:
                return None
            
            # Apply fusion algorithms
            fused_position = await self._fuse_position_data(platform_data)
            fused_orientation = await self._fuse_orientation_data(platform_data)
            fused_velocity = await self._fuse_velocity_data(platform_data)
            environment_features = await self._fuse_environment_data(platform_data)
            
            # Calculate confidence scores
            confidence_scores = {}
            for platform in platform_data:
                confidence_scores[platform.value] = self._calculate_platform_confidence(platform, platform_data[platform])
            
            # Detect anomalies
            anomalies = self._detect_sensor_anomalies(platform_data)
            
            return SensorFusionResult(
                timestamp=current_time,
                confidence_scores=confidence_scores,
                fused_position=fused_position,
                fused_orientation=fused_orientation,
                fused_velocity=fused_velocity,
                environment_features=environment_features,
                anomalies=anomalies
            )
            
        except Exception as e:
            logger.error(f"Error performing sensor fusion for agent {agent_id}: {e}")
            return None
    
    async def _fuse_position_data(self, platform_data: Dict) -> Dict[str, float]:
        """Fuse position data from multiple platforms"""
        positions = []
        weights = []
        
        for platform, data in platform_data.items():
            if 'position' in data:
                positions.append(data['position'])
                weights.append(self._get_platform_weight(platform, 'position'))
        
        if not positions:
            return {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Weighted average fusion
        fused_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        total_weight = sum(weights)
        
        if total_weight > 0:
            for pos, weight in zip(positions, weights):
                for axis in ['x', 'y', 'z']:
                    fused_position[axis] += pos.get(axis, 0.0) * weight / total_weight
        
        return fused_position
    
    async def _fuse_orientation_data(self, platform_data: Dict) -> Dict[str, float]:
        """Fuse orientation data from multiple platforms"""
        # Simplified orientation fusion - in practice would use quaternion SLERP
        orientations = []
        weights = []
        
        for platform, data in platform_data.items():
            if 'orientation' in data:
                orientations.append(data['orientation'])
                weights.append(self._get_platform_weight(platform, 'orientation'))
        
        if not orientations:
            return {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
        
        # Simplified weighted average (proper implementation would use quaternion math)
        fused_orientation = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
        total_weight = sum(weights)
        
        if total_weight > 0:
            for ori, weight in zip(orientations, weights):
                for axis in ['x', 'y', 'z', 'w']:
                    fused_orientation[axis] += ori.get(axis, 0.0 if axis != 'w' else 1.0) * weight / total_weight
        
        return fused_orientation
    
    async def _fuse_velocity_data(self, platform_data: Dict) -> Dict[str, float]:
        """Fuse velocity data from multiple platforms"""
        velocities = []
        weights = []
        
        for platform, data in platform_data.items():
            if 'velocity' in data:
                velocities.append(data['velocity'])
                weights.append(self._get_platform_weight(platform, 'velocity'))
        
        if not velocities:
            return {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Weighted average fusion
        fused_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        total_weight = sum(weights)
        
        if total_weight > 0:
            for vel, weight in zip(velocities, weights):
                for axis in ['x', 'y', 'z']:
                    fused_velocity[axis] += vel.get(axis, 0.0) * weight / total_weight
        
        return fused_velocity
    
    async def _fuse_environment_data(self, platform_data: Dict) -> Dict[str, Any]:
        """Fuse environment data from multiple platforms"""
        environment_features = {
            'obstacles': [],
            'landmarks': [],
            'surfaces': [],
            'lighting': {},
            'audio': {}
        }
        
        for platform, data in platform_data.items():
            if 'environment' in data:
                env_data = data['environment']
                
                # Merge environment features
                for feature_type, features in env_data.items():
                    if feature_type in environment_features:
                        if isinstance(features, list):
                            environment_features[feature_type].extend(features)
                        elif isinstance(features, dict):
                            environment_features[feature_type].update(features)
        
        return environment_features
    
    def _get_platform_weight(self, platform: EmbodimentPlatform, data_type: str) -> float:
        """Get platform weight for sensor fusion"""
        # Default weights - could be made configurable
        weights = {
            EmbodimentPlatform.ROS: {
                'position': 0.8,  # High accuracy for robotic platforms
                'orientation': 0.9,
                'velocity': 0.8
            },
            EmbodimentPlatform.UNITY3D: {
                'position': 0.7,  # Good for simulation
                'orientation': 0.8,
                'velocity': 0.7
            },
            EmbodimentPlatform.WEBSOCKET: {
                'position': 0.5,  # Lower accuracy for web clients
                'orientation': 0.6,
                'velocity': 0.5
            }
        }
        
        return weights.get(platform, {}).get(data_type, 0.5)
    
    def _calculate_platform_confidence(self, platform: EmbodimentPlatform, data: Dict[str, Any]) -> float:
        """Calculate confidence score for platform data"""
        # Simplified confidence calculation
        base_confidence = 0.7
        
        # Adjust based on data completeness
        required_fields = ['position', 'orientation', 'velocity']
        available_fields = sum(1 for field in required_fields if field in data)
        completeness_factor = available_fields / len(required_fields)
        
        # Adjust based on data freshness (simplified)
        freshness_factor = 1.0  # Would calculate based on timestamp in real implementation
        
        return base_confidence * completeness_factor * freshness_factor
    
    def _detect_sensor_anomalies(self, platform_data: Dict) -> List[str]:
        """Detect anomalies in sensor data"""
        anomalies = []
        
        # Check for conflicting position data
        positions = []
        for platform, data in platform_data.items():
            if 'position' in data:
                positions.append(data['position'])
        
        if len(positions) > 1:
            # Calculate variance in position data
            for axis in ['x', 'y', 'z']:
                values = [pos.get(axis, 0.0) for pos in positions]
                if max(values) - min(values) > 10.0:  # Large position disagreement
                    anomalies.append(f"Position disagreement on {axis} axis")
        
        return anomalies
    
    async def _broadcast_synchronized_state(self, agent_id: str, agent_state: AgentState):
        """Broadcast synchronized state to all platforms"""
        try:
            state_data = {
                'agent_id': agent_id,
                'position': agent_state.position,
                'orientation': agent_state.orientation,
                'velocity': agent_state.velocity,
                'cognitive_state': agent_state.cognitive_state,
                'timestamp': agent_state.last_update
            }
            
            # Broadcast to each platform
            for platform in agent_state.platforms:
                if platform in self.platform_interfaces:
                    await self._send_state_to_platform(platform, agent_id, state_data)
            
        except Exception as e:
            logger.error(f"Error broadcasting synchronized state for agent {agent_id}: {e}")
    
    async def _send_state_to_platform(self, platform: EmbodimentPlatform, agent_id: str, state_data: Dict[str, Any]):
        """Send synchronized state to specific platform"""
        try:
            interface = self.platform_interfaces[platform]
            
            if platform == EmbodimentPlatform.UNITY3D:
                await interface.broadcast_cognitive_state(state_data)
            elif platform == EmbodimentPlatform.ROS:
                # ROS state broadcasting would be implemented here
                pass
            elif platform == EmbodimentPlatform.WEBSOCKET:
                await interface.broadcast_cognitive_state(state_data)
            
        except Exception as e:
            logger.error(f"Error sending state to {platform.value}: {e}")
    
    async def _sensor_fusion_loop(self):
        """Dedicated sensor fusion processing loop"""
        while self.running:
            try:
                # Process sensor fusion for all agents
                for agent_id in list(self.agents.keys()):
                    if agent_id in self.synchronization_buffer:
                        # Check if fusion is needed
                        sync_data = self.synchronization_buffer[agent_id]
                        if len(sync_data) > 1:  # Multiple platforms have data
                            fusion_result = await self._perform_sensor_fusion(agent_id, sync_data)
                            if fusion_result:
                                # Store fusion results
                                agent_state = self.agents[agent_id]
                                agent_state.sensor_data['_fused'] = asdict(fusion_result)
                
                await asyncio.sleep(self.sync_interval / 2)  # Faster fusion loop
                
            except Exception as e:
                logger.error(f"Error in sensor fusion loop: {e}")
                await asyncio.sleep(self.sync_interval)
    
    async def _performance_monitoring_loop(self):
        """Monitor performance metrics and system health"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Update performance metrics
                self.performance_metrics['agents_count'] = len(self.agents)
                self.performance_metrics['platforms_active'] = len(self.platform_interfaces)
                self.performance_metrics['sync_rate'] = 1.0 / self.sync_interval
                self.performance_metrics['last_update'] = current_time.isoformat()
                
                # Check platform health
                for platform, interface in self.platform_interfaces.items():
                    try:
                        # Platform-specific health checks would go here
                        self.platform_states[platform] = EmbodimentState.ACTIVE
                    except Exception as e:
                        self.platform_states[platform] = EmbodimentState.ERROR
                        logger.error(f"Health check failed for {platform.value}: {e}")
                
                await asyncio.sleep(5.0)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(5.0)
    
    async def _error_recovery_loop(self):
        """Handle error recovery and reconnection"""
        while self.running:
            try:
                # Check for failed platforms and attempt recovery
                for platform, state in self.platform_states.items():
                    if state == EmbodimentState.ERROR:
                        logger.info(f"Attempting to recover {platform.value} interface")
                        
                        try:
                            interface = self.platform_interfaces[platform]
                            # Attempt to restart interface
                            await interface.stop()
                            await asyncio.sleep(1.0)
                            
                            if await interface.initialize():
                                await interface.start()
                                self.platform_states[platform] = EmbodimentState.ACTIVE
                                logger.info(f"Successfully recovered {platform.value} interface")
                            else:
                                logger.error(f"Failed to recover {platform.value} interface")
                        except Exception as e:
                            logger.error(f"Error during recovery of {platform.value}: {e}")
                
                await asyncio.sleep(10.0)  # Check for recovery every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in error recovery loop: {e}")
                await asyncio.sleep(10.0)
    
    # Public API methods
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get current state of an agent"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, AgentState]:
        """Get all registered agents"""
        return self.agents.copy()
    
    def get_platform_states(self) -> Dict[EmbodimentPlatform, EmbodimentState]:
        """Get status of all platforms"""
        return self.platform_states.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    def get_global_cognitive_state(self) -> Dict[str, Any]:
        """Get global cognitive state across all agents and platforms"""
        return self.global_cognitive_state.copy()
    
    def register_fusion_algorithm(self, data_type: str, algorithm_func: Callable):
        """Register custom sensor fusion algorithm"""
        self.sensor_fusion_algorithms[data_type] = algorithm_func
    
    def register_sync_handler(self, sync_type: str, handler_func: Callable):
        """Register custom synchronization handler"""
        self.sync_handlers[sync_type] = handler_func