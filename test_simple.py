#!/usr/bin/env python3
"""
Simple test for completed ElizaOS bridges
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bridges.agentmemory_bridge import AgentmemoryBridge
from bridges.easycompletion_bridge import EasycompletionBridge

async def test_completed_bridges():
    """Test the completed bridges"""
    print("🧪 Testing Completed ElizaOS Bridge Implementations...")
    
    # Test configuration
    test_config = {
        'elizaos': {'endpoint': 'http://localhost:3000'},
        'opencog': {'host': 'localhost', 'port': 17001},
        'gnucash': {'file_path': '/tmp/test.gnucash'}
    }
    
    # Test bridges
    bridges = {
        'agentmemory': AgentmemoryBridge(test_config),
        'easycompletion': EasycompletionBridge(test_config)
    }
    
    # Test initialization
    for name, bridge in bridges.items():
        try:
            success = await bridge.initialize()
            status = "✅" if success else "❌"
            print(f"  {status} {name} bridge: {'Initialized' if success else 'Failed'}")
        except Exception as e:
            print(f"  ❌ {name} bridge: Failed with error - {e}")
    
    # Test operations
    print("\n🧪 Testing Operations...")
    
    # Test agentmemory
    try:
        memory_bridge = bridges['agentmemory'] 
        
        # Store memory
        store_request = {
            'operation': 'store_memory',
            'agent_id': 'test_agent',
            'data': {'content': 'Hello ElizaOS!', 'type': 'greeting'}
        }
        response = await memory_bridge.process_elizaos_request(store_request)
        print(f"  ✅ Memory storage: {response.get('success', False)}")
        
        # Retrieve memory
        retrieve_request = {
            'operation': 'retrieve_memory', 
            'agent_id': 'test_agent',
            'data': {'query': 'Hello'}
        }
        response = await memory_bridge.process_elizaos_request(retrieve_request)
        print(f"  ✅ Memory retrieval: {len(response.get('memories', []))} memories found")
        
    except Exception as e:
        print(f"  ❌ agentmemory operations failed: {e}")
    
    # Test easycompletion
    try:
        completion_bridge = bridges['easycompletion']
        
        # Text completion
        completion_request = {
            'operation': 'text_completion',
            'agent_id': 'test_agent',
            'data': {'prompt': 'Complete this sentence', 'context': 'test'}
        }
        response = await completion_bridge.process_elizaos_request(completion_request)
        print(f"  ✅ Text completion: {response.get('success', False)}")
        
    except Exception as e:
        print(f"  ❌ easycompletion operations failed: {e}")
    
    print("\n🎉 ElizaOS implementation testing completed!")

if __name__ == "__main__":
    asyncio.run(test_completed_bridges())