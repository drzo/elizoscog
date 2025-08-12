#!/usr/bin/env python3
"""
ROS Node Integrations for Robotic Platforms
Phase 4 Step 2: ROS integration with real-time bi-directional data flow
"""

import asyncio
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

# Mock ROS2 types for environments where ROS2 is not installed
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String, Header
    from geometry_msgs.msg import Twist, PoseStamped, TransformStamped
    from sensor_msgs.msg import PointCloud2, Image, Imu, NavSatFix
    from tf2_ros import TransformBroadcaster, Buffer, TransformListener
    ROS_AVAILABLE = True
except ImportError:
    logger.warning("ROS2 not available, using mock implementations")
    ROS_AVAILABLE = False
    
    # Mock ROS2 classes
    class Node:
        def __init__(self, name):
            self.name = name
        def get_logger(self):
            return logger
        def create_publisher(self, msg_type, topic, qos_profile):
            return MockPublisher(msg_type, topic)
        def create_subscription(self, msg_type, topic, callback, qos_profile):
            return MockSubscription(msg_type, topic, callback)
        def create_timer(self, period, callback):
            return MockTimer(period, callback)
        def destroy_node(self):
            pass
    
    class MockPublisher:
        def __init__(self, msg_type, topic):
            self.msg_type = msg_type
            self.topic = topic
        def publish(self, msg):
            logger.info(f"Mock publish to {self.topic}: {msg}")
    
    class MockSubscription:
        def __init__(self, msg_type, topic, callback):
            self.msg_type = msg_type
            self.topic = topic
            self.callback = callback
    
    class MockTimer:
        def __init__(self, period, callback):
            self.period = period
            self.callback = callback
    
    # Mock message types
    class String:
        def __init__(self):
            self.data = ""
    
    class Twist:
        def __init__(self):
            self.linear = type('obj', (object,), {'x': 0.0, 'y': 0.0, 'z': 0.0})()
            self.angular = type('obj', (object,), {'x': 0.0, 'y': 0.0, 'z': 0.0})()
    
    class PoseStamped:
        def __init__(self):
            self.header = type('obj', (object,), {'stamp': None, 'frame_id': ''})()
            self.pose = type('obj', (object,), {
                'position': type('obj', (object,), {'x': 0.0, 'y': 0.0, 'z': 0.0})(),
                'orientation': type('obj', (object,), {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})()
            })()

class ROSMessageType(Enum):
    """ROS message types for cognitive integration"""
    COGNITIVE_STATE = "cognitive_state"
    SENSOR_DATA = "sensor_data"
    MOTION_COMMAND = "motion_command"
    ROBOT_STATUS = "robot_status"
    ENVIRONMENT_MAP = "environment_map"
    GOAL_UPDATE = "goal_update"

@dataclass
class ROSSensorData:
    """ROS sensor data structure"""
    timestamp: float
    robot_id: str
    sensor_type: str
    frame_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class ROSMotionCommand:
    """ROS motion command structure"""
    timestamp: float
    robot_id: str
    command_type: str
    linear_velocity: Dict[str, float]
    angular_velocity: Dict[str, float]
    duration: float
    frame_id: str

class ROSCognitiveNode(Node):
    """ROS node for cognitive integration"""
    
    def __init__(self, node_name: str, config: Dict[str, Any]):
        super().__init__(node_name)
        self.config = config
        self.robot_id = config.get('robot_id', str(uuid.uuid4()))
        
        # Publishers
        self.cognitive_state_pub = self.create_publisher(
            String, 
            '/cognitive/state', 
            10
        )
        
        self.motion_command_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        # Subscribers
        self.sensor_data_sub = self.create_subscription(
            String,
            '/cognitive/sensor_data',
            self.sensor_data_callback,
            10
        )
        
        self.robot_status_sub = self.create_subscription(
            String,
            '/robot/status',
            self.robot_status_callback,
            10
        )
        
        # Timers
        self.heartbeat_timer = self.create_timer(1.0, self.heartbeat_callback)
        self.cognitive_timer = self.create_timer(0.1, self.cognitive_update_callback)
        
        # State
        self.cognitive_state = {}
        self.sensor_data_buffer = {}
        self.last_motion_command = None
        self.robot_status = {}
        
        # Callbacks
        self.message_handlers = {}
        self.sensor_processors = {}
        
        self.get_logger().info(f"ROS Cognitive Node initialized: {node_name}")
    
    def sensor_data_callback(self, msg):
        """Handle incoming sensor data"""
        try:
            data = json.loads(msg.data)
            sensor_data = ROSSensorData(
                timestamp=data.get('timestamp', datetime.now().timestamp()),
                robot_id=data.get('robot_id', self.robot_id),
                sensor_type=data.get('sensor_type', 'unknown'),
                frame_id=data.get('frame_id', 'base_link'),
                data=data.get('data', {}),
                metadata=data.get('metadata', {})
            )
            
            # Process sensor data
            asyncio.create_task(self.process_sensor_data(sensor_data))
            
        except Exception as e:
            self.get_logger().error(f"Error processing sensor data: {e}")
    
    def robot_status_callback(self, msg):
        """Handle robot status updates"""
        try:
            self.robot_status = json.loads(msg.data)
            self.robot_status['timestamp'] = datetime.now().timestamp()
            
            # Update cognitive state
            self.cognitive_state['robot_status'] = self.robot_status
            
        except Exception as e:
            self.get_logger().error(f"Error processing robot status: {e}")
    
    def heartbeat_callback(self):
        """Send heartbeat message"""
        heartbeat_msg = String()
        heartbeat_data = {
            'type': 'heartbeat',
            'robot_id': self.robot_id,
            'timestamp': datetime.now().timestamp(),
            'status': 'active'
        }
        heartbeat_msg.data = json.dumps(heartbeat_data)
        # Would publish to heartbeat topic in real implementation
    
    def cognitive_update_callback(self):
        """Publish cognitive state updates"""
        try:
            cognitive_msg = String()
            cognitive_data = {
                'type': ROSMessageType.COGNITIVE_STATE.value,
                'robot_id': self.robot_id,
                'timestamp': datetime.now().timestamp(),
                'cognitive_state': self.cognitive_state
            }
            cognitive_msg.data = json.dumps(cognitive_data)
            self.cognitive_state_pub.publish(cognitive_msg)
            
        except Exception as e:
            self.get_logger().error(f"Error publishing cognitive state: {e}")
    
    async def process_sensor_data(self, sensor_data: ROSSensorData):
        """Process incoming sensor data"""
        try:
            # Buffer sensor data
            if sensor_data.robot_id not in self.sensor_data_buffer:
                self.sensor_data_buffer[sensor_data.robot_id] = {}
            
            self.sensor_data_buffer[sensor_data.robot_id][sensor_data.sensor_type] = sensor_data
            
            # Process with specific processor if available
            if sensor_data.sensor_type in self.sensor_processors:
                await self.sensor_processors[sensor_data.sensor_type](sensor_data)
            
            # Update cognitive state
            await self.update_cognitive_state(sensor_data)
            
        except Exception as e:
            self.get_logger().error(f"Error processing sensor data: {e}")
    
    async def update_cognitive_state(self, sensor_data: ROSSensorData):
        """Update cognitive state based on sensor data"""
        if 'sensors' not in self.cognitive_state:
            self.cognitive_state['sensors'] = {}
        
        self.cognitive_state['sensors'][sensor_data.sensor_type] = {
            'timestamp': sensor_data.timestamp,
            'frame_id': sensor_data.frame_id,
            'data': sensor_data.data,
            'metadata': sensor_data.metadata
        }
        
        self.cognitive_state['last_update'] = datetime.now().timestamp()
    
    def publish_motion_command(self, command: ROSMotionCommand):
        """Publish motion command to robot"""
        try:
            twist_msg = Twist()
            twist_msg.linear.x = command.linear_velocity.get('x', 0.0)
            twist_msg.linear.y = command.linear_velocity.get('y', 0.0)
            twist_msg.linear.z = command.linear_velocity.get('z', 0.0)
            twist_msg.angular.x = command.angular_velocity.get('x', 0.0)
            twist_msg.angular.y = command.angular_velocity.get('y', 0.0)
            twist_msg.angular.z = command.angular_velocity.get('z', 0.0)
            
            self.motion_command_pub.publish(twist_msg)
            self.last_motion_command = command
            
            self.get_logger().info(f"Published motion command: {command}")
            
        except Exception as e:
            self.get_logger().error(f"Error publishing motion command: {e}")
    
    def register_sensor_processor(self, sensor_type: str, processor_func: Callable):
        """Register custom sensor processor"""
        self.sensor_processors[sensor_type] = processor_func
    
    def register_message_handler(self, message_type: ROSMessageType, handler_func: Callable):
        """Register custom message handler"""
        self.message_handlers[message_type] = handler_func


class ROSInterface:
    """ROS interface for cognitive integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.node_name = config.get('node_name', 'cognitive_integration_node')
        
        self.node = None
        self.executor = None
        self.spin_thread = None
        
        self.running = False
        self.cognitive_nodes = {}
        self.node_managers = {}
    
    async def initialize(self) -> bool:
        """Initialize ROS interface"""
        try:
            if ROS_AVAILABLE:
                rclpy.init()
            
            # Create main cognitive node
            self.node = ROSCognitiveNode(self.node_name, self.config)
            
            # Create node manager
            self.node_manager = ROSNodeManager(self.config)
            await self.node_manager.initialize()
            
            logger.info("ROS interface initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ROS interface: {e}")
            return False
    
    async def start(self):
        """Start ROS interface"""
        self.running = True
        
        if ROS_AVAILABLE:
            # Start ROS spinning in separate thread
            self.executor = rclpy.executors.MultiThreadedExecutor()
            self.executor.add_node(self.node)
            
            self.spin_thread = threading.Thread(target=self.executor.spin)
            self.spin_thread.daemon = True
            self.spin_thread.start()
        
        logger.info("ROS interface started")
    
    async def stop(self):
        """Stop ROS interface"""
        self.running = False
        
        if ROS_AVAILABLE and self.executor:
            self.executor.shutdown()
            
        if self.spin_thread and self.spin_thread.is_alive():
            self.spin_thread.join(timeout=5.0)
        
        if self.node:
            self.node.destroy_node()
        
        if ROS_AVAILABLE:
            rclpy.shutdown()
        
        logger.info("ROS interface stopped")
    
    async def send_motion_command(self, robot_id: str, command: ROSMotionCommand) -> bool:
        """Send motion command to robot"""
        try:
            if robot_id in self.cognitive_nodes:
                self.cognitive_nodes[robot_id].publish_motion_command(command)
                return True
            elif self.node:
                self.node.publish_motion_command(command)
                return True
            else:
                logger.error(f"No ROS node available for robot {robot_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending motion command: {e}")
            return False
    
    async def get_sensor_data(self, robot_id: str, sensor_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get sensor data from robot"""
        try:
            if robot_id in self.cognitive_nodes:
                node = self.cognitive_nodes[robot_id]
            elif self.node:
                node = self.node
            else:
                return None
            
            if sensor_type:
                return node.sensor_data_buffer.get(robot_id, {}).get(sensor_type)
            else:
                return node.sensor_data_buffer.get(robot_id, {})
                
        except Exception as e:
            logger.error(f"Error getting sensor data: {e}")
            return None
    
    def get_cognitive_state(self, robot_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current cognitive state"""
        if robot_id and robot_id in self.cognitive_nodes:
            return self.cognitive_nodes[robot_id].cognitive_state
        elif self.node:
            return self.node.cognitive_state
        else:
            return {}
    
    def register_robot(self, robot_id: str, robot_config: Dict[str, Any]) -> bool:
        """Register a new robot with the ROS interface"""
        try:
            node_name = f"{self.node_name}_{robot_id}"
            cognitive_node = ROSCognitiveNode(node_name, robot_config)
            
            self.cognitive_nodes[robot_id] = cognitive_node
            
            if ROS_AVAILABLE and self.executor:
                self.executor.add_node(cognitive_node)
            
            logger.info(f"Registered robot: {robot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering robot {robot_id}: {e}")
            return False


class ROSNodeManager:
    """Manager for ROS nodes and robotic platform integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_nodes = {}
        self.node_configurations = {}
        self.platform_adapters = {}
        
    async def initialize(self) -> bool:
        """Initialize ROS node manager"""
        try:
            # Register default platform adapters
            self._register_default_adapters()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ROS node manager: {e}")
            return False
    
    def _register_default_adapters(self):
        """Register default platform adapters"""
        self.platform_adapters['turtlebot'] = self._create_turtlebot_adapter
        self.platform_adapters['husky'] = self._create_husky_adapter
        self.platform_adapters['universal_robot'] = self._create_ur_adapter
        self.platform_adapters['franka'] = self._create_franka_adapter
    
    def _create_turtlebot_adapter(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create TurtleBot platform adapter configuration"""
        return {
            'motion_topic': '/cmd_vel',
            'odom_topic': '/odom',
            'scan_topic': '/scan',
            'sensors': ['lidar', 'imu', 'camera'],
            'capabilities': ['navigation', 'mapping', 'object_detection']
        }
    
    def _create_husky_adapter(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Husky platform adapter configuration"""
        return {
            'motion_topic': '/husky_velocity_controller/cmd_vel',
            'odom_topic': '/odometry/filtered',
            'scan_topic': '/scan',
            'sensors': ['lidar', 'imu', 'gps', 'camera'],
            'capabilities': ['navigation', 'mapping', 'outdoor_operation']
        }
    
    def _create_ur_adapter(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Universal Robots adapter configuration"""
        return {
            'joint_trajectory_topic': '/scaled_pos_joint_traj_controller/follow_joint_trajectory',
            'joint_state_topic': '/joint_states',
            'sensors': ['force_torque', 'joint_encoders'],
            'capabilities': ['manipulation', 'precise_positioning']
        }
    
    def _create_franka_adapter(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Franka Emika adapter configuration"""
        return {
            'cartesian_impedance_topic': '/cartesian_impedance_controller/equilibrium_pose',
            'joint_state_topic': '/franka_state_controller/joint_states',
            'sensors': ['force_torque', 'joint_encoders', 'gripper'],
            'capabilities': ['manipulation', 'force_control', 'precision_grasping']
        }
    
    async def create_platform_node(self, platform_type: str, robot_id: str, config: Dict[str, Any]) -> Optional[str]:
        """Create a platform-specific ROS node"""
        try:
            if platform_type not in self.platform_adapters:
                logger.error(f"Unknown platform type: {platform_type}")
                return None
            
            # Get platform adapter configuration
            adapter_config = self.platform_adapters[platform_type](config)
            
            # Merge with provided config
            node_config = {**adapter_config, **config, 'robot_id': robot_id}
            
            # Create cognitive node
            node_name = f"cognitive_{platform_type}_{robot_id}"
            cognitive_node = ROSCognitiveNode(node_name, node_config)
            
            # Store node reference
            self.active_nodes[robot_id] = cognitive_node
            self.node_configurations[robot_id] = node_config
            
            logger.info(f"Created {platform_type} node for robot {robot_id}")
            return node_name
            
        except Exception as e:
            logger.error(f"Error creating platform node: {e}")
            return None
    
    async def destroy_platform_node(self, robot_id: str):
        """Destroy a platform-specific ROS node"""
        try:
            if robot_id in self.active_nodes:
                node = self.active_nodes[robot_id]
                node.destroy_node()
                del self.active_nodes[robot_id]
                del self.node_configurations[robot_id]
                
                logger.info(f"Destroyed node for robot {robot_id}")
                
        except Exception as e:
            logger.error(f"Error destroying platform node: {e}")
    
    def get_active_nodes(self) -> Dict[str, Any]:
        """Get all active ROS nodes"""
        return self.active_nodes
    
    def get_node_configuration(self, robot_id: str) -> Optional[Dict[str, Any]]:
        """Get node configuration for a robot"""
        return self.node_configurations.get(robot_id)
    
    def register_platform_adapter(self, platform_type: str, adapter_func: Callable):
        """Register custom platform adapter"""
        self.platform_adapters[platform_type] = adapter_func
    
    async def monitor_node_health(self):
        """Monitor health of active ROS nodes"""
        while True:
            try:
                current_time = datetime.now()
                
                for robot_id, node in self.active_nodes.items():
                    # Check node health metrics
                    # In a real implementation, this would check ROS node status
                    pass
                
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring node health: {e}")
                await asyncio.sleep(5.0)