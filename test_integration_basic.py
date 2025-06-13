#!/usr/bin/env python3
"""
Basic integration test for ElizaOS-OpenCog-GnuCash Integration Framework
Tests core bridge functionality to ensure components work together
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bridges.elizaos_opencog import AtomSpaceProvider, CogServerAction, PLNReasoner, OpenCogAgentTemplate


async def test_atomspace_provider():
    """Test AtomSpace provider basic functionality"""
    print("Testing AtomSpace Provider...")
    
    config = {'host': 'localhost', 'port': 17001}
    provider = AtomSpaceProvider(config)
    
    # Test initialization
    await provider.initialize()
    assert provider.atomspace is not None
    
    # Test knowledge storage
    knowledge = {
        'type': 'test_knowledge',
        'content': 'This is a test knowledge item',
        'timestamp': '2024-01-01'
    }
    result = await provider.store_knowledge(knowledge)
    assert result is True
    
    # Test knowledge query
    results = await provider.query_knowledge('test knowledge')
    assert len(results) > 0
    assert results[0]['data']['content'] == 'This is a test knowledge item'
    
    # Test reasoning
    context = {'type': 'financial', 'data': 'expense analysis'}
    reasoning_result = await provider.reason_about(context)
    assert 'conclusions' in reasoning_result
    assert reasoning_result['confidence'] > 0
    
    print("✓ AtomSpace Provider tests passed")


async def test_cogserver_action():
    """Test CogServer action functionality"""
    print("Testing CogServer Action...")
    
    action = CogServerAction('http://localhost:17020')
    
    # Test action execution
    action_data = {
        'type': 'query',
        'content': 'test query',
        'timestamp': '2024-01-01'
    }
    result = await action.execute(action_data)
    assert result['status'] == 'success'
    assert result['action_type'] == 'query'
    
    # Test event subscription
    await action.subscribe_to_events(['reasoning', 'memory_update'])
    assert hasattr(action, 'subscribed_events')
    assert 'reasoning' in action.subscribed_events
    
    print("✓ CogServer Action tests passed")


async def test_pln_reasoner():
    """Test PLN reasoner functionality"""
    print("Testing PLN Reasoner...")
    
    config = {'rules_file': 'mock_rules.scm'}
    reasoner = PLNReasoner(config)
    
    # Test inference
    premises = [
        {
            'type': 'financial_pattern',
            'name': 'grocery_spending',
            'confidence': 0.8
        },
        {
            'type': 'conversation',
            'content': 'user asking about expenses',
            'category': 'financial_query',
            'confidence': 0.9
        }
    ]
    
    conclusions = await reasoner.infer(premises)
    assert len(conclusions) == 2  # Should generate conclusions for both premises
    assert conclusions[0]['type'] == 'financial_prediction'
    assert conclusions[1]['type'] == 'response_intent'
    
    # Test conclusion validation
    test_conclusion = conclusions[0]
    confidence = await reasoner.validate_reasoning(test_conclusion)
    assert 0 <= confidence <= 1
    
    print("✓ PLN Reasoner tests passed")


async def test_opencog_agent_template():
    """Test OpenCog agent template integration"""
    print("Testing OpenCog Agent Template...")
    
    agent_config = {
        'atomspace': {'host': 'localhost'},
        'pln': {'rules_file': 'test_rules.scm'}
    }
    
    agent = OpenCogAgentTemplate(agent_config)
    
    # Test message processing
    message = "What are my recent expenses?"
    context = {'user_id': 'test_user', 'session_id': 'test_session'}
    
    response = await agent.process_message(message, context)
    assert isinstance(response, str)
    assert len(response) > 0
    
    print("✓ OpenCog Agent Template tests passed")


async def test_integration_workflow():
    """Test complete integration workflow"""
    print("Testing Complete Integration Workflow...")
    
    # Initialize components
    atomspace_config = {'host': 'localhost', 'port': 17001}
    agent_config = {
        'atomspace': atomspace_config,
        'pln': {'rules_file': 'integration_rules.scm'}
    }
    
    agent = OpenCogAgentTemplate(agent_config)
    
    # Simulate financial query workflow
    financial_query = "How much did I spend on groceries last month?"
    context = {
        'type': 'financial_query',
        'user_id': 'test_user',
        'domain': 'expenses'
    }
    
    # Process through the full cognitive pipeline
    response = await agent.process_message(financial_query, context)
    
    # Verify cognitive processing occurred
    assert "analysis" in response.lower() or "cognitive" in response.lower()
    
    print("✓ Integration Workflow tests passed")


async def main():
    """Run all integration tests"""
    print("=== ElizaOS-OpenCog Integration Framework Tests ===\n")
    
    try:
        await test_atomspace_provider()
        await test_cogserver_action()
        await test_pln_reasoner()
        await test_opencog_agent_template()
        await test_integration_workflow()
        
        print("\n=== All Tests Passed! ===")
        print("ElizaOS-OpenCog integration framework is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)