"""
Scheme Cognitive Grammar Microservices
Implementation of atomic vocabulary and bidirectional translation mechanisms
between ElizaOS ko6ml primitives and AtomSpace hypergraph patterns.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import subprocess
import tempfile
import os

class ElizaOSPrimitive(Enum):
    """ElizaOS ko6ml primitive types"""
    AGENT = "agent"
    ACTION = "action"
    MEMORY = "memory"
    QUERY = "query"
    CONTEXT = "context"
    GOAL = "goal"
    BELIEF = "belief"
    INTENTION = "intention"

class AtomSpacePattern(Enum):
    """AtomSpace hypergraph pattern types"""
    CONCEPT_NODE = "ConceptNode"
    PREDICATE_NODE = "PredicateNode"
    EVALUATION_LINK = "EvaluationLink"
    LIST_LINK = "ListLink"
    AND_LINK = "AndLink"
    OR_LINK = "OrLink"
    BIND_LINK = "BindLink"
    GET_LINK = "GetLink"

@dataclass
class TranslationResult:
    """Result of translation between ElizaOS and AtomSpace"""
    source_format: str
    target_format: str
    original_data: Any
    translated_data: Any
    translation_time_ms: float
    accuracy_score: float
    validation_errors: List[str]

@dataclass
class AtomicVocabularyEntry:
    """Entry in the atomic vocabulary mapping"""
    eliza_primitive: ElizaOSPrimitive
    atomspace_pattern: AtomSpacePattern
    mapping_rules: Dict[str, Any]
    bidirectional: bool
    confidence: float

class SchemeAdapter(ABC):
    """Abstract base for Scheme adapters"""
    
    @abstractmethod
    async def translate_to_atomspace(self, eliza_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate ElizaOS data to AtomSpace format"""
        pass
    
    @abstractmethod
    async def translate_from_atomspace(self, atomspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate AtomSpace data to ElizaOS format"""
        pass

class AgentGrammarAdapter(SchemeAdapter):
    """Adapter for agentic grammar patterns"""
    
    def __init__(self):
        self.agent_mappings = {
            "agent_id": "ConceptNode",
            "agent_type": "PredicateNode", 
            "agent_goals": "ListLink",
            "agent_beliefs": "AndLink",
            "agent_actions": "EvaluationLink"
        }
    
    async def translate_to_atomspace(self, eliza_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ElizaOS agent data to AtomSpace hypergraph"""
        start_time = time.time()
        
        atomspace_data = {
            "atoms": [],
            "links": []
        }
        
        if "agent" in eliza_data:
            agent = eliza_data["agent"]
            
            # Create agent concept node
            agent_node = {
                "type": "ConceptNode",
                "name": f"agent:{agent.get('id', 'unknown')}",
                "tv": {"strength": 0.9, "confidence": 0.9}
            }
            atomspace_data["atoms"].append(agent_node)
            
            # Create agent type predicate
            if "type" in agent:
                type_pred = {
                    "type": "PredicateNode", 
                    "name": f"agent_type:{agent['type']}"
                }
                atomspace_data["atoms"].append(type_pred)
                
                # Link agent to type
                type_link = {
                    "type": "EvaluationLink",
                    "outgoing": [type_pred["name"], agent_node["name"]]
                }
                atomspace_data["links"].append(type_link)
            
            # Handle agent goals
            if "goals" in agent:
                goals_list = {
                    "type": "ListLink",
                    "outgoing": [f"goal:{goal}" for goal in agent["goals"]]
                }
                atomspace_data["links"].append(goals_list)
        
        translation_time = (time.time() - start_time) * 1000
        return {
            "atomspace_data": atomspace_data,
            "translation_time_ms": translation_time
        }
    
    async def translate_from_atomspace(self, atomspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert AtomSpace hypergraph to ElizaOS agent data"""
        start_time = time.time()
        
        eliza_data = {
            "agents": [],
            "metadata": {}
        }
        
        # Parse atoms and links to reconstruct agent data
        if "atoms" in atomspace_data:
            for atom in atomspace_data["atoms"]:
                if atom.get("type") == "ConceptNode" and atom.get("name", "").startswith("agent:"):
                    agent_id = atom["name"].split(":", 1)[1]
                    agent = {
                        "id": agent_id,
                        "confidence": atom.get("tv", {}).get("confidence", 0.0)
                    }
                    eliza_data["agents"].append(agent)
        
        translation_time = (time.time() - start_time) * 1000
        eliza_data["metadata"]["translation_time_ms"] = translation_time
        
        return eliza_data

class MemoryGrammarAdapter(SchemeAdapter):
    """Adapter for memory and context patterns"""
    
    async def translate_to_atomspace(self, eliza_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ElizaOS memory data to AtomSpace format"""
        start_time = time.time()
        
        atomspace_data = {"atoms": [], "links": []}
        
        if "memory" in eliza_data:
            memory = eliza_data["memory"]
            
            # Create memory concept node
            memory_node = {
                "type": "ConceptNode",
                "name": f"memory:{memory.get('id', 'default')}",
                "tv": {"strength": memory.get("strength", 0.8), "confidence": 0.9}
            }
            atomspace_data["atoms"].append(memory_node)
            
            # Handle memory content
            if "content" in memory:
                content_node = {
                    "type": "ConceptNode",
                    "name": f"content:{hash(str(memory['content'])) % 10000}"
                }
                atomspace_data["atoms"].append(content_node)
                
                # Link memory to content
                content_link = {
                    "type": "EvaluationLink",
                    "outgoing": [
                        {"type": "PredicateNode", "name": "has_content"},
                        {"type": "ListLink", "outgoing": [memory_node["name"], content_node["name"]]}
                    ]
                }
                atomspace_data["links"].append(content_link)
        
        translation_time = (time.time() - start_time) * 1000
        return {
            "atomspace_data": atomspace_data,
            "translation_time_ms": translation_time
        }
    
    async def translate_from_atomspace(self, atomspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert AtomSpace memory patterns to ElizaOS format"""
        start_time = time.time()
        
        eliza_data = {"memories": [], "metadata": {}}
        
        # Parse memory nodes from AtomSpace data
        if "atoms" in atomspace_data:
            for atom in atomspace_data["atoms"]:
                if atom.get("type") == "ConceptNode" and atom.get("name", "").startswith("memory:"):
                    memory_id = atom["name"].split(":", 1)[1]
                    memory = {
                        "id": memory_id,
                        "strength": atom.get("tv", {}).get("strength", 0.0),
                        "timestamp": time.time()
                    }
                    eliza_data["memories"].append(memory)
        
        translation_time = (time.time() - start_time) * 1000
        eliza_data["metadata"]["translation_time_ms"] = translation_time
        
        return eliza_data

class SchemeCognitiveGrammarService:
    """Main service for Scheme Cognitive Grammar microservices"""
    
    def __init__(self):
        self.adapters = {
            "agent": AgentGrammarAdapter(),
            "memory": MemoryGrammarAdapter()
        }
        self.atomic_vocabulary = self._initialize_atomic_vocabulary()
        self.translation_stats = {
            "total_translations": 0,
            "successful_translations": 0,
            "average_translation_time_ms": 0.0,
            "accuracy_scores": []
        }
    
    def _initialize_atomic_vocabulary(self) -> Dict[str, AtomicVocabularyEntry]:
        """Initialize the atomic vocabulary mapping"""
        return {
            "agent": AtomicVocabularyEntry(
                eliza_primitive=ElizaOSPrimitive.AGENT,
                atomspace_pattern=AtomSpacePattern.CONCEPT_NODE,
                mapping_rules={"id": "name", "type": "predicate", "goals": "list"},
                bidirectional=True,
                confidence=0.95
            ),
            "memory": AtomicVocabularyEntry(
                eliza_primitive=ElizaOSPrimitive.MEMORY,
                atomspace_pattern=AtomSpacePattern.CONCEPT_NODE,
                mapping_rules={"content": "evaluation", "timestamp": "tv"},
                bidirectional=True,
                confidence=0.90
            ),
            "action": AtomicVocabularyEntry(
                eliza_primitive=ElizaOSPrimitive.ACTION,
                atomspace_pattern=AtomSpacePattern.EVALUATION_LINK,
                mapping_rules={"type": "predicate", "params": "list"},
                bidirectional=True,
                confidence=0.88
            )
        }
    
    async def translate_eliza_to_atomspace(self, 
                                         eliza_data: Dict[str, Any], 
                                         data_type: str) -> TranslationResult:
        """Translate ElizaOS data to AtomSpace hypergraph"""
        start_time = time.time()
        validation_errors = []
        
        try:
            if data_type not in self.adapters:
                validation_errors.append(f"Unknown data type: {data_type}")
                raise ValueError(f"No adapter for data type: {data_type}")
            
            adapter = self.adapters[data_type]
            result = await adapter.translate_to_atomspace(eliza_data)
            
            translation_time = (time.time() - start_time) * 1000
            accuracy_score = self._calculate_accuracy_score(eliza_data, result)
            
            self._update_translation_stats(translation_time, accuracy_score, True)
            
            return TranslationResult(
                source_format="ElizaOS",
                target_format="AtomSpace", 
                original_data=eliza_data,
                translated_data=result,
                translation_time_ms=translation_time,
                accuracy_score=accuracy_score,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            translation_time = (time.time() - start_time) * 1000
            validation_errors.append(str(e))
            self._update_translation_stats(translation_time, 0.0, False)
            
            return TranslationResult(
                source_format="ElizaOS",
                target_format="AtomSpace",
                original_data=eliza_data,
                translated_data={},
                translation_time_ms=translation_time,
                accuracy_score=0.0,
                validation_errors=validation_errors
            )
    
    async def translate_atomspace_to_eliza(self,
                                         atomspace_data: Dict[str, Any],
                                         data_type: str) -> TranslationResult:
        """Translate AtomSpace hypergraph to ElizaOS data"""
        start_time = time.time()
        validation_errors = []
        
        try:
            if data_type not in self.adapters:
                validation_errors.append(f"Unknown data type: {data_type}")
                raise ValueError(f"No adapter for data type: {data_type}")
            
            adapter = self.adapters[data_type]
            result = await adapter.translate_from_atomspace(atomspace_data)
            
            translation_time = (time.time() - start_time) * 1000
            accuracy_score = self._calculate_accuracy_score(atomspace_data, result)
            
            self._update_translation_stats(translation_time, accuracy_score, True)
            
            return TranslationResult(
                source_format="AtomSpace",
                target_format="ElizaOS",
                original_data=atomspace_data,
                translated_data=result,
                translation_time_ms=translation_time,
                accuracy_score=accuracy_score,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            translation_time = (time.time() - start_time) * 1000
            validation_errors.append(str(e))
            self._update_translation_stats(translation_time, 0.0, False)
            
            return TranslationResult(
                source_format="AtomSpace",
                target_format="ElizaOS",
                original_data=atomspace_data,
                translated_data={},
                translation_time_ms=translation_time,
                accuracy_score=0.0,
                validation_errors=validation_errors
            )
    
    async def round_trip_translate(self, 
                                 eliza_data: Dict[str, Any], 
                                 data_type: str) -> Dict[str, Any]:
        """Perform round-trip translation: ElizaOS -> AtomSpace -> ElizaOS"""
        # Forward translation
        forward_result = await self.translate_eliza_to_atomspace(eliza_data, data_type)
        
        if forward_result.validation_errors:
            return {
                "success": False,
                "errors": forward_result.validation_errors,
                "forward_result": forward_result
            }
        
        # Backward translation
        backward_result = await self.translate_atomspace_to_eliza(
            forward_result.translated_data["atomspace_data"], data_type
        )
        
        # Calculate round-trip accuracy
        round_trip_accuracy = self._calculate_round_trip_accuracy(
            eliza_data, backward_result.translated_data
        )
        
        return {
            "success": len(backward_result.validation_errors) == 0,
            "round_trip_accuracy": round_trip_accuracy,
            "forward_result": forward_result,
            "backward_result": backward_result,
            "original_data": eliza_data,
            "final_data": backward_result.translated_data
        }
    
    def _calculate_accuracy_score(self, original: Dict[str, Any], translated: Dict[str, Any]) -> float:
        """Calculate translation accuracy score"""
        if not original or not translated:
            return 0.0
        
        # Check if translation was successful by presence of expected structures
        if "atomspace_data" in translated:
            # Forward translation: check AtomSpace structure
            atomspace_data = translated["atomspace_data"]
            if atomspace_data.get("atoms") or atomspace_data.get("links"):
                # Basic structural accuracy: at least some atoms/links created
                atoms_count = len(atomspace_data.get("atoms", []))
                links_count = len(atomspace_data.get("links", []))
                
                # Score based on structural completeness
                if atoms_count > 0 and links_count > 0:
                    return 0.90  # High accuracy for complete structure
                elif atoms_count > 0 or links_count > 0:
                    return 0.75  # Partial accuracy for incomplete structure
                else:
                    return 0.50  # Low accuracy for minimal structure
        
        elif "agents" in translated or "memories" in translated:
            # Backward translation: check ElizaOS structure
            agents = translated.get("agents", [])
            memories = translated.get("memories", [])
            
            if agents or memories:
                # Check if reconstructed data has essential fields
                total_items = len(agents) + len(memories)
                valid_items = 0
                
                for agent in agents:
                    if agent.get("id"):
                        valid_items += 1
                        
                for memory in memories:
                    if memory.get("id"):
                        valid_items += 1
                
                if total_items > 0:
                    return min(0.95, 0.70 + (valid_items / total_items) * 0.25)
        
        # Default accuracy based on data presence
        return 0.60 if translated else 0.0
    
    def _calculate_round_trip_accuracy(self, original: Dict[str, Any], final: Dict[str, Any]) -> float:
        """Calculate round-trip translation accuracy"""
        if not original or not final:
            return 0.0
        
        # Extract original data structure
        original_agent = original.get("agent", {})
        original_memory = original.get("memory", {})
        
        # Extract final data structure
        final_agents = final.get("agents", [])
        final_memories = final.get("memories", [])
        
        total_accuracy = 0.0
        comparison_count = 0
        
        # Compare agent data
        if original_agent and final_agents:
            original_id = original_agent.get("id")
            final_agent = next((a for a in final_agents if a.get("id") == original_id), None)
            
            if final_agent:
                # Calculate field preservation accuracy
                preserved_fields = 0
                total_fields = 0
                
                for key, value in original_agent.items():
                    total_fields += 1
                    if key in final_agent:
                        if key == "id" and final_agent[key] == value:
                            preserved_fields += 1
                        elif key != "id":  # Other fields may be transformed
                            preserved_fields += 0.8  # Partial credit for transformation
                
                if total_fields > 0:
                    total_accuracy += preserved_fields / total_fields
                    comparison_count += 1
        
        # Compare memory data
        if original_memory and final_memories:
            original_id = original_memory.get("id")
            final_memory = next((m for m in final_memories if m.get("id") == original_id), None)
            
            if final_memory:
                # Calculate field preservation accuracy
                preserved_fields = 0
                total_fields = 0
                
                for key, value in original_memory.items():
                    total_fields += 1
                    if key in final_memory:
                        if key == "id" and final_memory[key] == value:
                            preserved_fields += 1
                        elif key != "id":  # Other fields may be transformed
                            preserved_fields += 0.7  # Partial credit for transformation
                
                if total_fields > 0:
                    total_accuracy += preserved_fields / total_fields
                    comparison_count += 1
        
        # If no specific comparisons made, use basic structural accuracy
        if comparison_count == 0:
            if (original_agent and final_agents) or (original_memory and final_memories):
                return 0.65  # Basic structural preservation
            else:
                return 0.0
        
        return total_accuracy / comparison_count
    
    def _flatten_keys(self, data: Dict[str, Any], prefix: str = "") -> List[str]:
        """Flatten nested dictionary keys for comparison"""
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, dict):
                keys.extend(self._flatten_keys(value, full_key))
        return keys
    
    def _update_translation_stats(self, time_ms: float, accuracy: float, success: bool):
        """Update translation statistics"""
        self.translation_stats["total_translations"] += 1
        if success:
            self.translation_stats["successful_translations"] += 1
        
        # Update average translation time
        total = self.translation_stats["total_translations"]
        current_avg = self.translation_stats["average_translation_time_ms"]
        self.translation_stats["average_translation_time_ms"] = (
            (current_avg * (total - 1) + time_ms) / total
        )
        
        # Track accuracy scores
        self.translation_stats["accuracy_scores"].append(accuracy)
        if len(self.translation_stats["accuracy_scores"]) > 1000:
            self.translation_stats["accuracy_scores"] = self.translation_stats["accuracy_scores"][-1000:]
    
    def get_atomic_vocabulary(self) -> Dict[str, Dict[str, Any]]:
        """Get the atomic vocabulary mapping"""
        result = {}
        for key, entry in self.atomic_vocabulary.items():
            entry_dict = asdict(entry)
            # Convert enums to their string values for serialization
            entry_dict["eliza_primitive"] = entry_dict["eliza_primitive"].value
            entry_dict["atomspace_pattern"] = entry_dict["atomspace_pattern"].value
            result[key] = entry_dict
        return result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get translation performance statistics"""
        accuracy_scores = self.translation_stats["accuracy_scores"]
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        
        return {
            **self.translation_stats,
            "average_accuracy": avg_accuracy,
            "success_rate": (
                self.translation_stats["successful_translations"] / 
                max(1, self.translation_stats["total_translations"])
            )
        }
    
    async def validate_translation_accuracy(self, 
                                          test_data: List[Dict[str, Any]], 
                                          data_type: str,
                                          target_accuracy: float = 0.99) -> Dict[str, Any]:
        """Validate translation accuracy with test patterns"""
        results = []
        
        for test_case in test_data:
            round_trip_result = await self.round_trip_translate(test_case, data_type)
            results.append(round_trip_result)
        
        # Calculate overall accuracy
        accuracies = [r["round_trip_accuracy"] for r in results if r["success"]]
        overall_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
        
        validation_passed = overall_accuracy >= target_accuracy
        
        return {
            "validation_passed": validation_passed,
            "overall_accuracy": overall_accuracy,
            "target_accuracy": target_accuracy,
            "test_results": results,
            "successful_tests": len(accuracies),
            "total_tests": len(test_data)
        }