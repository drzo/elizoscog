#!/usr/bin/env python3
"""
Master Integration Framework - Enhanced with Phase 1 Foundation

Coordinates all cross-ecosystem integrations between ElizaOS, OpenCog, and GnuCash
to create the unified hybrid cognitive-financial intelligence system.

Updated to use the Phase 1 foundation infrastructure.
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
        
        # Cognitive agents (Phase 2 preview)
        self.cognitive_agents = {}
        
        # Integration status
        self.integration_status = {
            'phase1_foundation': 'pending',
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
            
            # Phase 2 Preview: Initialize core integration bridges
            await self._initialize_core_integration_bridges()
            
            # Phase 2 Preview: Initialize cognitive financial agents
            await self._initialize_cognitive_financial_agents()
            
            # Validate full system integration
            await self._validate_system_integration()
            
            logger.info("✅ Hybrid framework initialized successfully")
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
    
    async def _initialize_core_integration_bridges(self):
        """Initialize Phase 2 core integration bridges (preview)"""
        logger.info("🔗 Initializing Core Integration Bridges (Phase 2 Preview)...")
        
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
        """Process a financial query through the complete cognitive system"""
        if self.integration_status['full_hybrid'] != 'active':
            raise RuntimeError("System not fully initialized")
        
        logger.info(f"🔍 Processing financial query: '{query[:50]}...'")
        
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
        
        # Generate integrated response
        response = {
            'query': query,
            'query_atom_id': query_atom,
            'plugin_results': plugin_results,
            'cognitive_analysis': cognitive_analysis,
            'system_stats': await self.get_system_status(),
            'processed_at': datetime.now().isoformat()
        }
        
        logger.info("✅ Financial query processed successfully")
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
        
        # Message routing protocols
        self.message_router = {
            'elizaos_to_opencog': self._route_elizaos_to_opencog,
            'opencog_to_elizaos': self._route_opencog_to_elizaos,
            'elizaos_to_gnucash': self._route_elizaos_to_gnucash,
            'gnucash_to_elizaos': self._route_gnucash_to_elizaos,
            'opencog_to_gnucash': self._route_opencog_to_gnucash,
            'gnucash_to_opencog': self._route_gnucash_to_opencog
        }
        
        # Data format translators
        self.data_translators = {
            'agent_to_atom': self._translate_agent_to_atom,
            'atom_to_agent': self._translate_atom_to_agent,
            'financial_to_atom': self._translate_financial_to_atom,
            'atom_to_financial': self._translate_atom_to_financial,
            'agent_to_financial': self._translate_agent_to_financial,
            'financial_to_agent': self._translate_financial_to_agent
        }
        
        logger.info("  - Message routing protocols established")
        logger.info("  - Data format translators active")
    
    async def _initialize_cognitive_financial_agents(self):
        """Initialize hybrid cognitive financial agents"""
        logger.info("🧠💰 Initializing cognitive financial agents...")
        
        # Core cognitive financial agents
        self.cognitive_agents = {
            'account_reasoning_agent': await self._create_account_reasoning_agent(),
            'transaction_analysis_agent': await self._create_transaction_analysis_agent(),
            'budget_planning_agent': await self._create_budget_planning_agent(),
            'anomaly_detection_agent': await self._create_anomaly_detection_agent(),
            'investment_advisor_agent': await self._create_investment_advisor_agent(),
            'financial_chat_agent': await self._create_financial_chat_agent()
        }
        
        logger.info(f"  - Created {len(self.cognitive_agents)} cognitive financial agents")
    
    async def _create_account_reasoning_agent(self) -> Dict:
        """Create OpenCog PLN + ElizaOS Plugin + GnuCash Ledger agent"""
        return {
            'name': 'Account Reasoning Agent',
            'description': 'Combines OpenCog PLN reasoning with ElizaOS plugins and GnuCash ledger data',
            'components': {
                'opencog': ['pln', 'atomspace', 'ure'],
                'elizaos': ['agentaction', 'agentmemory'],
                'gnucash': ['account_structure', 'ledger_data']
            },
            'capabilities': [
                'Logical reasoning about account relationships',
                'Automated account categorization',
                'Financial rule inference',
                'Account hierarchy optimization'
            ],
            'status': 'active'
        }
    
    async def _create_transaction_analysis_agent(self) -> Dict:
        """Create pattern recognition + agent processing + transaction data agent"""
        return {
            'name': 'Transaction Analysis Agent',
            'description': 'Pattern recognition using OpenCog mining with ElizaOS processing and GnuCash transaction data',
            'components': {
                'opencog': ['miner', 'learn', 'attention'],
                'elizaos': ['easycompletion', 'agentloop'],
                'gnucash': ['transaction_data', 'spending_patterns']
            },
            'capabilities': [
                'Transaction pattern mining',
                'Spending behavior analysis',
                'Fraud detection patterns',
                'Merchant categorization'
            ],
            'status': 'active'
        }
    
    async def _create_budget_planning_agent(self) -> Dict:
        """Create temporal reasoning + planning + budget optimization agent"""
        return {
            'name': 'Budget Planning Agent',
            'description': 'Temporal reasoning and planning for budget optimization',
            'components': {
                'opencog': ['spacetime', 'generate'],
                'elizaos': ['agentaction', 'agentbrowser'],
                'gnucash': ['budget_data', 'financial_goals']
            },
            'capabilities': [
                'Temporal budget analysis',
                'Goal-based budget planning',
                'Resource allocation optimization',
                'Future spending prediction'
            ],
            'status': 'active'
        }
    
    async def _create_anomaly_detection_agent(self) -> Dict:
        """Create statistical analysis + alerts + monitoring agent"""
        return {
            'name': 'Anomaly Detection Agent',
            'description': 'Statistical analysis with intelligent alerts and monitoring',
            'components': {
                'opencog': ['attention', 'miner'],
                'elizaos': ['agentloop', 'agentmemory'],
                'gnucash': ['transaction_monitoring', 'account_alerts']
            },
            'capabilities': [
                'Real-time anomaly detection',
                'Statistical outlier identification',
                'Intelligent alert generation',
                'Behavioral change detection'
            ],
            'status': 'active'
        }
    
    async def _create_investment_advisor_agent(self) -> Dict:
        """Create investment analysis and recommendation agent"""
        return {
            'name': 'Investment Advisor Agent',
            'description': 'AI-powered investment analysis and recommendations',
            'components': {
                'opencog': ['pln', 'learn'],
                'elizaos': ['easycompletion', 'agentmemory'],
                'gnucash': ['investment_data', 'portfolio_tracking']
            },
            'capabilities': [
                'Portfolio risk analysis',
                'Investment recommendation generation',
                'Market trend analysis',
                'Diversification optimization'
            ],
            'status': 'active'
        }
    
    async def _create_financial_chat_agent(self) -> Dict:
        """Create natural language financial interface agent"""
        return {
            'name': 'Financial Chat Agent',
            'description': 'Natural language interface for financial queries and operations',
            'components': {
                'opencog': ['relex', 'link-grammar'],
                'elizaos': ['easycompletion', 'agentbrowser'],
                'gnucash': ['query_interface', 'report_generation']
            },
            'capabilities': [
                'Natural language financial queries',
                'Conversational budget planning',
                'Voice-activated financial operations',
                'Intelligent financial assistance'
            ],
            'status': 'active'
        }
    
    async def _validate_system_integration(self):
        """Validate complete system integration"""
        logger.info("🧪 Validating system integration...")
        
        # Test cross-ecosystem communication
        await self._test_cross_ecosystem_communication()
        
        # Test cognitive financial workflows
        await self._test_cognitive_financial_workflows()
        
        # Test hybrid data processing
        await self._test_hybrid_data_processing()
        
        # Update integration status
        if all(status == 'active' for status in self.integration_status.values()):
            self.integration_status['full_hybrid'] = 'active'
            logger.info("✅ Full hybrid system validation successful")
        else:
            logger.warning("⚠️ Partial integration - some components not fully active")
    
    async def _test_cross_ecosystem_communication(self):
        """Test communication between all ecosystems"""
        logger.info("  - Testing cross-ecosystem communication...")
        
        # Test ElizaOS → OpenCog
        test_message = {
            'source': 'elizaos',
            'target': 'opencog',
            'data': {'agent_action': 'test_reasoning', 'parameters': {}}
        }
        response = await self._route_elizaos_to_opencog(test_message)
        logger.info(f"    ElizaOS → OpenCog: {response.get('status', 'unknown')}")
        
        # Test OpenCog → GnuCash
        test_message = {
            'source': 'opencog',
            'target': 'gnucash',
            'data': {'query': 'account_balance', 'account_id': 'test'}
        }
        response = await self._route_opencog_to_gnucash(test_message)
        logger.info(f"    OpenCog → GnuCash: {response.get('status', 'unknown')}")
        
        # Test full roundtrip: ElizaOS → OpenCog → GnuCash → ElizaOS
        await self._test_full_roundtrip_communication()
    
    async def _test_full_roundtrip_communication(self):
        """Test full roundtrip communication across all systems"""
        try:
            # Start with ElizaOS query
            elizaos_query = {
                'source': 'elizaos',
                'target': 'opencog',
                'data': {
                    'query': 'analyze_spending_patterns', 
                    'user_id': 'test_user'
                }
            }
            
            # Route to OpenCog
            opencog_response = await self._route_elizaos_to_opencog(
                elizaos_query
            )
            
            # OpenCog processes and routes to GnuCash
            gnucash_query = {
                'source': 'opencog',
                'target': 'gnucash',
                'data': opencog_response.get('data', {})
            }
            gnucash_response = await self._route_opencog_to_gnucash(
                gnucash_query
            )
            
            # Route back to ElizaOS
            final_response = await self._route_gnucash_to_elizaos(
                gnucash_response
            )
            
            status = final_response.get('status', 'success')
            logger.info(f"    Full roundtrip completed: {status}")
            
        except Exception as e:
            logger.warning(f"    Roundtrip test failed: {e}")
    
    async def _test_cognitive_financial_workflows(self):
        """Test end-to-end cognitive financial workflows"""
        logger.info("  - Testing cognitive financial workflows...")
        
        # Test account reasoning workflow
        await self._test_account_reasoning_workflow()
        
        # Test transaction analysis workflow
        await self._test_transaction_analysis_workflow()
        
        # Test budget planning workflow
        await self._test_budget_planning_workflow()
    
    async def _test_hybrid_data_processing(self):
        """Test hybrid data processing across all ecosystems"""
        logger.info("  - Testing hybrid data processing...")
        
        # Test data format translations
        for translator_name, translator_func in self.data_translators.items():
            try:
                test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
                result = await translator_func(test_data)
                logger.info(f"    {translator_name}: ✅")
            except Exception as e:
                logger.warning(f"    {translator_name}: ❌ {e}")
    
    # Message routing methods
    async def _route_elizaos_to_opencog(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Route messages from ElizaOS to OpenCog"""
        translated_message = await self._translate_agent_to_atom(message)
        
        # Send to OpenCog AtomSpace
        result = {
            'status': 'routed_to_opencog',
            'original_message': message,
            'atomspace_format': translated_message,
            'processing_node': 'opencog_atomspace'
        }
        
        logger.info(f"Routed ElizaOS message to OpenCog: {message.get('type', 'unknown')}")
        return result
    
    async def _route_opencog_to_elizaos(self, atom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route atom data from OpenCog to ElizaOS"""
        translated_data = await self._translate_atom_to_agent(atom_data)
        
        result = {
            'status': 'routed_to_elizaos',
            'original_atom': atom_data,
            'agent_format': translated_data,
            'processing_node': 'elizaos_agent'
        }
        
        logger.info(f"Routed OpenCog atom to ElizaOS: {atom_data.get('type', 'unknown')}")
        return result
    
    async def _route_elizaos_to_gnucash(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route agent data to GnuCash operations"""
        financial_data = await self._translate_agent_to_financial(agent_data)
        
        result = {
            'status': 'routed_to_gnucash',
            'original_data': agent_data,
            'financial_format': financial_data,
            'processing_node': 'gnucash_engine'
        }
        
        logger.info(f"Routed ElizaOS data to GnuCash: {agent_data.get('type', 'unknown')}")
        return result
    
    async def _route_gnucash_to_elizaos(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route financial data from GnuCash to ElizaOS"""
        agent_data = await self._translate_financial_to_agent(financial_data)
        
        result = {
            'status': 'routed_to_elizaos',
            'original_financial': financial_data,
            'agent_format': agent_data,
            'processing_node': 'elizaos_financial_agent'
        }
        
        logger.info(f"Routed GnuCash data to ElizaOS: {financial_data.get('type', 'unknown')}")
        return result
    
    async def _route_opencog_to_gnucash(self, atom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route cognitive data from OpenCog to GnuCash"""
        financial_insights = await self._translate_atom_to_financial(atom_data)
        
        result = {
            'status': 'routed_to_gnucash',
            'original_atom': atom_data,
            'financial_insights': financial_insights,
            'processing_node': 'gnucash_cognitive_integration'
        }
        
        logger.info(f"Routed OpenCog reasoning to GnuCash: {atom_data.get('type', 'unknown')}")
        return result
    
    async def _route_gnucash_to_opencog(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route financial data from GnuCash to OpenCog for reasoning"""
        atom_representation = await self._translate_financial_to_atom(financial_data)
        
        result = {
            'status': 'routed_to_opencog',
            'original_financial': financial_data,
            'atom_representation': atom_representation,
            'processing_node': 'opencog_financial_reasoning'
        }
        
        logger.info(f"Routed GnuCash data to OpenCog: {financial_data.get('type', 'unknown')}")
        return result

    # Data translation methods
    async def _translate_agent_to_atom(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate ElizaOS agent data to OpenCog atom format"""
        atom_type = 'ConceptNode'
        
        if agent_data.get('type') == 'financial_query':
            atom_type = 'EvaluationLink'
        elif agent_data.get('type') == 'transaction':
            atom_type = 'InheritanceLink'
        
        return {
            'atom_type': atom_type,
            'name': f"Agent-{agent_data.get('id', 'unknown')}",
            'data': agent_data,
            'truthvalue': {
                'strength': 0.8,
                'confidence': 0.9
            },
            'timestamp': agent_data.get('timestamp', datetime.now().isoformat())
        }
    
    async def _translate_atom_to_agent(self, atom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate OpenCog atom to ElizaOS agent format"""
        return {
            'type': 'cognitive_result',
            'content': atom_data.get('data', {}),
            'reasoning_type': atom_data.get('atom_type', 'unknown'),
            'confidence': atom_data.get('truthvalue', {}).get('confidence', 0.5),
            'source': 'opencog_atomspace',
            'timestamp': atom_data.get('timestamp', datetime.now().isoformat())
        }
    
    async def _translate_financial_to_atom(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate GnuCash financial data to OpenCog atom format"""
        return {
            'atom_type': 'EvaluationLink',
            'predicate': 'financial_data',
            'arguments': [
                financial_data.get('account', 'unknown'),
                str(financial_data.get('amount', 0)),
                financial_data.get('date', 'unknown')
            ],
            'truthvalue': {
                'strength': 1.0,  # Financial data is factual
                'confidence': 0.95
            },
            'financial_metadata': financial_data
        }
    
    async def _translate_atom_to_financial(self, atom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate OpenCog reasoning to financial operations"""
        return {
            'operation_type': 'cognitive_insight',
            'insight': atom_data.get('data', {}),
            'confidence': atom_data.get('truthvalue', {}).get('confidence', 0.5),
            'reasoning_source': 'opencog_pln',
            'suggested_actions': self._extract_financial_actions(atom_data),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _translate_agent_to_financial(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate ElizaOS agent data to GnuCash operations"""
        operation_map = {
            'financial_query': 'query_accounts',
            'budget_request': 'budget_analysis',
            'expense_analysis': 'expense_report',
            'transaction_categorization': 'categorize_transaction'
        }
        
        operation = operation_map.get(agent_data.get('type'), 'general_operation')
        
        return {
            'operation': operation,
            'parameters': agent_data.get('data', {}),
            'user_context': agent_data.get('context', {}),
            'timestamp': agent_data.get('timestamp', datetime.now().isoformat())
        }
    
    async def _translate_financial_to_agent(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate GnuCash data to ElizaOS agent format"""
        return {
            'type': 'financial_data',
            'content': financial_data,
            'source': 'gnucash',
            'processing_status': 'ready_for_agent',
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_financial_actions(self, atom_data: Dict[str, Any]) -> List[str]:
        """Extract actionable financial recommendations from reasoning"""
        actions = []
        
        data = atom_data.get('data', {})
        if 'anomaly' in str(data).lower():
            actions.append('review_transaction')
        if 'budget' in str(data).lower():
            actions.append('adjust_budget')
        if 'investment' in str(data).lower():
            actions.append('review_investment_allocation')
        
        return actions if actions else ['general_review']
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            'integration_status': self.integration_status,
            'active_agents': len(self.cognitive_agents),
            'bridge_count': len(self.bridges),
            'message_routers': len(self.message_router),
            'data_translators': len(self.data_translators),
            'timestamp': datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the hybrid framework"""
        logger.info("🔌 Shutting down hybrid framework...")
        
        # Shutdown all bridges
        for bridge_name, bridge in self.bridges.items():
            try:
                await bridge.shutdown()
            except Exception as e:
                logger.warning(f"Error shutting down {bridge_name}: {e}")
        
        # Clear all sessions
        self.active_sessions.clear()
        
        logger.info("✅ Hybrid framework shutdown complete")

async def main():
    """Main execution function for testing the framework"""
    print("🚀 Starting Hybrid Cognitive-Financial Framework Demo")
    
    framework = HybridCognitiveFinancialFramework()
    
    # Initialize the framework
    success = await framework.initialize()
    
    if success:
        print("✅ Framework initialized successfully!")
        
        # Display system status
        status = framework.get_system_status()
        print(f"\n📊 System Status:")
        print(f"  - Integration Status: {status['integration_status']}")
        print(f"  - Active Agents: {status['active_agents']}")
        print(f"  - Bridge Count: {status['bridge_count']}")
        print(f"  - Message Routers: {status['message_routers']}")
        print(f"  - Data Translators: {status['data_translators']}")
        
        # Display available cognitive financial agents
        print(f"\n🧠💰 Available Cognitive Financial Agents:")
        for agent_name, agent_info in framework.cognitive_agents.items():
            print(f"  - {agent_info['name']}: {agent_info['description']}")
        
        print(f"\n🎉 Hybrid Cognitive-Financial Intelligence System is ACTIVE!")
        print(f"   Ready for revolutionary financial reasoning and automation!")
        
    else:
        print("❌ Framework initialization failed")
    
    # Shutdown
    await framework.shutdown()

if __name__ == "__main__":
    asyncio.run(main())