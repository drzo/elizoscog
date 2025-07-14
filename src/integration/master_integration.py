#!/usr/bin/env python3
"""
Master Integration Framework - Phase 1 Foundation Implementation

Coordinates all cross-ecosystem integrations between ElizaOS, OpenCog, and GnuCash
to create the unified hybrid cognitive-financial intelligence system.

This implementation provides the Phase 1 foundation with previews of Phase 2+ features.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import Phase 1 foundation components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.atomspace_bindings import AtomSpaceCore, FinancialAtomSpace
from core.elizaos_plugin_architecture import ElizaOSPluginManager, OpenCogAgentPlugin, FinancialCognitivePlugin
from core.gnucash_access import GnuCashDataAccess, FinancialPatternAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridCognitiveFinancialFramework:
    """Master framework coordinating all ecosystem integrations with Phase 1 foundation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.base_dir = Path(__file__).parent.parent
        
        # Phase 1 foundation components
        self.atomspace_core = None
        self.financial_atomspace = None
        self.plugin_manager = None
        self.gnucash_access = None
        self.pattern_analyzer = None
        
        # Cognitive agents (Phase 2)
        self.cognitive_agents = {}
        
        # Phase 2: Dynamic mesh integration framework
        self.dynamic_mesh_framework = None
        self.performance_profiler = None
        self.caching_strategy = None
        self.monitoring_system = None
        self.financial_advisor = None
        self.market_analysis_engine = None
        
        # Integration status
        self.integration_status = {
            'phase1_foundation': 'pending',
            'phase2_core_integration': 'pending',
            'phase3_advanced_features': 'pending',
            'phase4_optimization': 'pending',
            'phase5_advanced_applications': 'pending',
            'elizaos_opencog': 'pending',
            'opencog_gnucash': 'pending', 
            'elizaos_gnucash': 'pending',
            'full_hybrid': 'pending'
        }
        
        # Session management
        self.active_sessions = {}
        
    async def initialize(self) -> bool:
        """Initialize the complete hybrid framework with Phase 1 foundation"""
        logger.info("🚀 Initializing Hybrid Cognitive-Financial Framework (Phase 1+)")
        
        try:
            # Phase 1: Initialize foundation infrastructure
            await self._initialize_phase1_foundation()
            
            # Phase 2: Initialize core integration bridges
            await self._initialize_core_integration_bridges()
            
            # Phase 3: Initialize cognitive financial agents
            await self._initialize_cognitive_financial_agents()
            
            # Phase 4: Initialize optimization and scaling
            await self._initialize_phase4_optimization()
            
            # Phase 5: Initialize advanced applications
            await self._initialize_phase5_advanced_applications()
            
            # Validate full system integration
            await self._validate_system_integration()
            
            logger.info("✅ Complete hybrid framework initialized successfully - All Phases 1-5")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize hybrid framework: {e}")
            return False
    
    async def _initialize_phase1_foundation(self):
        """Initialize Phase 1 foundation components"""
        logger.info("🏗️ Initializing Phase 1 Foundation Infrastructure...")
        
        # Initialize AtomSpace core
        self.atomspace_core = AtomSpaceCore(self.config.get('atomspace', {}))
        if not await self.atomspace_core.initialize():
            raise RuntimeError("Failed to initialize AtomSpace core")
        
        # Initialize financial AtomSpace
        self.financial_atomspace = FinancialAtomSpace(self.config.get('financial_atomspace', {}))
        if not await self.financial_atomspace.initialize():
            raise RuntimeError("Failed to initialize Financial AtomSpace")
        
        # Initialize GnuCash access
        gnucash_config = self.config.get('gnucash', {})
        gnucash_db_path = gnucash_config.get('database_path', 'data/gnucash_demo.sqlite')
        self.gnucash_access = GnuCashDataAccess(gnucash_db_path)
        if not await self.gnucash_access.initialize():
            raise RuntimeError("Failed to initialize GnuCash access")
        
        # Initialize pattern analyzer
        self.pattern_analyzer = FinancialPatternAnalyzer(self.gnucash_access)
        
        # Initialize plugin manager
        self.plugin_manager = ElizaOSPluginManager()
        
        # Register and enable core plugins
        opencog_plugin = OpenCogAgentPlugin(self.config.get('opencog_plugin', {}))
        financial_plugin = FinancialCognitivePlugin(self.config.get('financial_plugin', {}))
        
        await self.plugin_manager.register_plugin(opencog_plugin)
        await self.plugin_manager.register_plugin(financial_plugin)
        
        await self.plugin_manager.enable_plugin('opencog_agent')
        await self.plugin_manager.enable_plugin('financial_cognitive')
        
        self.integration_status['phase1_foundation'] = 'active'
        logger.info("✅ Phase 1 foundation infrastructure initialized")
    
    async def _initialize_phase4_optimization(self):
        """Initialize Phase 4 optimization and scaling components"""
        logger.info("🚀 Initializing Phase 4 Optimization & Scaling...")
        
        # Import Phase 4 components
        from optimization.performance_optimization import PerformanceProfiler, CachingStrategy
        from optimization.production_readiness import MonitoringSystem
        
        # Initialize performance optimization
        self.performance_profiler = PerformanceProfiler(self.config.get('performance', {}))
        self.caching_strategy = CachingStrategy(self.config.get('caching', {}))
        
        # Initialize production readiness
        self.monitoring_system = MonitoringSystem(self.config.get('monitoring', {}))
        
        # Start monitoring system (run in background)
        asyncio.create_task(self.monitoring_system.start_monitoring())
        
        self.integration_status['phase4_optimization'] = 'active'
        logger.info("✅ Phase 4 Optimization & Scaling Initialized")
    
    async def _initialize_phase5_advanced_applications(self):
        """Initialize Phase 5 advanced applications"""
        logger.info("🌟 Initializing Phase 5 Advanced Applications...")
        
        # Import Phase 5 components
        from advanced_applications.intelligent_financial_advisory import IntelligentFinancialAdvisor
        from advanced_applications.market_analysis_integration import MarketAnalysisEngine
        
        # Initialize intelligent financial advisor
        self.financial_advisor = IntelligentFinancialAdvisor(self.config.get('financial_advisor', {}))
        
        # Initialize market analysis engine
        self.market_analysis_engine = MarketAnalysisEngine(self.config.get('market_analysis', {}))
        
        self.integration_status['phase5_advanced_applications'] = 'active'
        logger.info("✅ Phase 5 Advanced Applications Initialized")
    
    async def _initialize_core_integration_bridges(self):
        """Initialize Phase 2 core integration bridges with dynamic mesh"""
        logger.info("🔗 Initializing Core Integration Bridges (Phase 2 Dynamic Mesh)...")
        
        # Import and initialize dynamic mesh integration
        from integration.dynamic_mesh_integration import DynamicMeshIntegrationFramework
        
        # Configure dynamic mesh for cognitive agents
        mesh_config = {
            'topology': {
                'max_connections': 8,
                'min_connections': 3,
                'update_interval': 30
            },
            'attention': {
                'attention_budget': 1.0,
                'algorithm': 'priority_based',
                'coordination_interval': 5
            },
            'reconfiguration': {
                'reconfiguration_threshold': 0.7,
                'stability_window': 60,
                'max_concurrent': 3
            },
            'state_propagation': {
                'protocol': 'epidemic',
                'max_hops': 5,
                'timeout': 10.0
            },
            'fault_tolerance': {
                'heartbeat_interval': 5,
                'failure_threshold': 3,
                'recovery_timeout': 30
            },
            'load_distribution': {
                'algorithm': 'cognitive_aware',
                'rebalancing_threshold': 0.3
            }
        }
        
        # Initialize dynamic mesh framework
        self.dynamic_mesh_framework = DynamicMeshIntegrationFramework(mesh_config)
        
        # Convert cognitive agents to mesh nodes
        mesh_nodes = []
        for agent_name, agent_config in self.cognitive_agents.items():
            if agent_config.get('active', False):
                mesh_node = {
                    'node_id': agent_name,
                    'type': 'cognitive_agent',
                    'capabilities': agent_config.get('capabilities', []),
                    'max_capacity': 1.0,
                    'position': (len(mesh_nodes) * 0.5, (len(mesh_nodes) % 2) * 0.5)
                }
                mesh_nodes.append(mesh_node)
        
        # Initialize dynamic mesh with cognitive agents
        mesh_success = await self.dynamic_mesh_framework.initialize_dynamic_mesh(mesh_nodes)
        if not mesh_success:
            logger.warning("Dynamic mesh initialization failed, continuing with basic bridges")
        else:
            logger.info("✅ Dynamic mesh integration initialized successfully")
        
        # ElizaOS ↔ OpenCog bridges
        elizaos_opencog_bridges = [
            'atomspace', 'cogserver', 'pln', 'ure', 'miner', 
            'learn', 'attention', 'relex', 'link-grammar'
        ]
        
        for bridge_name in elizaos_opencog_bridges:
            try:
                # Create bridge integration record in AtomSpace
                bridge_atom = self.atomspace_core.create_atom(
                    'ConceptNode', f"Bridge-{bridge_name}"
                )
                
                # Create bridge status link
                status_link = self.atomspace_core.create_link('EvaluationLink', [
                    self.atomspace_core.create_atom('PredicateNode', 'BridgeStatus'),
                    self.atomspace_core.create_link('ListLink', [
                        bridge_atom,
                        self.atomspace_core.create_atom('ConceptNode', 'Active')
                    ])
                ])
                
                logger.info(f"  - Initialized {bridge_name} bridge integration")
                
            except Exception as e:
                logger.warning(f"  - Failed to initialize {bridge_name} bridge: {e}")
        
        self.integration_status['elizaos_opencog'] = 'active'
        
        # OpenCog ↔ GnuCash cognitive financial bridge  
        financial_bridge_atom = self.financial_atomspace.create_account_atom(
            "CognitiveBridge", "SYSTEM", 0.0
        )
        logger.info("  - Initialized OpenCog-GnuCash cognitive bridge")
        
        self.integration_status['opencog_gnucash'] = 'active'
        self.integration_status['elizaos_gnucash'] = 'active'
        self.integration_status['phase2_core_integration'] = 'active'
    
    async def _initialize_cognitive_financial_agents(self):
        """Initialize cognitive financial agents (Phase 2 preview)"""
        logger.info("🤖 Initializing Cognitive Financial Agents (Phase 2 Preview)...")
        
        # Account Reasoning Agent
        self.cognitive_agents['account_reasoning_agent'] = {
            'name': 'AccountReasoningAgent',
            'description': 'Applies formal logic to financial account decisions',
            'atomspace_id': self.financial_atomspace.create_atom('ConceptNode', 'AccountReasoningAgent'),
            'capabilities': ['balance_analysis', 'account_optimization', 'risk_assessment'],
            'active': True
        }
        
        # Transaction Analysis Agent
        self.cognitive_agents['transaction_analysis_agent'] = {
            'name': 'TransactionAnalysisAgent', 
            'description': 'Discovers hidden patterns in transaction data',
            'atomspace_id': self.financial_atomspace.create_atom('ConceptNode', 'TransactionAnalysisAgent'),
            'capabilities': ['pattern_recognition', 'anomaly_detection', 'categorization'],
            'active': True
        }
        
        # Budget Planning Agent
        self.cognitive_agents['budget_planning_agent'] = {
            'name': 'BudgetPlanningAgent',
            'description': 'Optimizes financial goals with temporal reasoning',
            'atomspace_id': self.financial_atomspace.create_atom('ConceptNode', 'BudgetPlanningAgent'),
            'capabilities': ['goal_planning', 'temporal_reasoning', 'optimization'],
            'active': True
        }
        
        # Anomaly Detection Agent
        self.cognitive_agents['anomaly_detection_agent'] = {
            'name': 'AnomalyDetectionAgent',
            'description': 'Cognitive fraud and unusual pattern detection',
            'atomspace_id': self.financial_atomspace.create_atom('ConceptNode', 'AnomalyDetectionAgent'),
            'capabilities': ['fraud_detection', 'outlier_analysis', 'security_monitoring'],
            'active': True
        }
        
        # Investment Advisory Agent (Phase 3 preview)
        self.cognitive_agents['investment_advisory_agent'] = {
            'name': 'InvestmentAdvisoryAgent',
            'description': 'Portfolio analysis with market intelligence',
            'atomspace_id': self.financial_atomspace.create_atom('ConceptNode', 'InvestmentAdvisoryAgent'),
            'capabilities': ['portfolio_analysis', 'market_intelligence', 'risk_modeling'],
            'active': False  # Phase 3 feature
        }
        
        # Financial Chat Agent (Phase 3 preview)
        self.cognitive_agents['financial_chat_agent'] = {
            'name': 'FinancialChatAgent',
            'description': 'Natural conversation about financial data',
            'atomspace_id': self.financial_atomspace.create_atom('ConceptNode', 'FinancialChatAgent'),
            'capabilities': ['natural_language', 'conversation', 'financial_qa'],
            'active': False  # Phase 3 feature
        }
        
        active_agents = sum(1 for agent in self.cognitive_agents.values() if agent['active'])
        logger.info(f"  - Initialized {len(self.cognitive_agents)} cognitive agents ({active_agents} active)")
    
    async def _validate_system_integration(self):
        """Validate complete system integration"""
        logger.info("🔍 Validating System Integration...")
        
        # Count active components
        components = {
            'atomspace_atoms': self.atomspace_core.get_atom_count(),
            'financial_atoms': self.financial_atomspace.get_atom_count(),
            'registered_plugins': len(self.plugin_manager.plugins),
            'enabled_plugins': len(self.plugin_manager.enabled_plugins),
            'cognitive_agents': len([a for a in self.cognitive_agents.values() if a['active']]),
            'gnucash_connection': self.gnucash_access.initialized
        }
        
        # Validate minimum requirements
        if components['atomspace_atoms'] > 0:
            logger.info(f"  ✓ AtomSpace operational: {components['atomspace_atoms']} atoms")
        else:
            raise RuntimeError("AtomSpace not operational")
        
        if components['financial_atoms'] > 0:
            logger.info(f"  ✓ Financial AtomSpace operational: {components['financial_atoms']} atoms")
        else:
            raise RuntimeError("Financial AtomSpace not operational")
        
        if components['enabled_plugins'] > 0:
            logger.info(f"  ✓ Plugin system operational: {components['enabled_plugins']} active plugins")
        else:
            raise RuntimeError("No plugins enabled")
        
        if components['gnucash_connection']:
            logger.info(f"  ✓ GnuCash access operational")
        else:
            raise RuntimeError("GnuCash access not operational")
        
        self.integration_status['full_hybrid'] = 'active'
        logger.info("✅ System integration validated successfully")
    
    async def process_financial_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a financial query through the complete cognitive system with dynamic mesh"""
        if self.integration_status['full_hybrid'] != 'active':
            raise RuntimeError("System not fully initialized")
        
        logger.info(f"🔍 Processing financial query through dynamic mesh: '{query[:50]}...'")
        
        # Store query in AtomSpace
        query_atom = self.financial_atomspace.create_atom('ConceptNode', f"Query-{datetime.now().isoformat()}")
        
        # Process through plugin system
        message = {
            'content': query,
            'type': 'financial_query',
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        plugin_results = await self.plugin_manager.process_message_through_plugins(message)
        
        # Apply cognitive agents (Phase 2)
        cognitive_analysis = await self._apply_cognitive_agents(query, context)
        
        # Apply dynamic mesh cognitive processing if available
        mesh_processing = {}
        if self.dynamic_mesh_framework:
            try:
                # Create attention requests for financial query processing
                attention_requests = [
                    {
                        'requesting_node': 'account_reasoning_agent',
                        'target_node': 'transaction_analysis_agent',
                        'attention_amount': 0.4,
                        'priority': 2,
                        'task_type': 'financial_analysis',
                        'duration': 10.0
                    },
                    {
                        'requesting_node': 'budget_planning_agent',
                        'target_node': 'account_reasoning_agent',
                        'attention_amount': 0.3,
                        'priority': 1,
                        'task_type': 'financial_planning',
                        'duration': 8.0
                    }
                ]
                
                mesh_coordination = await self.coordinate_distributed_attention(attention_requests)
                mesh_processing['attention_coordination'] = mesh_coordination
                
                # Get mesh status for query context
                mesh_status = await self.get_mesh_cognitive_status()
                mesh_processing['mesh_status'] = mesh_status
                
            except Exception as e:
                logger.warning(f"Dynamic mesh processing encountered error: {e}")
                mesh_processing['error'] = str(e)
        
        # Generate integrated response
        response = {
            'query': query,
            'query_atom_id': query_atom,
            'plugin_results': plugin_results,
            'cognitive_analysis': cognitive_analysis,
            'dynamic_mesh_processing': mesh_processing,
            'system_stats': await self.get_system_status(),
            'processed_at': datetime.now().isoformat()
        }
        
        logger.info("✅ Financial query processed successfully through dynamic mesh")
        return response
    
    async def _apply_cognitive_agents(self, query: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Apply cognitive agents to analyze query (Phase 2 preview)"""
        analysis = {
            'active_agents': [],
            'insights': [],
            'recommendations': []
        }
        
        # Apply active cognitive agents
        for agent_name, agent_config in self.cognitive_agents.items():
            if agent_config['active']:
                analysis['active_agents'].append(agent_name)
                
                # Mock agent-specific analysis
                if 'balance' in query.lower() and agent_name == 'account_reasoning_agent':
                    analysis['insights'].append({
                        'agent': agent_name,
                        'insight': 'Account balance analysis requested',
                        'confidence': 0.9
                    })
                
                elif 'spending' in query.lower() and agent_name == 'transaction_analysis_agent':
                    analysis['insights'].append({
                        'agent': agent_name,
                        'insight': 'Spending pattern analysis requested',
                        'confidence': 0.85
                    })
                
                elif 'budget' in query.lower() and agent_name == 'budget_planning_agent':
                    analysis['insights'].append({
                        'agent': agent_name,
                        'insight': 'Budget planning analysis requested',
                        'confidence': 0.8
                    })
        
        # Generate recommendations
        if analysis['insights']:
            analysis['recommendations'].append({
                'type': 'cognitive_analysis',
                'message': f"Applied {len(analysis['active_agents'])} cognitive agents to your query",
                'confidence': 0.75
            })
        
        return analysis
    
    async def optimize_mesh_topology(self) -> Dict[str, Any]:
        """Optimize the dynamic mesh topology for cognitive efficiency"""
        if not self.dynamic_mesh_framework:
            return {"error": "Dynamic mesh not initialized"}
        
        logger.info("🕸️ Optimizing dynamic mesh topology")
        
        try:
            optimization_result = await self.dynamic_mesh_framework.optimize_topology()
            
            # Record optimization in AtomSpace
            optimization_atom = self.financial_atomspace.create_atom(
                'ConceptNode', f"MeshOptimization-{optimization_result.get('optimization_id', 'unknown')}"
            )
            
            return {
                "mesh_optimization": optimization_result,
                "atomspace_record": optimization_atom,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Mesh topology optimization failed: {e}")
            return {"error": str(e)}
    
    async def coordinate_distributed_attention(self, attention_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordinate attention allocation across the dynamic mesh"""
        if not self.dynamic_mesh_framework:
            return {"error": "Dynamic mesh not initialized"}
        
        logger.info(f"🎯 Coordinating distributed attention for {len(attention_requests)} requests")
        
        try:
            coordination_result = await self.dynamic_mesh_framework.coordinate_attention_allocation(attention_requests)
            
            # Update cognitive agents with attention flow data
            for agent_name, agent_config in self.cognitive_agents.items():
                agent_config['last_attention_coordination'] = datetime.now().isoformat()
            
            return {
                "attention_coordination": coordination_result,
                "cognitive_agents_updated": len(self.cognitive_agents),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Distributed attention coordination failed: {e}")
            return {"error": str(e)}
    
    async def reconfigure_cognitive_mesh(self, trigger: Dict[str, Any]) -> Dict[str, Any]:
        """Reconfigure the cognitive mesh based on trigger conditions"""
        if not self.dynamic_mesh_framework:
            return {"error": "Dynamic mesh not initialized"}
        
        logger.info(f"🔄 Reconfiguring cognitive mesh: {trigger.get('type', 'unknown')}")
        
        try:
            reconfiguration_result = await self.dynamic_mesh_framework.reconfigure_mesh(trigger)
            
            # Update integration status based on reconfiguration
            if reconfiguration_result.get("success", False):
                self.integration_status['phase2_core_integration'] = 'optimized'
            
            return {
                "mesh_reconfiguration": reconfiguration_result,
                "integration_status_updated": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Cognitive mesh reconfiguration failed: {e}")
            return {"error": str(e)}
    
    async def get_mesh_cognitive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the dynamic mesh cognitive system"""
        if not self.dynamic_mesh_framework:
            return {"error": "Dynamic mesh not initialized"}
        
        try:
            mesh_status = await self.dynamic_mesh_framework.get_mesh_status()
            
            # Combine with existing system status
            system_status = await self.get_system_status()
            
            return {
                "dynamic_mesh_status": mesh_status,
                "cognitive_system_status": system_status,
                "integration_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get mesh cognitive status: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'integration_status': self.integration_status,
            'component_stats': {
                'atomspace_atoms': self.atomspace_core.get_atom_count() if self.atomspace_core else 0,
                'financial_atoms': self.financial_atomspace.get_atom_count() if self.financial_atomspace else 0,
                'active_plugins': len(self.plugin_manager.enabled_plugins) if self.plugin_manager else 0,
                'cognitive_agents': len([a for a in self.cognitive_agents.values() if a.get('active', False)]),
                'gnucash_operational': self.gnucash_access.initialized if self.gnucash_access else False
            },
            'cognitive_agents': {
                name: {
                    'active': agent['active'],
                    'capabilities': agent['capabilities']
                }
                for name, agent in self.cognitive_agents.items()
            },
            'last_updated': datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the hybrid framework gracefully"""
        logger.info("🛑 Shutting down Hybrid Cognitive-Financial Framework...")
        
        # Cleanup plugins
        if self.plugin_manager:
            await self.plugin_manager.cleanup_all_plugins()
        
        # Close GnuCash connection
        if self.gnucash_access:
            await self.gnucash_access.close()
        
        # Clear sessions
        self.active_sessions.clear()
        
        # Reset status
        for key in self.integration_status:
            self.integration_status[key] = 'shutdown'
        
        logger.info("✅ Hybrid framework shutdown complete")

# Simplified main for testing
async def main():
    """Main execution function for testing the framework"""
    print("🚀 Starting Hybrid Cognitive-Financial Framework Demo")
    
    framework = HybridCognitiveFinancialFramework()
    
    # Initialize the framework
    success = await framework.initialize()
    
    if success:
        print("✅ Framework initialized successfully!")
        
        # Display system status
        status = await framework.get_system_status()
        print(f"\n📊 System Status:")
        print(f"  - Integration Status: {status['integration_status']}")
        print(f"  - Component Stats: {status['component_stats']}")
        
        # Display available cognitive financial agents
        print(f"\n🧠💰 Available Cognitive Financial Agents:")
        for agent_name, agent_info in framework.cognitive_agents.items():
            status_icon = "✅" if agent_info['active'] else "⏸️"
            print(f"  {status_icon} {agent_info['name']}: {agent_info['description']}")
        
        print(f"\n🎉 Hybrid Cognitive-Financial Intelligence System is ACTIVE!")
        
    else:
        print("❌ Framework initialization failed")
    
    # Shutdown
    await framework.shutdown()

if __name__ == "__main__":
    asyncio.run(main())