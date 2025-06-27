"""
Multi-Agent Coordination Framework - Phase 3 Implementation
Advanced coordination protocols for financial agent collaboration
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COMMAND = "command"
    HEARTBEAT = "heartbeat"
    COORDINATION = "coordination"


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    ERROR = "error"
    OFFLINE = "offline"


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    message_type: MessageType = MessageType.REQUEST
    content: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)
    response_required: bool = True
    timeout_seconds: int = 30
    correlation_id: Optional[str] = None


@dataclass
class TaskAllocation:
    """Task allocation information"""
    task_id: str
    agent_id: str
    task_type: str
    priority: Priority
    estimated_duration: float
    assigned_at: datetime
    deadline: Optional[datetime] = None


@dataclass
class ConsensusProposal:
    """Proposal for consensus decision making"""
    proposal_id: str
    proposer: str
    topic: str
    options: List[Dict[str, Any]]
    votes: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: datetime = field(default_factory=lambda: datetime.now())


class MultiAgentCoordinator:
    """
    Advanced multi-agent coordination system for financial analysis
    Handles communication protocols, distributed reasoning, conflict resolution,
    consensus algorithms, and load balancing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.message_queue: List[AgentMessage] = []
        self.task_queue: List[Dict[str, Any]] = []
        self.active_tasks: Dict[str, TaskAllocation] = {}
        self.consensus_proposals: Dict[str, ConsensusProposal] = {}
        
        # Communication setup
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Load balancing
        self.agent_workload: Dict[str, float] = {}
        self.agent_states: Dict[str, AgentState] = {}
        
        # Conflict resolution
        self.conflict_resolution_rules: List[Dict[str, Any]] = []
        self.active_conflicts: List[Dict[str, Any]] = []
        
        self._setup_default_handlers()
    
    async def register_agent(self, agent_id: str, agent_capabilities: Dict[str, Any]) -> bool:
        """Register a new agent in the coordination system"""
        try:
            self.agents[agent_id] = {
                "capabilities": agent_capabilities,
                "last_heartbeat": datetime.now(),
                "message_count": 0,
                "task_count": 0,
                "state": AgentState.IDLE
            }
            
            self.agent_workload[agent_id] = 0.0
            self.agent_states[agent_id] = AgentState.IDLE
            
            logger.info(f"Agent {agent_id} registered with capabilities: {agent_capabilities}")
            
            # Notify other agents of new registration
            await self._broadcast_message(AgentMessage(
                sender="coordinator",
                message_type=MessageType.NOTIFICATION,
                content={
                    "event": "agent_registered",
                    "agent_id": agent_id,
                    "capabilities": agent_capabilities
                },
                response_required=False
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    async def send_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Send message between agents with coordination logic"""
        try:
            # Validate message
            if not self._validate_message(message):
                logger.warning(f"Invalid message from {message.sender} to {message.recipient}")
                return None
            
            # Check recipient availability
            if message.recipient != "all" and message.recipient not in self.agents:
                logger.warning(f"Recipient {message.recipient} not found")
                return None
            
            # Handle coordination logic
            if message.message_type == MessageType.COORDINATION:
                return await self._handle_coordination_message(message)
            
            # Queue message for delivery
            self.message_queue.append(message)
            
            # Process immediately if high priority
            if message.priority in [Priority.HIGH, Priority.CRITICAL]:
                return await self._process_message_immediately(message)
            
            return {"status": "queued", "message_id": message.id}
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    async def coordinate_distributed_reasoning(self, 
                                             reasoning_task: Dict[str, Any], 
                                             required_agents: List[str]) -> Dict[str, Any]:
        """
        Coordinate distributed reasoning across multiple financial agents
        """
        logger.info(f"Starting distributed reasoning task: {reasoning_task.get('task_id', 'unknown')}")
        
        task_id = reasoning_task.get('task_id', str(uuid.uuid4()))
        reasoning_results = {}
        
        # Phase 1: Task decomposition
        subtasks = await self._decompose_reasoning_task(reasoning_task, required_agents)
        
        # Phase 2: Agent allocation
        agent_assignments = await self._allocate_reasoning_tasks(subtasks, required_agents)
        
        # Phase 3: Parallel execution
        execution_futures = []
        for agent_id, assigned_tasks in agent_assignments.items():
            if agent_id in self.agents:
                future = asyncio.create_task(
                    self._execute_agent_reasoning(agent_id, assigned_tasks, task_id)
                )
                execution_futures.append((agent_id, future))
        
        # Phase 4: Collect results
        for agent_id, future in execution_futures:
            try:
                agent_result = await asyncio.wait_for(future, timeout=60)
                reasoning_results[agent_id] = agent_result
            except asyncio.TimeoutError:
                logger.warning(f"Agent {agent_id} reasoning timed out")
                reasoning_results[agent_id] = {"error": "timeout"}
            except Exception as e:
                logger.error(f"Agent {agent_id} reasoning failed: {e}")
                reasoning_results[agent_id] = {"error": str(e)}
        
        # Phase 5: Result synthesis
        synthesized_result = await self._synthesize_reasoning_results(reasoning_results, reasoning_task)
        
        return {
            "task_id": task_id,
            "reasoning_result": synthesized_result,
            "agent_contributions": reasoning_results,
            "execution_metadata": {
                "subtasks_created": len(subtasks),
                "agents_involved": len(agent_assignments),
                "completion_time": datetime.now().isoformat()
            }
        }
    
    async def resolve_conflicts(self, conflict_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve conflicts between agents using established resolution mechanisms
        """
        conflict_id = str(uuid.uuid4())
        conflict_type = conflict_scenario.get('type', 'unknown')
        
        logger.info(f"Resolving conflict {conflict_id} of type: {conflict_type}")
        
        # Identify conflicting agents and their positions
        conflicting_agents = conflict_scenario.get('agents', [])
        agent_positions = conflict_scenario.get('positions', {})
        
        # Apply conflict resolution strategy based on type
        resolution_strategy = await self._select_resolution_strategy(conflict_type, conflicting_agents)
        
        if resolution_strategy == "voting":
            resolution = await self._resolve_by_voting(conflict_id, agent_positions)
        elif resolution_strategy == "priority_based":
            resolution = await self._resolve_by_priority(conflict_id, agent_positions)
        elif resolution_strategy == "consensus":
            resolution = await self._resolve_by_consensus(conflict_id, agent_positions)
        elif resolution_strategy == "coordinator_decision":
            resolution = await self._resolve_by_coordinator(conflict_id, agent_positions)
        else:
            resolution = {"error": f"Unknown resolution strategy: {resolution_strategy}"}
        
        # Record conflict resolution
        conflict_record = {
            "conflict_id": conflict_id,
            "type": conflict_type,
            "agents": conflicting_agents,
            "resolution_strategy": resolution_strategy,
            "resolution": resolution,
            "resolved_at": datetime.now().isoformat()
        }
        
        self.active_conflicts.append(conflict_record)
        
        # Notify agents of resolution
        await self._notify_conflict_resolution(conflicting_agents, conflict_record)
        
        return conflict_record
    
    async def consensus_decision(self, 
                               decision_topic: str, 
                               options: List[Dict[str, Any]], 
                               participants: List[str],
                               timeout_minutes: int = 10) -> Dict[str, Any]:
        """
        Facilitate consensus decision making among financial agents
        """
        proposal_id = str(uuid.uuid4())
        deadline = datetime.now()
        
        logger.info(f"Starting consensus decision {proposal_id} on topic: {decision_topic}")
        
        # Create consensus proposal
        proposal = ConsensusProposal(
            proposal_id=proposal_id,
            proposer="coordinator",
            topic=decision_topic,
            options=options,
            deadline=deadline
        )
        
        self.consensus_proposals[proposal_id] = proposal
        
        # Send voting requests to participants
        voting_tasks = []
        for agent_id in participants:
            if agent_id in self.agents:
                vote_request = AgentMessage(
                    sender="coordinator",
                    recipient=agent_id,
                    message_type=MessageType.REQUEST,
                    content={
                        "action": "consensus_vote",
                        "proposal_id": proposal_id,
                        "topic": decision_topic,
                        "options": options,
                        "deadline": deadline.isoformat()
                    },
                    priority=Priority.HIGH
                )
                
                task = asyncio.create_task(self._collect_vote(agent_id, vote_request))
                voting_tasks.append(task)
        
        # Collect votes with timeout
        collected_votes = {}
        try:
            vote_results = await asyncio.wait_for(
                asyncio.gather(*voting_tasks, return_exceptions=True),
                timeout=timeout_minutes * 60
            )
            
            for i, result in enumerate(vote_results):
                if not isinstance(result, Exception):
                    agent_id = participants[i]
                    collected_votes[agent_id] = result
                    
        except asyncio.TimeoutError:
            logger.warning(f"Consensus voting timed out for proposal {proposal_id}")
        
        # Analyze consensus
        consensus_result = await self._analyze_consensus(proposal_id, collected_votes, options)
        
        # Update proposal with final votes
        proposal.votes = collected_votes
        
        return {
            "proposal_id": proposal_id,
            "topic": decision_topic,
            "votes_collected": len(collected_votes),
            "total_participants": len(participants),
            "consensus_achieved": consensus_result.get("consensus_achieved", False),
            "winning_option": consensus_result.get("winning_option"),
            "vote_distribution": consensus_result.get("vote_distribution", {}),
            "confidence_score": consensus_result.get("confidence_score", 0.0)
        }
    
    async def balance_workload(self) -> Dict[str, Any]:
        """
        Implement load balancing across cognitive financial agents
        """
        logger.info("Performing workload balancing across agents")
        
        # Calculate current workload distribution
        current_workloads = {}
        for agent_id in self.agents:
            workload = await self._calculate_agent_workload(agent_id)
            current_workloads[agent_id] = workload
            self.agent_workload[agent_id] = workload
        
        # Identify overloaded and underloaded agents
        avg_workload = sum(current_workloads.values()) / len(current_workloads) if current_workloads else 0
        overloaded_agents = [aid for aid, load in current_workloads.items() if load > avg_workload * 1.5]
        underloaded_agents = [aid for aid, load in current_workloads.items() if load < avg_workload * 0.5]
        
        # Task redistribution
        redistributed_tasks = []
        for overloaded_agent in overloaded_agents:
            if underloaded_agents:
                # Find suitable tasks to redistribute
                redistributable_tasks = await self._find_redistributable_tasks(overloaded_agent)
                
                for task in redistributable_tasks[:2]:  # Limit redistribution
                    target_agent = self._select_best_target_agent(task, underloaded_agents)
                    if target_agent:
                        success = await self._redistribute_task(task, overloaded_agent, target_agent)
                        if success:
                            redistributed_tasks.append({
                                "task_id": task["task_id"],
                                "from_agent": overloaded_agent,
                                "to_agent": target_agent
                            })
                            
                            # Update workload estimates
                            self.agent_workload[overloaded_agent] -= task.get("workload_estimate", 0.1)
                            self.agent_workload[target_agent] += task.get("workload_estimate", 0.1)
        
        # Update agent states based on new workloads
        for agent_id, workload in self.agent_workload.items():
            if workload > 0.8:
                self.agent_states[agent_id] = AgentState.OVERLOADED
            elif workload > 0.5:
                self.agent_states[agent_id] = AgentState.BUSY
            else:
                self.agent_states[agent_id] = AgentState.IDLE
        
        return {
            "balance_timestamp": datetime.now().isoformat(),
            "workload_distribution": current_workloads,
            "average_workload": avg_workload,
            "overloaded_agents": overloaded_agents,
            "underloaded_agents": underloaded_agents,
            "redistributed_tasks": redistributed_tasks,
            "new_agent_states": dict(self.agent_states)
        }
    
    # Helper methods for coordination functionality
    
    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self.message_handlers.update({
            MessageType.HEARTBEAT.value: self._handle_heartbeat,
            MessageType.REQUEST.value: self._handle_request,
            MessageType.RESPONSE.value: self._handle_response,
            MessageType.NOTIFICATION.value: self._handle_notification,
            MessageType.COORDINATION.value: self._handle_coordination_message
        })
    
    def _validate_message(self, message: AgentMessage) -> bool:
        """Validate message format and content"""
        if not message.sender or not message.recipient:
            return False
        if message.recipient != "all" and message.recipient not in self.agents and message.recipient != "coordinator":
            return False
        return True
    
    async def _handle_coordination_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle coordination-specific messages"""
        content = message.content
        action = content.get("action")
        
        if action == "request_workload_balance":
            return await self.balance_workload()
        elif action == "propose_consensus":
            return await self.consensus_decision(
                content["topic"], content["options"], content["participants"]
            )
        elif action == "report_conflict":
            return await self.resolve_conflicts(content["conflict_scenario"])
        else:
            return {"error": f"Unknown coordination action: {action}"}
    
    async def _broadcast_message(self, message: AgentMessage):
        """Broadcast message to all agents"""
        for agent_id in self.agents:
            individual_message = AgentMessage(
                sender=message.sender,
                recipient=agent_id,
                message_type=message.message_type,
                content=message.content,
                priority=message.priority,
                response_required=message.response_required
            )
            await self.send_message(individual_message)
    
    async def _process_message_immediately(self, message: AgentMessage) -> Dict[str, Any]:
        """Process high priority messages immediately"""
        handler = self.message_handlers.get(message.message_type.value)
        if handler:
            return await handler(message)
        return {"error": "No handler found for message type"}
    
    # Distributed reasoning helpers
    
    async def _decompose_reasoning_task(self, task: Dict[str, Any], agents: List[str]) -> List[Dict[str, Any]]:
        """Decompose a complex reasoning task into subtasks"""
        task_type = task.get("type", "analysis")
        
        if task_type == "financial_analysis":
            return [
                {"subtask": "data_preparation", "agent_types": ["data_processor"]},
                {"subtask": "pattern_analysis", "agent_types": ["pattern_analyzer"]},
                {"subtask": "risk_assessment", "agent_types": ["risk_analyzer"]},
                {"subtask": "recommendation_generation", "agent_types": ["advisor"]}
            ]
        elif task_type == "budget_optimization":
            return [
                {"subtask": "current_spending_analysis", "agent_types": ["expense_analyzer"]},
                {"subtask": "goal_evaluation", "agent_types": ["budget_planner"]},
                {"subtask": "optimization_modeling", "agent_types": ["optimizer"]},
                {"subtask": "implementation_planning", "agent_types": ["planner"]}
            ]
        else:
            # Generic decomposition
            return [{"subtask": "general_analysis", "agent_types": ["any"]}]
    
    async def _allocate_reasoning_tasks(self, subtasks: List[Dict[str, Any]], available_agents: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Allocate reasoning subtasks to appropriate agents"""
        allocations = {}
        
        for subtask in subtasks:
            required_types = subtask.get("agent_types", ["any"])
            
            # Find suitable agents
            suitable_agents = []
            for agent_id in available_agents:
                agent_info = self.agents.get(agent_id, {})
                agent_capabilities = agent_info.get("capabilities", {})
                agent_type = agent_capabilities.get("type", "general")
                
                if "any" in required_types or agent_type in required_types:
                    suitable_agents.append(agent_id)
            
            # Allocate to least loaded suitable agent
            if suitable_agents:
                best_agent = min(suitable_agents, key=lambda a: self.agent_workload.get(a, 0))
                if best_agent not in allocations:
                    allocations[best_agent] = []
                allocations[best_agent].append(subtask)
        
        return allocations
    
    async def _execute_agent_reasoning(self, agent_id: str, tasks: List[Dict[str, Any]], task_id: str) -> Dict[str, Any]:
        """Execute reasoning tasks on a specific agent"""
        # Mock implementation - in reality, this would send tasks to the actual agent
        results = []
        
        for task in tasks:
            # Simulate reasoning execution
            await asyncio.sleep(0.1)  # Simulate processing time
            
            result = {
                "subtask": task["subtask"],
                "status": "completed",
                "findings": f"Analysis complete for {task['subtask']}",
                "confidence": 0.8,
                "processing_time": 0.1
            }
            results.append(result)
        
        return {
            "agent_id": agent_id,
            "task_id": task_id,
            "subtask_results": results,
            "overall_status": "completed",
            "execution_timestamp": datetime.now().isoformat()
        }
    
    async def _synthesize_reasoning_results(self, agent_results: Dict[str, Any], original_task: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize distributed reasoning results into final conclusion"""
        successful_results = [r for r in agent_results.values() if r.get("overall_status") == "completed"]
        
        if not successful_results:
            return {"error": "No successful reasoning results to synthesize"}
        
        # Extract findings from all agents
        all_findings = []
        confidence_scores = []
        
        for result in successful_results:
            subtask_results = result.get("subtask_results", [])
            for subtask_result in subtask_results:
                all_findings.append(subtask_result.get("findings", ""))
                confidence_scores.append(subtask_result.get("confidence", 0.5))
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            "synthesis_summary": f"Distributed reasoning analysis completed with {len(successful_results)} agents",
            "key_findings": all_findings,
            "overall_confidence": overall_confidence,
            "participating_agents": len(successful_results),
            "synthesis_timestamp": datetime.now().isoformat(),
            "original_task_type": original_task.get("type", "unknown")
        }
    
    # Conflict resolution helpers
    
    async def _select_resolution_strategy(self, conflict_type: str, agents: List[str]) -> str:
        """Select appropriate conflict resolution strategy"""
        if conflict_type == "resource_allocation":
            return "priority_based"
        elif conflict_type == "data_interpretation":
            return "consensus"
        elif conflict_type == "task_assignment":
            return "coordinator_decision"
        else:
            return "voting"
    
    async def _resolve_by_voting(self, conflict_id: str, positions: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict through agent voting"""
        vote_counts = {}
        for agent, position in positions.items():
            vote = position.get("preferred_option", "abstain")
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        winning_option = max(vote_counts.items(), key=lambda x: x[1])[0] if vote_counts else "no_consensus"
        
        return {
            "resolution_method": "voting",
            "winning_option": winning_option,
            "vote_distribution": vote_counts,
            "total_votes": sum(vote_counts.values())
        }
    
    async def _resolve_by_priority(self, conflict_id: str, positions: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict based on agent priorities"""
        # Find highest priority agent's position
        highest_priority_agent = None
        highest_priority = 0
        
        for agent, position in positions.items():
            agent_priority = self.agents.get(agent, {}).get("priority", 1)
            if agent_priority > highest_priority:
                highest_priority = agent_priority
                highest_priority_agent = agent
        
        resolution = positions.get(highest_priority_agent, {}).get("preferred_option", "no_resolution")
        
        return {
            "resolution_method": "priority_based",
            "deciding_agent": highest_priority_agent,
            "resolution": resolution,
            "priority_level": highest_priority
        }
    
    async def _resolve_by_consensus(self, conflict_id: str, positions: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict through consensus building"""
        # Check for unanimous agreement
        unique_positions = set(pos.get("preferred_option") for pos in positions.values())
        
        if len(unique_positions) == 1:
            return {
                "resolution_method": "consensus",
                "consensus_achieved": True,
                "agreed_option": list(unique_positions)[0]
            }
        else:
            return {
                "resolution_method": "consensus",
                "consensus_achieved": False,
                "fallback_to": "coordinator_decision"
            }
    
    async def _resolve_by_coordinator(self, conflict_id: str, positions: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict through coordinator decision"""
        # Coordinator makes final decision based on available information
        options = [pos.get("preferred_option") for pos in positions.values()]
        
        # Simple heuristic: choose the most common option, or first if tie
        option_counts = {}
        for option in options:
            option_counts[option] = option_counts.get(option, 0) + 1
        
        coordinator_decision = max(option_counts.items(), key=lambda x: x[1])[0] if option_counts else "default"
        
        return {
            "resolution_method": "coordinator_decision",
            "coordinator_choice": coordinator_decision,
            "rationale": "Selected based on frequency analysis of agent preferences"
        }
    
    async def _notify_conflict_resolution(self, agents: List[str], resolution: Dict[str, Any]):
        """Notify agents of conflict resolution"""
        notification = AgentMessage(
            sender="coordinator",
            message_type=MessageType.NOTIFICATION,
            content={
                "event": "conflict_resolved",
                "resolution": resolution
            },
            response_required=False
        )
        
        for agent_id in agents:
            if agent_id in self.agents:
                notification.recipient = agent_id
                await self.send_message(notification)
    
    # Consensus decision helpers
    
    async def _collect_vote(self, agent_id: str, vote_request: AgentMessage) -> Optional[str]:
        """Collect vote from an agent"""
        try:
            # In real implementation, this would send request to agent and wait for response
            # Mock response for demonstration
            await asyncio.sleep(0.1)  # Simulate agent deliberation time
            
            # Mock voting logic - agents vote based on their "personality"
            agent_info = self.agents.get(agent_id, {})
            agent_type = agent_info.get("capabilities", {}).get("type", "general")
            
            options = vote_request.content.get("options", [])
            if not options:
                return "abstain"
            
            # Simple voting logic based on agent type
            if agent_type == "conservative":
                return options[0].get("value", "option_1")  # Choose first option
            elif agent_type == "aggressive":
                return options[-1].get("value", "option_last")  # Choose last option
            else:
                return options[len(options)//2].get("value", "option_middle")  # Choose middle option
                
        except Exception as e:
            logger.error(f"Error collecting vote from {agent_id}: {e}")
            return None
    
    async def _analyze_consensus(self, proposal_id: str, votes: Dict[str, str], options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consensus results"""
        if not votes:
            return {"consensus_achieved": False, "reason": "no_votes_collected"}
        
        # Count votes for each option
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        total_votes = len(votes)
        majority_threshold = total_votes * 0.6  # 60% for consensus
        
        # Find winning option
        winning_option = max(vote_counts.items(), key=lambda x: x[1]) if vote_counts else ("no_winner", 0)
        winning_count = winning_option[1]
        
        consensus_achieved = winning_count >= majority_threshold
        confidence_score = winning_count / total_votes if total_votes > 0 else 0.0
        
        return {
            "consensus_achieved": consensus_achieved,
            "winning_option": winning_option[0],
            "vote_distribution": vote_counts,
            "confidence_score": confidence_score,
            "total_participants": total_votes
        }
    
    # Load balancing helpers
    
    async def _calculate_agent_workload(self, agent_id: str) -> float:
        """Calculate current workload for an agent"""
        # Count active tasks assigned to agent
        active_task_count = len([task for task in self.active_tasks.values() if task.agent_id == agent_id])
        
        # Count queued messages for agent
        queued_message_count = len([msg for msg in self.message_queue if msg.recipient == agent_id])
        
        # Calculate workload score (0.0 = idle, 1.0 = fully loaded)
        task_load = min(active_task_count / 5.0, 1.0)  # Max 5 concurrent tasks
        message_load = min(queued_message_count / 10.0, 0.5)  # Max queue impact of 0.5
        
        return min(task_load + message_load, 1.0)
    
    async def _find_redistributable_tasks(self, agent_id: str) -> List[Dict[str, Any]]:
        """Find tasks that can be redistributed from overloaded agent"""
        redistributable = []
        
        agent_tasks = [task for task in self.active_tasks.values() if task.agent_id == agent_id]
        
        # Tasks eligible for redistribution: non-critical priority, not close to deadline
        for task_allocation in agent_tasks:
            if task_allocation.priority != Priority.CRITICAL:
                time_remaining = (task_allocation.deadline - datetime.now()).total_seconds() if task_allocation.deadline else float('inf')
                if time_remaining > 3600:  # More than 1 hour remaining
                    redistributable.append({
                        "task_id": task_allocation.task_id,
                        "task_type": task_allocation.task_type,
                        "priority": task_allocation.priority,
                        "workload_estimate": task_allocation.estimated_duration
                    })
        
        return redistributable
    
    def _select_best_target_agent(self, task: Dict[str, Any], candidates: List[str]) -> Optional[str]:
        """Select best agent to receive redistributed task"""
        if not candidates:
            return None
        
        # Select agent with lowest workload and compatible capabilities
        best_agent = None
        lowest_workload = float('inf')
        
        for agent_id in candidates:
            agent_workload = self.agent_workload.get(agent_id, 0)
            agent_capabilities = self.agents.get(agent_id, {}).get("capabilities", {})
            
            # Check if agent can handle this task type
            task_type = task.get("task_type", "general")
            agent_types = agent_capabilities.get("task_types", ["general"])
            
            if task_type in agent_types or "general" in agent_types:
                if agent_workload < lowest_workload:
                    lowest_workload = agent_workload
                    best_agent = agent_id
        
        return best_agent
    
    async def _redistribute_task(self, task: Dict[str, Any], from_agent: str, to_agent: str) -> bool:
        """Redistribute task from one agent to another"""
        try:
            task_id = task["task_id"]
            
            # Remove from original agent
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            # Assign to new agent
            new_allocation = TaskAllocation(
                task_id=task_id,
                agent_id=to_agent,
                task_type=task["task_type"],
                priority=task["priority"],
                estimated_duration=task.get("workload_estimate", 1.0),
                assigned_at=datetime.now()
            )
            
            self.active_tasks[task_id] = new_allocation
            
            # Notify both agents
            await self._notify_task_redistribution(from_agent, to_agent, task)
            
            logger.info(f"Redistributed task {task_id} from {from_agent} to {to_agent}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to redistribute task: {e}")
            return False
    
    async def _notify_task_redistribution(self, from_agent: str, to_agent: str, task: Dict[str, Any]):
        """Notify agents about task redistribution"""
        # Notify original agent
        removal_message = AgentMessage(
            sender="coordinator",
            recipient=from_agent,
            message_type=MessageType.NOTIFICATION,
            content={
                "event": "task_removed",
                "task_id": task["task_id"],
                "reason": "workload_balancing"
            },
            response_required=False
        )
        
        # Notify new agent
        assignment_message = AgentMessage(
            sender="coordinator",
            recipient=to_agent,
            message_type=MessageType.COMMAND,
            content={
                "action": "accept_task",
                "task": task,
                "source": "redistribution"
            },
            priority=Priority.MEDIUM
        )
        
        await self.send_message(removal_message)
        await self.send_message(assignment_message)
    
    # Default message handlers
    
    async def _handle_heartbeat(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle agent heartbeat messages"""
        agent_id = message.sender
        if agent_id in self.agents:
            self.agents[agent_id]["last_heartbeat"] = datetime.now()
            return {"status": "heartbeat_acknowledged"}
        return {"error": "unknown_agent"}
    
    async def _handle_request(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle general request messages"""
        return {"status": "request_processed", "message_id": message.id}
    
    async def _handle_response(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle response messages"""
        return {"status": "response_received", "message_id": message.id}
    
    async def _handle_notification(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle notification messages"""
        return {"status": "notification_processed", "message_id": message.id}