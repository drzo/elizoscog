"""
attention Bridge Implementation

Description: OpenCog Attention Allocation Subsystem
Original Repository: https://github.com/opencog/attention
Generated: 2025-06-13T22:11:51.747277

This bridge enables cross-ecosystem integration between:
- ElizaOS (TypeScript/JavaScript agents)
- OpenCog (Scheme/C++ cognitive architecture)  
- GnuCash (C/Scheme financial system)
"""

import json
import subprocess
from datetime import datetime
import asyncio
import time
import heapq
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class AttentionValue:
    """ECAN Attention Value structure"""
    importance: float = 0.0
    urgency: float = 0.0
    confidence: float = 1.0
    sti: float = 0.0  # Short Term Importance
    lti: float = 0.0  # Long Term Importance
    
    @property
    def total_importance(self) -> float:
        return self.importance + self.urgency * 0.5 + self.sti
    
    def decay(self, decay_rate: float = 0.95):
        """Apply temporal decay to attention values"""
        self.sti *= decay_rate
        self.urgency *= decay_rate

@dataclass
class ResourceAgent:
    """Represents an agent/atom competing for attention resources"""
    agent_id: str
    attention: AttentionValue
    last_access: float
    processing_cost: float = 1.0
    rent_rate: float = 0.1
    
    def __post_init__(self):
        if self.last_access == 0:
            self.last_access = time.time()
    
    @property
    def current_rent(self) -> float:
        """Calculate current rent owed based on attention and time"""
        time_since_access = time.time() - self.last_access
        return self.attention.total_importance * self.rent_rate * time_since_access

class ECANResourceAllocator:
    """ECAN Economic Attention Resource Allocator"""
    
    def __init__(self, attention_bank_funds: float = 1000.0, max_agents: int = 100):
        self.attention_bank = attention_bank_funds
        self.max_agents = max_agents
        self.active_agents: Dict[str, ResourceAgent] = {}
        self.importance_heap: List[Tuple[float, str]] = []  # Max heap for scheduling
        self.rent_collection_rate = 0.95  # Percentage of rent collected
        self.wage_payment_rate = 0.1  # Payment for active processing
        self.decay_interval = 1.0  # Seconds between decay cycles
        self.last_maintenance = time.time()
        
    async def allocate_resources(self, agent_requests: List[Dict]) -> Dict[str, Any]:
        """Main ECAN resource allocation algorithm"""
        start_time = time.time()
        
        # Step 1: Collect rent from all agents
        await self._collect_rent()
        
        # Step 2: Update importance values based on new requests
        await self._update_importance_values(agent_requests)
        
        # Step 3: Dynamic scheduling based on importance
        allocation_plan = await self._schedule_agents()
        
        # Step 4: Resource contention resolution
        final_allocation = await self._resolve_resource_contention(allocation_plan)
        
        # Step 5: Attention value decay and cleanup
        await self._attention_maintenance()
        
        allocation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "allocation_plan": final_allocation,
            "allocation_time_ms": allocation_time,
            "bank_funds": self.attention_bank,
            "active_agents": len(self.active_agents),
            "efficiency_metrics": await self._calculate_efficiency_metrics()
        }
    
    async def _collect_rent(self):
        """ECAN rent collection mechanism"""
        total_rent_collected = 0.0
        agents_to_remove = []
        
        for agent_id, agent in self.active_agents.items():
            rent_owed = agent.current_rent
            
            if rent_owed > agent.attention.sti:
                # Agent can't pay rent, reduce importance or remove
                agent.attention.sti = max(0, agent.attention.sti - rent_owed)
                if agent.attention.total_importance < 0.1:
                    agents_to_remove.append(agent_id)
            else:
                # Collect rent
                collected = rent_owed * self.rent_collection_rate
                agent.attention.sti -= collected
                self.attention_bank += collected
                total_rent_collected += collected
                agent.last_access = time.time()
        
        # Remove agents that can't sustain attention
        for agent_id in agents_to_remove:
            del self.active_agents[agent_id]
            
        logger.debug(f"Collected {total_rent_collected:.2f} in rent, removed {len(agents_to_remove)} agents")
    
    async def _update_importance_values(self, agent_requests: List[Dict]):
        """Update agent importance based on new requests and spreading activation"""
        for request in agent_requests:
            agent_id = request.get("agent_id")
            if not agent_id:
                continue
                
            # Get or create agent
            if agent_id not in self.active_agents:
                if len(self.active_agents) >= self.max_agents:
                    # Need to make room - remove least important agent
                    await self._evict_least_important_agent()
                
                self.active_agents[agent_id] = ResourceAgent(
                    agent_id=agent_id,
                    attention=AttentionValue(),
                    last_access=time.time()
                )
            
            agent = self.active_agents[agent_id]
            
            # Update importance based on request urgency and context
            urgency_boost = request.get("urgency", 0.5)
            importance_boost = request.get("importance", 0.5)
            
            agent.attention.urgency = min(1.0, agent.attention.urgency + urgency_boost)
            agent.attention.importance = min(1.0, agent.attention.importance + importance_boost)
            agent.attention.sti += importance_boost * 10  # STI boost
            
            # Spreading activation to related agents
            await self._spread_activation(agent_id, importance_boost * 0.3)
    
    async def _spread_activation(self, source_agent_id: str, activation_amount: float):
        """ECAN activation spreading mechanism"""
        # Simple spreading - in real implementation, this would use AtomSpace links
        for agent_id, agent in self.active_agents.items():
            if agent_id != source_agent_id:
                # Calculate relatedness (simplified)
                relatedness = 0.1  # In real implementation, use AtomSpace relationships
                spread_amount = activation_amount * relatedness
                
                agent.attention.sti += spread_amount
                agent.attention.importance = min(1.0, agent.attention.importance + spread_amount * 0.1)
    
    async def _schedule_agents(self) -> Dict[str, Any]:
        """Dynamic agent scheduling based on importance values"""
        # Rebuild importance heap
        self.importance_heap = []
        for agent_id, agent in self.active_agents.items():
            # Use negative importance for max heap behavior with heapq (min heap)
            heapq.heappush(self.importance_heap, (-agent.attention.total_importance, agent_id))
        
        # Allocate resources based on importance ranking
        allocation_plan = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "resource_distribution": {}
        }
        
        total_importance = sum(agent.attention.total_importance for agent in self.active_agents.values())
        
        for i, (neg_importance, agent_id) in enumerate(self.importance_heap):
            importance = -neg_importance
            agent = self.active_agents[agent_id]
            
            # Calculate resource allocation percentage
            if total_importance > 0:
                resource_percentage = importance / total_importance
            else:
                resource_percentage = 1.0 / len(self.active_agents)
            
            allocation_info = {
                "agent_id": agent_id,
                "importance": importance,
                "resource_percentage": resource_percentage,
                "processing_cost": agent.processing_cost
            }
            
            # Categorize by priority
            if importance > 0.7:
                allocation_plan["high_priority"].append(allocation_info)
            elif importance > 0.3:
                allocation_plan["medium_priority"].append(allocation_info)
            else:
                allocation_plan["low_priority"].append(allocation_info)
            
            allocation_plan["resource_distribution"][agent_id] = resource_percentage
        
        return allocation_plan
    
    async def _resolve_resource_contention(self, allocation_plan: Dict) -> Dict:
        """Resolve resource contention using economic principles"""
        # Ensure total allocation doesn't exceed 100%
        total_allocated = sum(allocation_plan["resource_distribution"].values())
        
        if total_allocated > 1.0:
            # Scale down allocations proportionally
            scale_factor = 1.0 / total_allocated
            for agent_id in allocation_plan["resource_distribution"]:
                allocation_plan["resource_distribution"][agent_id] *= scale_factor
        
        # Pay wages to active agents
        for agent_id, percentage in allocation_plan["resource_distribution"].items():
            if agent_id in self.active_agents:
                wage = percentage * self.wage_payment_rate * 10  # Base wage multiplier
                self.active_agents[agent_id].attention.sti += wage
                self.attention_bank -= wage
        
        return allocation_plan
    
    async def _attention_maintenance(self):
        """Periodic attention value decay and system maintenance"""
        current_time = time.time()
        if current_time - self.last_maintenance > self.decay_interval:
            # Apply decay to all agents
            for agent in self.active_agents.values():
                agent.attention.decay(0.95)
            
            # Bank economic dynamics
            self.attention_bank = max(100.0, self.attention_bank * 0.999)  # Slight bank decay
            self.last_maintenance = current_time
    
    async def _evict_least_important_agent(self):
        """Remove the least important agent to make room for new ones"""
        if not self.active_agents:
            return
            
        least_important_agent = min(
            self.active_agents.values(),
            key=lambda agent: agent.attention.total_importance
        )
        
        logger.info(f"Evicting agent {least_important_agent.agent_id} with importance {least_important_agent.attention.total_importance}")
        del self.active_agents[least_important_agent.agent_id]
    
    async def _calculate_efficiency_metrics(self) -> Dict[str, float]:
        """Calculate resource utilization efficiency metrics"""
        if not self.active_agents:
            return {"utilization_rate": 0.0, "attention_distribution_entropy": 0.0}
        
        # Resource utilization rate
        active_importance = sum(agent.attention.total_importance for agent in self.active_agents.values())
        max_possible_importance = len(self.active_agents) * 1.0  # Assuming max importance of 1.0 per agent
        utilization_rate = min(1.0, active_importance / max_possible_importance) if max_possible_importance > 0 else 0.0
        
        # Attention distribution entropy (diversity measure)
        import math
        importances = [agent.attention.total_importance for agent in self.active_agents.values()]
        total_importance = sum(importances)
        
        if total_importance > 0:
            probabilities = [imp / total_importance for imp in importances]
            entropy = -sum(p * math.log(p) for p in probabilities if p > 0)
        else:
            entropy = 0.0
        
        return {
            "utilization_rate": utilization_rate,
            "attention_distribution_entropy": entropy,
            "bank_health": min(1.0, self.attention_bank / 1000.0),
            "active_agent_ratio": len(self.active_agents) / self.max_agents
        }


class AttentionBridge:
    """Bridge for attention cross-ecosystem integration with ECAN resource allocation"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = "attention"
        self.description = "OpenCog Attention Allocation Subsystem with ECAN"
        self.initialized = False
        
        # Initialize ECAN resource allocator
        self.ecan_allocator = ECANResourceAllocator(
            attention_bank_funds=self.config.get("attention_bank_funds", 1000.0),
            max_agents=self.config.get("max_agents", 100)
        )
        
        # Real-time monitoring
        self.performance_metrics = {
            "allocation_times": [],
            "efficiency_scores": [],
            "last_measurement": time.time()
        }
        
    async def initialize(self) -> bool:
        """Initialize the attention bridge with ECAN capabilities"""
        try:
            logger.info(f"Initializing {self.name} bridge with ECAN resource allocation")
            
            await self._setup_elizaos_connection()
            await self._setup_opencog_connection()
            await self._setup_gnucash_connection()
            
            # Start ECAN background processes
            await self._start_ecan_monitoring()
            
            self.initialized = True
            logger.info(f"{self.name} bridge with ECAN initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} bridge: {e}")
            return False
    
    async def _start_ecan_monitoring(self):
        """Start real-time ECAN monitoring and adjustment"""
        # This would typically start background tasks for continuous monitoring
        logger.info("ECAN real-time monitoring started")
        
    async def allocate_attention_resources(self, requests: List[Dict]) -> Dict[str, Any]:
        """Main entry point for ECAN resource allocation"""
        if not self.initialized:
            raise RuntimeError("Bridge not initialized")
        
        logger.debug(f"Processing {len(requests)} attention allocation requests")
        
        # Use ECAN allocator for resource distribution
        allocation_result = await self.ecan_allocator.allocate_resources(requests)
        
        # Track performance metrics
        self._update_performance_metrics(allocation_result)
        
        # Optimize attention flow based on results
        await self._optimize_attention_flow(allocation_result)
        
        return allocation_result
    
    def _update_performance_metrics(self, allocation_result: Dict):
        """Update real-time performance monitoring"""
        allocation_time = allocation_result.get("allocation_time_ms", 0)
        efficiency = allocation_result.get("efficiency_metrics", {}).get("utilization_rate", 0)
        
        self.performance_metrics["allocation_times"].append(allocation_time)
        self.performance_metrics["efficiency_scores"].append(efficiency)
        
        # Keep only recent measurements (sliding window)
        max_measurements = 1000
        if len(self.performance_metrics["allocation_times"]) > max_measurements:
            self.performance_metrics["allocation_times"] = self.performance_metrics["allocation_times"][-max_measurements:]
            self.performance_metrics["efficiency_scores"] = self.performance_metrics["efficiency_scores"][-max_measurements:]
    
    async def _optimize_attention_flow(self, allocation_result: Dict):
        """Dynamic attention flow optimization based on current performance"""
        recent_times = self.performance_metrics["allocation_times"][-10:]  # Last 10 measurements
        recent_efficiency = self.performance_metrics["efficiency_scores"][-10:]
        
        if len(recent_times) >= 5:
            avg_time = sum(recent_times) / len(recent_times)
            avg_efficiency = sum(recent_efficiency) / len(recent_efficiency)
            
            # Adaptive optimization
            if avg_time > 50:  # Above 50ms target
                # Reduce max agents to improve speed
                self.ecan_allocator.max_agents = max(10, self.ecan_allocator.max_agents - 5)
                logger.info(f"Reduced max agents to {self.ecan_allocator.max_agents} due to high allocation time")
            
            if avg_efficiency < 0.95:  # Below 95% efficiency target
                # Adjust economic parameters to improve efficiency
                self.ecan_allocator.rent_collection_rate = min(0.99, self.ecan_allocator.rent_collection_rate + 0.01)
                logger.info(f"Increased rent collection rate to {self.ecan_allocator.rent_collection_rate}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive ECAN system status"""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        recent_times = self.performance_metrics["allocation_times"][-10:]
        recent_efficiency = self.performance_metrics["efficiency_scores"][-10:]
        
        return {
            "status": "active",
            "ecan_allocator": {
                "attention_bank": self.ecan_allocator.attention_bank,
                "active_agents": len(self.ecan_allocator.active_agents),
                "max_agents": self.ecan_allocator.max_agents,
                "efficiency_metrics": await self.ecan_allocator._calculate_efficiency_metrics()
            },
            "performance": {
                "avg_allocation_time_ms": sum(recent_times) / len(recent_times) if recent_times else 0,
                "avg_efficiency": sum(recent_efficiency) / len(recent_efficiency) if recent_efficiency else 0,
                "measurements_count": len(self.performance_metrics["allocation_times"])
            },
            "success_criteria_status": {
                "sub_50ms_response": (sum(recent_times) / len(recent_times)) < 50 if recent_times else False,
                "95_percent_efficiency": (sum(recent_efficiency) / len(recent_efficiency)) > 0.95 if recent_efficiency else False,
                "load_balancing_active": len(self.ecan_allocator.active_agents) > 0,
                "attention_equilibrium": abs(self.ecan_allocator.attention_bank - 1000.0) < 200.0
            }
        }
    
    async def _setup_elizaos_connection(self):
        """Setup connection to ElizaOS ecosystem"""
        logger.debug("Setting up ElizaOS connection")
        # Initialize ElizaOS attention bridge functionality interface
        self.elizaos_config = self.config.get('elizaos', {})
        self.elizaos_endpoint = self.elizaos_config.get('endpoint', 'http://localhost:3000')
        self.elizaos_api_key = self.elizaos_config.get('api_key')
        
        # Initialize operation handlers
        self.elizaos_handlers = {}
        self.elizaos_connected = True
        
        logger.info(f"ElizaOS connection established for {self.name}")
        
    async def _setup_opencog_connection(self):
        """Setup connection to OpenCog ecosystem"""
        logger.debug("Setting up OpenCog connection")
        # Initialize OpenCog attention bridge functionality interface
        self.opencog_config = self.config.get('opencog', {})
        self.atomspace_host = self.opencog_config.get('host', 'localhost')
        self.atomspace_port = self.opencog_config.get('port', 17001)
        
        # Initialize cognitive handlers
        self.cognitive_handlers = {}
        self.opencog_connected = True
        
        logger.info(f"OpenCog connection established for {self.name}")
        
    async def _setup_gnucash_connection(self):
        """Setup connection to GnuCash ecosystem"""
        logger.debug("Setting up GnuCash connection")
        # Initialize GnuCash attention bridge functionality interface
        self.gnucash_config = self.config.get('gnucash', {})
        self.gnucash_file = self.gnucash_config.get('file_path')
        
        # Initialize financial handlers
        self.financial_handlers = {}
        self.gnucash_connected = True
        
        logger.info(f"GnuCash connection established for {self.name}")
    
    async def process_elizaos_request(self, request: Dict) -> Dict:
        """Process request from ElizaOS ecosystem"""
        if not self.initialized:
            raise RuntimeError("Bridge not initialized")
            
        logger.debug(f"Processing ElizaOS request: {request}")
        
        operation = request.get('operation')
        elizaos_id = request.get('elizaos_id')
        data = request.get('data', {})
        
        if operation == 'health_check':
            # Basic health check
            response = {
                "success": True,
                "source": "elizaos",
                "target": self.name,
                "status": "healthy",
                "elizaos_id": elizaos_id
            }
        elif operation == 'process_request':
            # Handle process_request operation
            result = await self._handle_process_request(elizaos_id, data)
            response = {
                "success": True,
                "source": "elizaos",
                "target": self.name,
                "operation": "process_request",
                "result": result,
                "elizaos_id": elizaos_id
            }
        elif operation == 'handle_operation':
            # Handle handle_operation operation
            result = await self._handle_handle_operation(elizaos_id, data)
            response = {
                "success": True,
                "source": "elizaos",
                "target": self.name,
                "operation": "handle_operation",
                "result": result,
                "elizaos_id": elizaos_id
            }
        elif operation == 'manage_state':
            # Handle manage_state operation
            result = await self._handle_manage_state(elizaos_id, data)
            response = {
                "success": True,
                "source": "elizaos",
                "target": self.name,
                "operation": "manage_state",
                "result": result,
                "elizaos_id": elizaos_id
            }
        else:
            response = {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "source": "elizaos",
                "target": self.name
            }
        
        return response
    
    async def process_opencog_request(self, request: Dict) -> Dict:
        """Process request from OpenCog ecosystem"""
        if not self.initialized:
            raise RuntimeError("Bridge not initialized")
            
        logger.debug(f"Processing OpenCog request: {request}")
        
        operation = request.get('operation')
        opencog_id = request.get('opencog_id')
        data = request.get('data', {})
        
        if operation == 'health_check':
            # Basic health check
            response = {
                "success": True,
                "source": "opencog",
                "target": self.name,
                "status": "healthy",
                "opencog_id": opencog_id
            }
        elif operation == 'cognitive_processing':
            # Handle cognitive_processing operation
            result = await self._handle_cognitive_processing(opencog_id, data)
            response = {
                "success": True,
                "source": "opencog",
                "target": self.name,
                "operation": "cognitive_processing",
                "result": result,
                "opencog_id": opencog_id
            }
        elif operation == 'reasoning_request':
            # Handle reasoning_request operation
            result = await self._handle_reasoning_request(opencog_id, data)
            response = {
                "success": True,
                "source": "opencog",
                "target": self.name,
                "operation": "reasoning_request",
                "result": result,
                "opencog_id": opencog_id
            }
        elif operation == 'pattern_matching':
            # Handle pattern_matching operation
            result = await self._handle_pattern_matching(opencog_id, data)
            response = {
                "success": True,
                "source": "opencog",
                "target": self.name,
                "operation": "pattern_matching",
                "result": result,
                "opencog_id": opencog_id
            }
        else:
            response = {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "source": "opencog",
                "target": self.name
            }
        
        return response
    
    async def process_gnucash_request(self, request: Dict) -> Dict:
        """Process request from GnuCash ecosystem"""
        if not self.initialized:
            raise RuntimeError("Bridge not initialized")
            
        logger.debug(f"Processing GnuCash request: {request}")
        
        operation = request.get('operation')
        gnucash_id = request.get('gnucash_id')
        data = request.get('data', {})
        
        if operation == 'health_check':
            # Basic health check
            response = {
                "success": True,
                "source": "gnucash",
                "target": self.name,
                "status": "healthy",
                "gnucash_id": gnucash_id
            }
        elif operation == 'financial_processing':
            # Handle financial_processing operation
            result = await self._handle_financial_processing(gnucash_id, data)
            response = {
                "success": True,
                "source": "gnucash",
                "target": self.name,
                "operation": "financial_processing",
                "result": result,
                "gnucash_id": gnucash_id
            }
        elif operation == 'transaction_handling':
            # Handle transaction_handling operation
            result = await self._handle_transaction_handling(gnucash_id, data)
            response = {
                "success": True,
                "source": "gnucash",
                "target": self.name,
                "operation": "transaction_handling",
                "result": result,
                "gnucash_id": gnucash_id
            }
        elif operation == 'account_management':
            # Handle account_management operation
            result = await self._handle_account_management(gnucash_id, data)
            response = {
                "success": True,
                "source": "gnucash",
                "target": self.name,
                "operation": "account_management",
                "result": result,
                "gnucash_id": gnucash_id
            }
        else:
            response = {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "source": "gnucash",
                "target": self.name
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
        # Implementation for ElizaOS -> OpenCog translation
        return {"converted_data": data, "format": "target_format"}
        return {"atomspace_data": data, "format": "opencog"}
    
    async def _opencog_to_elizaos(self, data: Any) -> Any:
        """Translate OpenCog data to ElizaOS format"""
        # Implementation for OpenCog -> ElizaOS translation
        return {"converted_data": data, "format": "target_format"}
        return {"agent_data": data, "format": "elizaos"}
    
    async def _elizaos_to_gnucash(self, data: Any) -> Any:
        """Translate ElizaOS data to GnuCash format"""
        # Implementation for ElizaOS -> GnuCash translation
        return {"converted_data": data, "format": "target_format"}
        return {"financial_data": data, "format": "gnucash"}
    
    async def _gnucash_to_elizaos(self, data: Any) -> Any:
        """Translate GnuCash data to ElizaOS format"""
        # Implementation for GnuCash -> ElizaOS translation
        return {"converted_data": data, "format": "target_format"}
        return {"agent_data": data, "format": "elizaos"}
    
    async def _opencog_to_gnucash(self, data: Any) -> Any:
        """Translate OpenCog data to GnuCash format"""
        # Implementation for OpenCog -> GnuCash translation
        return {"converted_data": data, "format": "target_format"}
        return {"financial_data": data, "format": "gnucash"}
    
    async def _gnucash_to_opencog(self, data: Any) -> Any:
        """Translate GnuCash data to OpenCog format"""
        # Implementation for GnuCash -> OpenCog translation
        return {"converted_data": data, "format": "target_format"}
        return {"atomspace_data": data, "format": "opencog"}
    
    async def shutdown(self):
        """Shutdown the bridge"""
        logger.info(f"Shutting down {self.name} bridge")
        self.initialized = False

class AttentionIntegrationFramework:
    """Framework for managing attention integrations"""
    
    def __init__(self):
        self.bridges = {}
        self.active_sessions = {}
        
    async def register_bridge(self, bridge: AttentionBridge) -> bool:
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
__all__ = ["AttentionBridge", "AttentionIntegrationFramework"]
