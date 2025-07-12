#!/usr/bin/env python3
"""
ElizaOS Plugin Architecture for OpenCog Integration
Phase 1: Core infrastructure for multi-agent cognitive architecture
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod

from .atomspace_bindings import AtomSpaceCore, FinancialAtomSpace

logger = logging.getLogger(__name__)

class ElizaOSPlugin(ABC):
    """Base class for ElizaOS plugins integrating with OpenCog"""
    
    def __init__(self, plugin_name: str, config: Dict[str, Any]):
        self.plugin_name = plugin_name
        self.config = config
        self.enabled = False
        self.atomspace = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message through this plugin"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        pass


class OpenCogAgentPlugin(ElizaOSPlugin):
    """Plugin for OpenCog agent integration with ElizaOS"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("opencog_agent", config)
        self.atomspace_core = None
        self.reasoning_agents = {}
        
    async def initialize(self) -> bool:
        """Initialize OpenCog agent plugin"""
        try:
            logger.info("Initializing OpenCog Agent Plugin...")
            
            # Initialize AtomSpace core
            atomspace_config = self.config.get('atomspace', {})
            self.atomspace_core = AtomSpaceCore(atomspace_config)
            
            if not await self.atomspace_core.initialize():
                raise RuntimeError("Failed to initialize AtomSpace core")
            
            # Initialize reasoning agents
            await self._initialize_reasoning_agents()
            
            self.enabled = True
            logger.info("✅ OpenCog Agent Plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenCog Agent Plugin: {e}")
            return False
    
    async def _initialize_reasoning_agents(self):
        """Initialize various reasoning agents"""
        
        # Pattern Recognition Agent
        self.reasoning_agents['pattern_recognition'] = {
            'name': 'PatternRecognitionAgent',
            'description': 'Identifies patterns in data using AtomSpace',
            'active': True
        }
        
        # Logic Reasoning Agent  
        self.reasoning_agents['logic_reasoning'] = {
            'name': 'LogicReasoningAgent',
            'description': 'Applies PLN logical reasoning',
            'active': True
        }
        
        # Memory Agent
        self.reasoning_agents['memory'] = {
            'name': 'MemoryAgent',
            'description': 'Manages long-term and working memory',
            'active': True
        }
        
        logger.info(f"Initialized {len(self.reasoning_agents)} reasoning agents")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process message through OpenCog reasoning pipeline"""
        if not self.enabled:
            return {'error': 'Plugin not enabled'}
        
        try:
            # Extract message content
            content = message.get('content', '')
            message_type = message.get('type', 'text')
            context = message.get('context', {})
            
            # Store message in AtomSpace
            message_atom = self.atomspace_core.create_atom(
                'ConceptNode', f"Message-{datetime.now().isoformat()}"
            )
            
            # Apply reasoning agents
            reasoning_results = []
            
            # Pattern recognition
            if 'pattern_recognition' in self.reasoning_agents:
                pattern_result = await self._apply_pattern_recognition(content, context)
                reasoning_results.append(pattern_result)
            
            # Logic reasoning
            if 'logic_reasoning' in self.reasoning_agents:
                logic_result = await self._apply_logic_reasoning(content, context)
                reasoning_results.append(logic_result)
            
            # Memory processing
            if 'memory' in self.reasoning_agents:
                memory_result = await self._apply_memory_processing(content, context)
                reasoning_results.append(memory_result)
            
            return {
                'plugin': self.plugin_name,
                'message_atom_id': message_atom,
                'reasoning_results': reasoning_results,
                'atomspace_stats': {
                    'atom_count': self.atomspace_core.get_atom_count(),
                    'link_count': self.atomspace_core.get_link_count()
                },
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message in OpenCog plugin: {e}")
            return {'error': str(e)}
    
    async def _apply_pattern_recognition(self, content: str, context: Dict) -> Dict:
        """Apply pattern recognition to content"""
        # Simple pattern recognition implementation
        patterns = []
        
        # Financial patterns
        if any(word in content.lower() for word in ['money', 'cost', 'price', 'budget', 'expense']):
            patterns.append({
                'type': 'financial',
                'confidence': 0.8,
                'keywords': ['money', 'cost', 'price', 'budget', 'expense']
            })
        
        # Question patterns
        if any(word in content.lower() for word in ['what', 'how', 'when', 'where', 'why']):
            patterns.append({
                'type': 'question',
                'confidence': 0.9,
                'keywords': ['what', 'how', 'when', 'where', 'why']
            })
        
        return {
            'agent': 'pattern_recognition',
            'patterns_found': patterns,
            'pattern_count': len(patterns)
        }
    
    async def _apply_logic_reasoning(self, content: str, context: Dict) -> Dict:
        """Apply logical reasoning to content"""
        # Mock PLN reasoning implementation
        premises = []
        conclusions = []
        
        # Create premises from content
        if 'financial' in str(context).lower():
            premises.append("User is discussing financial topics")
            conclusions.append("Provide financial reasoning and advice")
        
        if any(word in content.lower() for word in ['help', 'advice', 'suggest']):
            premises.append("User is requesting assistance")
            conclusions.append("Provide helpful recommendations")
        
        return {
            'agent': 'logic_reasoning',
            'premises': premises,
            'conclusions': conclusions,
            'confidence': 0.75
        }
    
    async def _apply_memory_processing(self, content: str, context: Dict) -> Dict:
        """Process and store in memory"""
        # Store in AtomSpace memory
        memory_concepts = []
        
        # Extract key concepts from content
        words = content.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                concept_atom = self.atomspace_core.create_atom(
                    'ConceptNode', f"Concept-{word}"
                )
                memory_concepts.append({
                    'concept': word,
                    'atom_id': concept_atom
                })
        
        return {
            'agent': 'memory',
            'stored_concepts': len(memory_concepts),
            'concepts': memory_concepts[:5]  # Return first 5 for brevity
        }
    
    async def cleanup(self) -> bool:
        """Cleanup OpenCog agent plugin"""
        try:
            logger.info("Cleaning up OpenCog Agent Plugin...")
            self.enabled = False
            self.reasoning_agents.clear()
            return True
        except Exception as e:
            logger.error(f"Error cleaning up OpenCog plugin: {e}")
            return False


class FinancialCognitivePlugin(ElizaOSPlugin):
    """Plugin for financial cognitive processing with OpenCog and GnuCash"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("financial_cognitive", config)
        self.financial_atomspace = None
        self.gnucash_config = config.get('gnucash', {})
        
    async def initialize(self) -> bool:
        """Initialize financial cognitive plugin"""
        try:
            logger.info("Initializing Financial Cognitive Plugin...")
            
            # Initialize financial AtomSpace
            self.financial_atomspace = FinancialAtomSpace(self.config)
            if not await self.financial_atomspace.initialize():
                raise RuntimeError("Failed to initialize Financial AtomSpace")
            
            # Load sample financial data
            await self._load_sample_financial_data()
            
            self.enabled = True
            logger.info("✅ Financial Cognitive Plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Financial Cognitive Plugin: {e}")
            return False
    
    async def _load_sample_financial_data(self):
        """Load sample financial data for demonstration"""
        # Create sample accounts
        checking_account = self.financial_atomspace.create_account_atom(
            "Checking", "Asset", 2500.00
        )
        savings_account = self.financial_atomspace.create_account_atom(
            "Savings", "Asset", 10000.00
        )
        expense_account = self.financial_atomspace.create_account_atom(
            "Groceries", "Expense", 0.00
        )
        
        # Create sample transactions
        self.financial_atomspace.create_transaction_link(
            "Checking", "Groceries", 85.50, "Weekly grocery shopping"
        )
        self.financial_atomspace.create_transaction_link(
            "Checking", "Groceries", 92.30, "Organic food market"
        )
        
        logger.info("Loaded sample financial data into AtomSpace")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process financial queries and provide cognitive analysis"""
        if not self.enabled:
            return {'error': 'Plugin not enabled'}
        
        try:
            content = message.get('content', '').lower()
            
            # Detect financial query types
            if any(word in content for word in ['balance', 'account', 'money']):
                return await self._handle_balance_query(message)
            elif any(word in content for word in ['spend', 'spent', 'expense']):
                return await self._handle_spending_query(message)
            elif any(word in content for word in ['transaction', 'payment']):
                return await self._handle_transaction_query(message)
            else:
                return await self._handle_general_financial_query(message)
                
        except Exception as e:
            logger.error(f"Error processing financial message: {e}")
            return {'error': str(e)}
    
    async def _handle_balance_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle account balance queries"""
        checking_balance = self.financial_atomspace.get_account_balance("Checking")
        savings_balance = self.financial_atomspace.get_account_balance("Savings")
        
        return {
            'plugin': self.plugin_name,
            'query_type': 'balance',
            'response': {
                'checking_balance': checking_balance,
                'savings_balance': savings_balance,
                'total_assets': checking_balance + savings_balance
            },
            'cognitive_analysis': {
                'financial_health': 'Good' if (checking_balance + savings_balance) > 10000 else 'Moderate',
                'liquidity_ratio': checking_balance / (checking_balance + savings_balance) if (checking_balance + savings_balance) > 0 else 0
            }
        }
    
    async def _handle_spending_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle spending pattern queries"""
        grocery_transactions = self.financial_atomspace.query_transactions_by_account("Groceries")
        
        return {
            'plugin': self.plugin_name,
            'query_type': 'spending',
            'response': {
                'grocery_transactions': len(grocery_transactions),
                'recent_spending_pattern': 'Regular weekly grocery shopping detected'
            },
            'cognitive_analysis': {
                'spending_pattern': 'Consistent grocery spending',
                'recommendation': 'Consider meal planning to optimize grocery expenses'
            }
        }
    
    async def _handle_transaction_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transaction history queries"""
        all_transactions = []
        for account_name in self.financial_atomspace.account_atoms:
            transactions = self.financial_atomspace.query_transactions_by_account(account_name)
            all_transactions.extend(transactions)
        
        return {
            'plugin': self.plugin_name,
            'query_type': 'transactions',
            'response': {
                'total_transactions': len(all_transactions),
                'transaction_summary': 'Recent financial activity detected'
            },
            'cognitive_analysis': {
                'activity_level': 'Moderate',
                'pattern_analysis': 'Regular spending patterns observed'
            }
        }
    
    async def _handle_general_financial_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general financial queries"""
        atomspace_stats = {
            'atoms': self.financial_atomspace.get_atom_count(),
            'links': self.financial_atomspace.get_link_count(),
            'accounts': len(self.financial_atomspace.account_atoms)
        }
        
        return {
            'plugin': self.plugin_name,
            'query_type': 'general',
            'response': {
                'message': 'Financial cognitive system is active and processing your request',
                'available_features': ['balance_queries', 'spending_analysis', 'transaction_history']
            },
            'atomspace_stats': atomspace_stats,
            'cognitive_analysis': {
                'system_status': 'Active',
                'reasoning_capability': 'Available'
            }
        }
    
    async def cleanup(self) -> bool:
        """Cleanup financial cognitive plugin"""
        try:
            logger.info("Cleaning up Financial Cognitive Plugin...")
            self.enabled = False
            return True
        except Exception as e:
            logger.error(f"Error cleaning up financial plugin: {e}")
            return False


class ElizaOSPluginManager:
    """Manager for ElizaOS plugins with OpenCog integration"""
    
    def __init__(self):
        self.plugins = {}
        self.enabled_plugins = []
        
    async def register_plugin(self, plugin: ElizaOSPlugin) -> bool:
        """Register a plugin with the manager"""
        try:
            self.plugins[plugin.plugin_name] = plugin
            logger.info(f"Registered plugin: {plugin.plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin.plugin_name}: {e}")
            return False
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a specific plugin"""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin {plugin_name} not found")
            return False
        
        plugin = self.plugins[plugin_name]
        if await plugin.initialize():
            if plugin_name not in self.enabled_plugins:
                self.enabled_plugins.append(plugin_name)
            logger.info(f"Enabled plugin: {plugin_name}")
            return True
        else:
            logger.error(f"Failed to enable plugin: {plugin_name}")
            return False
    
    async def process_message_through_plugins(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a message through all enabled plugins"""
        results = []
        
        for plugin_name in self.enabled_plugins:
            plugin = self.plugins[plugin_name]
            try:
                result = await plugin.process_message(message)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing message in plugin {plugin_name}: {e}")
                results.append({'plugin': plugin_name, 'error': str(e)})
        
        return results
    
    async def cleanup_all_plugins(self) -> bool:
        """Cleanup all plugins"""
        success = True
        for plugin in self.plugins.values():
            if not await plugin.cleanup():
                success = False
        
        self.enabled_plugins.clear()
        return success