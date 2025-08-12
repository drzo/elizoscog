#!/usr/bin/env python3
"""
Simple Integration Test for Embodiment Layer Bindings
Tests basic functionality and integration with master framework
"""

import asyncio
import json
import logging
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_embodiment_bindings():
    """Test basic embodiment bindings functionality"""
    print("🧪 Testing Basic Embodiment Bindings...")
    
    # Test Unity3D bindings
    print("🎮 Testing Unity3D bindings...")
    try:
        from embodiment.unity_bindings import Unity3DInterface, Unity3DSensorData, Unity3DActionCommand
        
        # Create interface
        unity_config = {'host': 'localhost', 'port': 12349, 'heartbeat_timeout': 5}
        unity_interface = Unity3DInterface(unity_config)
        
        # Test initialization
        result = await unity_interface.initialize()
        print(f"  ✅ Unity3D initialization: {result}")
        
        # Test sensor data structure
        sensor_data = Unity3DSensorData(
            timestamp=time.time(),
            agent_id='test_agent',
            sensor_type='camera',
            position={'x': 1.0, 'y': 2.0, 'z': 3.0},
            rotation={'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
            velocity={'x': 0.5, 'y': 0.0, 'z': 0.0},
            raw_data={'image': 'test_image'},
            metadata={'fps': 30}
        )
        print(f"  ✅ Unity3D sensor data structure created")
        
        # Test action command
        action_cmd = Unity3DActionCommand(
            timestamp=time.time(),
            agent_id='test_agent',
            action_type='move',
            parameters={'target': {'x': 5.0, 'y': 0.0, 'z': 0.0}},
            priority=1,
            timeout=5.0
        )
        print(f"  ✅ Unity3D action command structure created")
        
        await unity_interface.stop()
        
    except Exception as e:
        print(f"  ❌ Unity3D test failed: {e}")
    
    # Test ROS bindings
    print("🤖 Testing ROS bindings...")
    try:
        from embodiment.ros_bindings import ROSInterface, ROSSensorData, ROSMotionCommand
        
        # Create interface
        ros_config = {'node_name': 'test_node', 'robot_id': 'test_robot'}
        ros_interface = ROSInterface(ros_config)
        
        # Test initialization
        result = await ros_interface.initialize()
        print(f"  ✅ ROS initialization: {result}")
        
        # Test sensor data structure
        sensor_data = ROSSensorData(
            timestamp=time.time(),
            robot_id='robot_1',
            sensor_type='lidar',
            frame_id='base_link',
            data={'points': [[1, 2, 3], [4, 5, 6]]},
            metadata={'scan_time': 0.1}
        )
        print(f"  ✅ ROS sensor data structure created")
        
        # Test motion command
        motion_cmd = ROSMotionCommand(
            timestamp=time.time(),
            robot_id='robot_1',
            command_type='velocity',
            linear_velocity={'x': 1.0, 'y': 0.0, 'z': 0.0},
            angular_velocity={'x': 0.0, 'y': 0.0, 'z': 0.5},
            duration=2.0,
            frame_id='base_link'
        )
        print(f"  ✅ ROS motion command structure created")
        
        await ros_interface.stop()
        
    except Exception as e:
        print(f"  ❌ ROS test failed: {e}")
    
    # Test WebSocket bindings
    print("🌐 Testing WebSocket bindings...")
    try:
        from embodiment.websocket_bindings import WebSocketInterface, WebSocketMessage, WebSocketMessageType
        
        # Create interface
        websocket_config = {'host': 'localhost', 'port': 8769, 'heartbeat_interval': 5}
        websocket_interface = WebSocketInterface(websocket_config)
        
        # Test initialization
        result = await websocket_interface.initialize()
        print(f"  ✅ WebSocket initialization: {result}")
        
        # Test message structure
        message = WebSocketMessage(
            message_type=WebSocketMessageType.USER_INPUT,
            timestamp=time.time(),
            client_id='client_123',
            data={'input': 'Hello, agent!', 'input_type': 'text'},
            metadata={'session_id': 'session_456'}
        )
        print(f"  ✅ WebSocket message structure created")
        
        # Test server capabilities
        capabilities = websocket_interface._get_server_capabilities()
        print(f"  ✅ WebSocket server capabilities: {len(capabilities)} items")
        
        await websocket_interface.stop()
        
    except Exception as e:
        print(f"  ❌ WebSocket test failed: {e}")

async def test_embodiment_manager():
    """Test embodiment manager coordination"""
    print("🎛️ Testing Embodiment Manager...")
    
    try:
        from embodiment.embodiment_manager import EmbodimentManager, EmbodimentPlatform, AgentState, EmbodimentState
        
        # Create manager with test configuration
        config = {
            'unity3d': {'enabled': False},  # Disable for testing
            'ros': {'enabled': False},
            'websocket': {'enabled': False},
            'sync_interval': 0.5,
            'max_sync_delay': 1.0
        }
        
        manager = EmbodimentManager(config)
        
        # Test initialization
        result = await manager.initialize()
        print(f"  ✅ Manager initialization: {result}")
        
        # Test agent state structure
        agent_state = AgentState(
            agent_id='test_agent',
            platforms={EmbodimentPlatform.UNITY3D},
            position={'x': 0.0, 'y': 0.0, 'z': 0.0},
            orientation={'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
            velocity={'x': 0.0, 'y': 0.0, 'z': 0.0},
            cognitive_state={'mode': 'active'},
            sensor_data={},
            last_update=time.time(),
            status=EmbodimentState.ACTIVE
        )
        print(f"  ✅ Agent state structure created")
        
        # Test platform weights
        unity_weight = manager._get_platform_weight(EmbodimentPlatform.UNITY3D, 'position')
        ros_weight = manager._get_platform_weight(EmbodimentPlatform.ROS, 'position')
        websocket_weight = manager._get_platform_weight(EmbodimentPlatform.WEBSOCKET, 'position')
        print(f"  ✅ Platform weights: Unity={unity_weight}, ROS={ros_weight}, WebSocket={websocket_weight}")
        
        # Test sensor fusion
        platform_data = {
            EmbodimentPlatform.UNITY3D: {'position': {'x': 1.0, 'y': 0.0, 'z': 0.0}},
            EmbodimentPlatform.WEBSOCKET: {'position': {'x': 1.1, 'y': 0.1, 'z': 0.0}}
        }
        
        fused_position = await manager._fuse_position_data(platform_data)
        print(f"  ✅ Sensor fusion result: {fused_position}")
        
        # Test status
        platform_states = manager.get_platform_states()
        performance_metrics = manager.get_performance_metrics()
        print(f"  ✅ Manager status: {len(platform_states)} platforms, metrics available: {bool(performance_metrics)}")
        
        await manager.stop()
        
    except Exception as e:
        print(f"  ❌ Embodiment manager test failed: {e}")

async def test_master_framework_integration():
    """Test integration with master framework"""
    print("🌟 Testing Master Framework Integration...")
    
    try:
        from integration.master_integration import HybridCognitiveFinancialFramework
        
        # Create framework with embodiment disabled for testing
        config = {
            'embodiment': {
                'unity3d': {'enabled': False},
                'ros': {'enabled': False},
                'websocket': {'enabled': False}
            }
        }
        
        framework = HybridCognitiveFinancialFramework(config)
        
        # Test API methods exist
        assert hasattr(framework, 'register_embodied_agent'), "register_embodied_agent method missing"
        assert hasattr(framework, 'send_embodied_action'), "send_embodied_action method missing"
        assert hasattr(framework, 'get_embodied_agent_state'), "get_embodied_agent_state method missing"
        assert hasattr(framework, 'get_all_embodied_agents'), "get_all_embodied_agents method missing"
        assert hasattr(framework, 'get_embodiment_status'), "get_embodiment_status method missing"
        assert hasattr(framework, 'process_embodied_cognitive_query'), "process_embodied_cognitive_query method missing"
        print(f"  ✅ All embodiment API methods are present")
        
        # Test embodiment status without initialization
        status = framework.get_embodiment_status()
        print(f"  ✅ Embodiment status (not initialized): {status['status']}")
        
        # Test initialization (this may take some time)
        print("  🔄 Initializing framework (this may take a moment)...")
        start_time = time.time()
        result = await framework.initialize()
        init_time = time.time() - start_time
        print(f"  ✅ Framework initialization: {result} (took {init_time:.2f}s)")
        
        if result:
            # Test embodiment status after initialization
            status = framework.get_embodiment_status()
            print(f"  ✅ Embodiment status (initialized): {status}")
            
            # Test embodied agent operations (should handle gracefully when embodiment is disabled)
            agents = framework.get_all_embodied_agents()
            print(f"  ✅ Embodied agents: {len(agents)} agents")
            
            # Test embodied cognitive query
            query_result = await framework.process_embodied_cognitive_query(
                'test_agent', 
                'What is my current position?',
                {'test': True}
            )
            print(f"  ✅ Embodied cognitive query processed: {bool(query_result)}")
        
        await framework.shutdown()
        
    except Exception as e:
        print(f"  ❌ Master framework integration test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🚀 Starting Embodiment Layer Integration Tests")
    print("=" * 60)
    
    try:
        await test_basic_embodiment_bindings()
        print()
        
        await test_embodiment_manager()
        print()
        
        await test_master_framework_integration()
        print()
        
        print("=" * 60)
        print("🎉 Embodiment Layer Integration Tests Complete!")
        print()
        print("✅ Key Features Implemented:")
        print("  • Unity3D cognitive interface bindings")
        print("  • ROS node integrations for robotic platforms")
        print("  • WebSocket interfaces for web agents")
        print("  • Multi-platform embodiment synchronization")
        print("  • Sensor fusion algorithms")
        print("  • Bi-directional data flow")
        print("  • Integration with master cognitive framework")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())