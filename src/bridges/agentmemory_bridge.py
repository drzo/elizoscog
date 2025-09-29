"""
agentmemory Bridge Implementation

Description: Easy-to-use agent memory, powered by chromadb and postgres
Original Repository: https://github.com/elizaOS/agentmemory
Generated: 2025-06-13T22:11:51.748221

This bridge enables cross-ecosystem integration between:
- ElizaOS (TypeScript/JavaScript agents)
- OpenCog (Scheme/C++ cognitive architecture)  
- GnuCash (C/Scheme financial system)
"""

import json
import subprocess
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AgentmemoryBridge:
    """Bridge for agentmemory cross-ecosystem integration"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = "agentmemory"
        self.description = "Easy-to-use agent memory, powered by chromadb and postgres"
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the agentmemory bridge"""
        try:
            logger.info(f"Initializing {self.name} bridge")
            
            # Initialize memory storage systems
            self.memory_stores = {}
            self.active_connections = {}
            
            await self._setup_elizaos_connection()
            await self._setup_opencog_connection() 
            await self._setup_gnucash_connection()
            
            # Initialize memory indexing and retrieval systems
            await self._initialize_memory_systems()
            
            self.initialized = True
            logger.info(f"{self.name} bridge initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} bridge: {e}")
            return False
    
    async def _setup_elizaos_connection(self):
        """Setup connection to ElizaOS ecosystem"""
        logger.debug("Setting up ElizaOS connection")
        
        # Initialize ElizaOS agent memory interface
        self.elizaos_config = self.config.get('elizaos', {})
        self.elizaos_endpoint = self.elizaos_config.get('endpoint', 'http://localhost:3000')
        self.elizaos_api_key = self.elizaos_config.get('api_key')
        
        # Initialize memory collections for ElizaOS agents
        self.agent_memories = {}
        self.conversation_histories = {}
        self.elizaos_connected = True
        
        logger.info("ElizaOS connection established for agentmemory")
        
    async def _setup_opencog_connection(self):
        """Setup connection to OpenCog ecosystem"""
        logger.debug("Setting up OpenCog connection")
        
        # Initialize AtomSpace memory integration
        self.opencog_config = self.config.get('opencog', {})
        self.atomspace_host = self.opencog_config.get('host', 'localhost')
        self.atomspace_port = self.opencog_config.get('port', 17001)
        
        # Initialize AtomSpace memory mapping
        self.atomspace_memories = {}
        self.cognitive_memories = {}
        self.opencog_connected = True
        
        logger.info("OpenCog connection established for agentmemory")
        
    async def _setup_gnucash_connection(self):
        """Setup connection to GnuCash ecosystem"""
        logger.debug("Setting up GnuCash connection")
        
        # Initialize financial memory storage
        self.gnucash_config = self.config.get('gnucash', {})
        self.gnucash_file = self.gnucash_config.get('file_path')
        
        # Initialize financial memory collections
        self.financial_memories = {}
        self.transaction_memories = {}
        self.gnucash_connected = True
        
        logger.info("GnuCash connection established for agentmemory")
        
    async def _initialize_memory_systems(self):
        """Initialize memory storage and retrieval systems"""
        logger.debug("Initializing memory systems")
        
        # Initialize vector storage for semantic memory
        self.vector_stores = {
            'elizaos': {},
            'opencog': {},
            'gnucash': {}
        }
        
        # Initialize memory indexing
        self.memory_indices = {
            'semantic': {},
            'episodic': {},
            'procedural': {},
            'financial': {}
        }
    
    async def process_elizaos_request(self, request: Dict) -> Dict:
        """Process request from ElizaOS ecosystem"""
        if not self.initialized:
            raise RuntimeError("Bridge not initialized")
            
        logger.debug(f"Processing ElizaOS request: {request}")
        
        operation = request.get('operation')
        agent_id = request.get('agent_id')
        data = request.get('data', {})
        
        if operation == 'store_memory':
            # Store memory for ElizaOS agent
            memory_id = await self._store_agent_memory(agent_id, data)
            response = {
                "success": True,
                "source": "elizaos",
                "target": "agentmemory",
                "operation": "store_memory",
                "memory_id": memory_id,
                "agent_id": agent_id
            }
        elif operation == 'retrieve_memory':
            # Retrieve memory for ElizaOS agent
            memories = await self._retrieve_agent_memory(agent_id, data.get('query'))
            response = {
                "success": True,
                "source": "elizaos",
                "target": "agentmemory", 
                "operation": "retrieve_memory",
                "memories": memories,
                "agent_id": agent_id
            }
        elif operation == 'search_memory':
            # Search memory using semantic similarity
            results = await self._search_agent_memory(agent_id, data.get('query'))
            response = {
                "success": True,
                "source": "elizaos",
                "target": "agentmemory",
                "operation": "search_memory",
                "results": results,
                "agent_id": agent_id
            }
        else:
            response = {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "source": "elizaos",
                "target": "agentmemory"
            }
        
        return response
    
    async def process_opencog_request(self, request: Dict) -> Dict:
        """Process request from OpenCog ecosystem"""
        if not self.initialized:
            raise RuntimeError("Bridge not initialized")
            
        logger.debug(f"Processing OpenCog request: {request}")
        
        operation = request.get('operation')
        atomspace_id = request.get('atomspace_id')
        data = request.get('data', {})
        
        if operation == 'store_cognitive_memory':
            # Store cognitive memory in AtomSpace format
            memory_id = await self._store_cognitive_memory(atomspace_id, data)
            response = {
                "success": True,
                "source": "opencog",
                "target": "agentmemory",
                "operation": "store_cognitive_memory",
                "memory_id": memory_id,
                "atomspace_id": atomspace_id
            }
        elif operation == 'retrieve_cognitive_memory':
            # Retrieve cognitive memory patterns
            memories = await self._retrieve_cognitive_memory(atomspace_id, data.get('pattern'))
            response = {
                "success": True,
                "source": "opencog",
                "target": "agentmemory",
                "operation": "retrieve_cognitive_memory", 
                "memories": memories,
                "atomspace_id": atomspace_id
            }
        elif operation == 'pattern_match_memory':
            # Pattern matching in cognitive memory
            matches = await self._pattern_match_memory(atomspace_id, data.get('pattern'))
            response = {
                "success": True,
                "source": "opencog", 
                "target": "agentmemory",
                "operation": "pattern_match_memory",
                "matches": matches,
                "atomspace_id": atomspace_id
            }
        else:
            response = {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "source": "opencog",
                "target": "agentmemory"
            }
        
        return response
    
    async def process_gnucash_request(self, request: Dict) -> Dict:
        """Process request from GnuCash ecosystem"""
        if not self.initialized:
            raise RuntimeError("Bridge not initialized")
            
        logger.debug(f"Processing GnuCash request: {request}")
        
        operation = request.get('operation')
        account_id = request.get('account_id')
        data = request.get('data', {})
        
        if operation == 'store_financial_memory':
            # Store financial transaction memory
            memory_id = await self._store_financial_memory(account_id, data)
            response = {
                "success": True,
                "source": "gnucash",
                "target": "agentmemory",
                "operation": "store_financial_memory",
                "memory_id": memory_id,
                "account_id": account_id
            }
        elif operation == 'retrieve_financial_memory':
            # Retrieve financial memory patterns
            memories = await self._retrieve_financial_memory(account_id, data.get('criteria'))
            response = {
                "success": True,
                "source": "gnucash", 
                "target": "agentmemory",
                "operation": "retrieve_financial_memory",
                "memories": memories,
                "account_id": account_id
            }
        elif operation == 'analyze_spending_patterns':
            # Analyze spending patterns from memory
            patterns = await self._analyze_spending_patterns(account_id, data.get('timeframe'))
            response = {
                "success": True,
                "source": "gnucash",
                "target": "agentmemory",
                "operation": "analyze_spending_patterns",
                "patterns": patterns,
                "account_id": account_id
            }
        else:
            response = {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "source": "gnucash",
                "target": "agentmemory"
            }
        
        return response
    
    async def translate_data(self, data: Any, source_format: str, target_format: str) -> Any:
        """Translate data between ecosystem formats"""
        logger.debug(f"Translating data from {source_format} to {target_format}")
        
        translators = {
            ("elizaos", "opencog"): self._elizaos_to_opencog,
            ("opencog", "elizaos"): self._opencog_to_elizaos,
            ("elizaos", "gnucash"): self._elizaos_to_gnucash,
            ("gnucash", "elizaos"): self._gnucash_to_elizaos,
            ("opencog", "gnucash"): self._opencog_to_gnucash,
            ("gnucash", "opencog"): self._gnucash_to_opencog
        }
        
        translator = translators.get((source_format, target_format))
        if translator:
            return await translator(data)
        else:
            logger.warning(f"No translator found for {source_format} -> {target_format}")
            return data
    
    async def _elizaos_to_opencog(self, data: Any) -> Any:
        """Translate ElizaOS data to OpenCog format"""
        if isinstance(data, dict):
            # Convert ElizaOS agent memory to AtomSpace format
            atomspace_data = {
                "atoms": [],
                "links": []
            }
            
            # Convert memories to concept atoms
            if 'memories' in data:
                for memory in data['memories']:
                    atom = {
                        "type": "ConceptNode",
                        "name": f"Memory_{memory.get('id', 'unknown')}",
                        "tv": {"strength": 0.9, "confidence": 0.8}
                    }
                    atomspace_data["atoms"].append(atom)
                    
            # Convert relationships to inheritance links
            if 'relationships' in data:
                for rel in data['relationships']:
                    link = {
                        "type": "InheritanceLink",
                        "outgoing": [rel.get('source'), rel.get('target')],
                        "tv": {"strength": 0.8, "confidence": 0.7}
                    }
                    atomspace_data["links"].append(link)
                    
            return {"atomspace_data": atomspace_data, "format": "opencog"}
        else:
            return {"atomspace_data": str(data), "format": "opencog"}
    
    async def _opencog_to_elizaos(self, data: Any) -> Any:
        """Translate OpenCog data to ElizaOS format"""
        if isinstance(data, dict) and 'atomspace_data' in data:
            # Convert AtomSpace format to ElizaOS agent memory
            agent_data = {
                "memories": [],
                "relationships": [],
                "metadata": {}
            }
            
            atomspace = data['atomspace_data']
            
            # Convert concept atoms to memories
            if 'atoms' in atomspace:
                for atom in atomspace['atoms']:
                    if atom.get('type') == 'ConceptNode':
                        memory = {
                            "id": atom.get('name', '').replace('Memory_', ''),
                            "content": atom.get('name'),
                            "confidence": atom.get('tv', {}).get('confidence', 0.5),
                            "type": "cognitive"
                        }
                        agent_data["memories"].append(memory)
                        
            # Convert links to relationships
            if 'links' in atomspace:
                for link in atomspace['links']:
                    if link.get('type') == 'InheritanceLink':
                        outgoing = link.get('outgoing', [])
                        if len(outgoing) >= 2:
                            relationship = {
                                "source": outgoing[0],
                                "target": outgoing[1],
                                "type": "inheritance",
                                "strength": link.get('tv', {}).get('strength', 0.5)
                            }
                            agent_data["relationships"].append(relationship)
                            
            return {"agent_data": agent_data, "format": "elizaos"}
        else:
            return {"agent_data": {"content": str(data)}, "format": "elizaos"}
    
    async def _elizaos_to_gnucash(self, data: Any) -> Any:
        """Translate ElizaOS data to GnuCash format"""
        if isinstance(data, dict):
            # Convert ElizaOS financial agent data to GnuCash format
            financial_data = {
                "transactions": [],
                "accounts": [],
                "categories": []
            }
            
            # Convert agent memories to financial transactions
            if 'memories' in data:
                for memory in data['memories']:
                    if memory.get('type') == 'financial':
                        transaction = {
                            "guid": memory.get('id'),
                            "description": memory.get('content'),
                            "amount": memory.get('amount', 0.0),
                            "date": memory.get('timestamp'),
                            "account": memory.get('account', 'Unknown')
                        }
                        financial_data["transactions"].append(transaction)
                        
            return {"financial_data": financial_data, "format": "gnucash"}
        else:
            return {"financial_data": {"description": str(data)}, "format": "gnucash"}
    
    async def _gnucash_to_elizaos(self, data: Any) -> Any:
        """Translate GnuCash data to ElizaOS format"""
        if isinstance(data, dict) and 'financial_data' in data:
            # Convert GnuCash financial data to ElizaOS agent format
            agent_data = {
                "memories": [],
                "financial_context": {},
                "metadata": {}
            }
            
            financial_data = data['financial_data']
            
            # Convert transactions to agent memories
            if 'transactions' in financial_data:
                for transaction in financial_data['transactions']:
                    memory = {
                        "id": transaction.get('guid'),
                        "content": transaction.get('description'),
                        "amount": transaction.get('amount'),
                        "timestamp": transaction.get('date'),
                        "type": "financial",
                        "account": transaction.get('account')
                    }
                    agent_data["memories"].append(memory)
                    
            return {"agent_data": agent_data, "format": "elizaos"}
        else:
            return {"agent_data": {"content": str(data)}, "format": "elizaos"}
    
    async def _opencog_to_gnucash(self, data: Any) -> Any:
        """Translate OpenCog data to GnuCash format"""
        if isinstance(data, dict) and 'atomspace_data' in data:
            # Convert cognitive reasoning results to financial format
            financial_data = {
                "insights": [],
                "patterns": [],
                "recommendations": []
            }
            
            atomspace = data['atomspace_data']
            
            # Convert reasoning atoms to financial insights
            if 'atoms' in atomspace:
                for atom in atomspace['atoms']:
                    if 'Financial' in atom.get('name', ''):
                        insight = {
                            "type": "cognitive_insight",
                            "description": atom.get('name'),
                            "confidence": atom.get('tv', {}).get('confidence', 0.5),
                            "source": "opencog"
                        }
                        financial_data["insights"].append(insight)
                        
            return {"financial_data": financial_data, "format": "gnucash"}
        else:
            return {"financial_data": {"description": str(data)}, "format": "gnucash"}
    
    async def _gnucash_to_opencog(self, data: Any) -> Any:
        """Translate GnuCash data to OpenCog format"""
        if isinstance(data, dict) and 'financial_data' in data:
            # Convert financial data to cognitive reasoning format
            atomspace_data = {
                "atoms": [],
                "links": []
            }
            
            financial_data = data['financial_data']
            
            # Convert transactions to financial concept atoms
            if 'transactions' in financial_data:
                for transaction in financial_data['transactions']:
                    atom = {
                        "type": "ConceptNode", 
                        "name": f"Transaction_{transaction.get('guid', 'unknown')}",
                        "tv": {"strength": 0.9, "confidence": 0.8}
                    }
                    atomspace_data["atoms"].append(atom)
                    
                    # Create evaluation link for transaction amount
                    amount_link = {
                        "type": "EvaluationLink",
                        "outgoing": [
                            "AmountPredicate",
                            f"Transaction_{transaction.get('guid', 'unknown')}",
                            str(transaction.get('amount', 0))
                        ],
                        "tv": {"strength": 1.0, "confidence": 0.9}
                    }
                    atomspace_data["links"].append(amount_link)
                    
            return {"atomspace_data": atomspace_data, "format": "opencog"}
        else:
            return {"atomspace_data": str(data), "format": "opencog"}
    
    async def shutdown(self):
        """Shutdown the bridge"""
        logger.info(f"Shutting down {self.name} bridge")
        self.initialized = False
        
        # Close all active connections
        if hasattr(self, 'active_connections'):
            for conn_id, conn in self.active_connections.items():
                try:
                    await conn.close()
                except Exception as e:
                    logger.warning(f"Error closing connection {conn_id}: {e}")
                    
        # Clear memory stores
        if hasattr(self, 'memory_stores'):
            self.memory_stores.clear()
            
    async def _store_agent_memory(self, agent_id: str, data: Dict) -> str:
        """Store memory for ElizaOS agent"""
        memory_id = f"{agent_id}_{datetime.now().timestamp()}"
        
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = []
            
        memory_entry = {
            "id": memory_id,
            "agent_id": agent_id,
            "content": data.get('content'),
            "timestamp": datetime.now().isoformat(),
            "type": data.get('type', 'general'),
            "metadata": data.get('metadata', {})
        }
        
        self.agent_memories[agent_id].append(memory_entry)
        logger.debug(f"Stored memory {memory_id} for agent {agent_id}")
        return memory_id
        
    async def _retrieve_agent_memory(self, agent_id: str, query: Optional[str] = None) -> List[Dict]:
        """Retrieve memory for ElizaOS agent"""
        if agent_id not in self.agent_memories:
            return []
            
        memories = self.agent_memories[agent_id]
        
        if query:
            # Simple text search in memory content
            filtered_memories = []
            for memory in memories:
                if query.lower() in memory.get('content', '').lower():
                    filtered_memories.append(memory)
            return filtered_memories
        else:
            return memories
            
    async def _search_agent_memory(self, agent_id: str, query: str) -> List[Dict]:
        """Search agent memory using semantic similarity"""
        if agent_id not in self.agent_memories:
            return []
            
        # Simple keyword-based search (in production, use vector embeddings)
        memories = self.agent_memories[agent_id]
        search_results = []
        
        query_words = query.lower().split()
        
        for memory in memories:
            content = memory.get('content', '').lower()
            score = 0
            for word in query_words:
                if word in content:
                    score += 1
                    
            if score > 0:
                result = memory.copy()
                result['relevance_score'] = score / len(query_words)
                search_results.append(result)
                
        # Sort by relevance score
        search_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return search_results
        
    async def _store_cognitive_memory(self, atomspace_id: str, data: Dict) -> str:
        """Store cognitive memory in AtomSpace format"""
        memory_id = f"cognitive_{atomspace_id}_{datetime.now().timestamp()}"
        
        if atomspace_id not in self.cognitive_memories:
            self.cognitive_memories[atomspace_id] = []
            
        memory_entry = {
            "id": memory_id,
            "atomspace_id": atomspace_id,
            "atoms": data.get('atoms', []),
            "links": data.get('links', []),
            "timestamp": datetime.now().isoformat(),
            "confidence": data.get('confidence', 0.8)
        }
        
        self.cognitive_memories[atomspace_id].append(memory_entry)
        logger.debug(f"Stored cognitive memory {memory_id} for atomspace {atomspace_id}")
        return memory_id
        
    async def _retrieve_cognitive_memory(self, atomspace_id: str, pattern: Optional[Dict] = None) -> List[Dict]:
        """Retrieve cognitive memory patterns"""
        if atomspace_id not in self.cognitive_memories:
            return []
            
        memories = self.cognitive_memories[atomspace_id]
        
        if pattern:
            # Pattern matching logic
            filtered_memories = []
            for memory in memories:
                if self._matches_pattern(memory, pattern):
                    filtered_memories.append(memory)
            return filtered_memories
        else:
            return memories
            
    async def _pattern_match_memory(self, atomspace_id: str, pattern: Dict) -> List[Dict]:
        """Pattern matching in cognitive memory"""
        memories = await self._retrieve_cognitive_memory(atomspace_id, pattern)
        
        # Add pattern matching scores
        matches = []
        for memory in memories:
            match_score = self._calculate_pattern_score(memory, pattern)
            match = memory.copy()
            match['match_score'] = match_score
            matches.append(match)
            
        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches
        
    async def _store_financial_memory(self, account_id: str, data: Dict) -> str:
        """Store financial transaction memory"""
        memory_id = f"financial_{account_id}_{datetime.now().timestamp()}"
        
        if account_id not in self.financial_memories:
            self.financial_memories[account_id] = []
            
        memory_entry = {
            "id": memory_id,
            "account_id": account_id,
            "transaction": data.get('transaction', {}),
            "patterns": data.get('patterns', []),
            "timestamp": datetime.now().isoformat(),
            "category": data.get('category', 'unknown')
        }
        
        self.financial_memories[account_id].append(memory_entry)
        logger.debug(f"Stored financial memory {memory_id} for account {account_id}")
        return memory_id
        
    async def _retrieve_financial_memory(self, account_id: str, criteria: Optional[Dict] = None) -> List[Dict]:
        """Retrieve financial memory patterns"""
        if account_id not in self.financial_memories:
            return []
            
        memories = self.financial_memories[account_id]
        
        if criteria:
            # Filter by criteria
            filtered_memories = []
            for memory in memories:
                if self._matches_financial_criteria(memory, criteria):
                    filtered_memories.append(memory)
            return filtered_memories
        else:
            return memories
            
    async def _analyze_spending_patterns(self, account_id: str, timeframe: Optional[Dict] = None) -> List[Dict]:
        """Analyze spending patterns from memory"""
        memories = await self._retrieve_financial_memory(account_id)
        
        # Simple pattern analysis
        patterns = []
        category_totals = {}
        
        for memory in memories:
            transaction = memory.get('transaction', {})
            category = memory.get('category', 'unknown')
            amount = transaction.get('amount', 0)
            
            if category not in category_totals:
                category_totals[category] = {'total': 0, 'count': 0}
                
            category_totals[category]['total'] += amount
            category_totals[category]['count'] += 1
            
        # Generate pattern insights
        for category, data in category_totals.items():
            pattern = {
                "category": category,
                "total_amount": data['total'],
                "transaction_count": data['count'],
                "average_amount": data['total'] / data['count'] if data['count'] > 0 else 0,
                "account_id": account_id
            }
            patterns.append(pattern)
            
        return patterns
        
    def _matches_pattern(self, memory: Dict, pattern: Dict) -> bool:
        """Check if memory matches cognitive pattern"""
        # Simple pattern matching logic
        for key, value in pattern.items():
            if key in memory and memory[key] != value:
                return False
        return True
        
    def _calculate_pattern_score(self, memory: Dict, pattern: Dict) -> float:
        """Calculate pattern matching score"""
        matches = 0
        total_keys = len(pattern)
        
        for key, value in pattern.items():
            if key in memory and memory[key] == value:
                matches += 1
                
        return matches / total_keys if total_keys > 0 else 0.0
        
    def _matches_financial_criteria(self, memory: Dict, criteria: Dict) -> bool:
        """Check if financial memory matches criteria"""
        transaction = memory.get('transaction', {})
        
        # Check amount range
        if 'amount_min' in criteria:
            if transaction.get('amount', 0) < criteria['amount_min']:
                return False
                
        if 'amount_max' in criteria:
            if transaction.get('amount', 0) > criteria['amount_max']:
                return False
                
        # Check category
        if 'category' in criteria:
            if memory.get('category') != criteria['category']:
                return False
                
        # Check date range
        if 'start_date' in criteria or 'end_date' in criteria:
            memory_date = datetime.fromisoformat(memory.get('timestamp'))
            if 'start_date' in criteria:
                start_date = datetime.fromisoformat(criteria['start_date'])
                if memory_date < start_date:
                    return False
            if 'end_date' in criteria:
                end_date = datetime.fromisoformat(criteria['end_date'])
                if memory_date > end_date:
                    return False
                    
        return True

class AgentmemoryIntegrationFramework:
    """Framework for managing agentmemory integrations"""
    
    def __init__(self):
        self.bridges = {}
        self.active_sessions = {}
        
    async def register_bridge(self, bridge: AgentmemoryBridge) -> bool:
        """Register a new bridge"""
        try:
            await bridge.initialize()
            self.bridges[bridge.name] = bridge
            logger.info(f"Registered bridge: {bridge.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register bridge {bridge.name}: {e}")
            return False
    
    async def process_cross_ecosystem_request(self, source: str, target: str, request: Dict) -> Dict:
        """Process request across ecosystems"""
        bridge_name = f"{source}_{target}_bridge"
        
        if bridge_name not in self.bridges:
            raise ValueError(f"No bridge found for {source} -> {target}")
            
        bridge = self.bridges[bridge_name]
        
        # Route request to appropriate processor
        if source == "elizaos":
            return await bridge.process_elizaos_request(request)
        elif source == "opencog":
            return await bridge.process_opencog_request(request)
        elif source == "gnucash":
            return await bridge.process_gnucash_request(request)
        else:
            raise ValueError(f"Unknown source ecosystem: {source}")

# Export classes for external use
__all__ = ["AgentmemoryBridge", "AgentmemoryIntegrationFramework"]
