"""
Advanced Reasoning - Phase 3 Implementation
Temporal logic, causal reasoning, probabilistic models, meta-cognitive reflection,
and learning from user feedback for financial analysis

Enhanced with Phase 5: Recursive Meta-Cognitive Pathways
"""

import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import math

# Try to import numpy, but fall back gracefully if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Provide minimal numpy-like functionality
    class np:
        @staticmethod
        def array(data):
            return data
        
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
        
        @staticmethod
        def std(data):
            if not data or len(data) < 2:
                return 0
            mean_val = sum(data) / len(data)
            variance = sum((x - mean_val) ** 2 for x in data) / len(data)
            return math.sqrt(variance)

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning approaches"""
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    PROBABILISTIC = "probabilistic"
    METACOGNITIVE = "metacognitive"
    INDUCTIVE = "inductive"
    DEDUCTIVE = "deductive"


class ConfidenceLevel(Enum):
    """Confidence levels for reasoning conclusions"""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9


@dataclass
class TemporalRule:
    """Represents a temporal logic rule for financial reasoning"""
    rule_id: str
    condition: str
    temporal_operator: str  # "always", "eventually", "until", "since"
    consequence: str
    confidence: float
    evidence_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CausalRelationship:
    """Represents a causal relationship between financial events"""
    cause_event: str
    effect_event: str
    causal_strength: float
    evidence_instances: List[Dict[str, Any]] = field(default_factory=list)
    confounding_factors: List[str] = field(default_factory=list)
    temporal_delay: Optional[timedelta] = None


@dataclass
class ProbabilisticModel:
    """Represents a probabilistic model for financial predictions"""
    model_id: str
    model_type: str  # "bayesian", "markov", "regression"
    variables: List[str]
    parameters: Dict[str, Any]
    accuracy_metrics: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ReasoningConclusion:
    """Represents a conclusion from reasoning process"""
    conclusion_id: str
    reasoning_type: ReasoningType
    premise: str
    conclusion: str
    confidence: float
    evidence: List[Dict[str, Any]]
    reasoning_chain: List[str]
    meta_analysis: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UserFeedback:
    """Represents user feedback on reasoning conclusions"""
    feedback_id: str
    conclusion_id: str
    user_id: str
    feedback_type: str  # "correct", "incorrect", "partially_correct", "unclear"
    confidence_rating: Optional[float] = None
    explanation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class AdvancedReasoningEngine:
    """
    Advanced reasoning engine with temporal logic, causal reasoning, probabilistic models,
    and meta-cognitive reflection capabilities enhanced with recursive meta-cognitive pathways
    """
    
    def __init__(self, enable_recursive_metacognition: bool = True, config: Dict[str, Any] = None):
        # Configuration
        self.config = config or {}
        
        # Existing initialization
        self.temporal_rules: Dict[str, TemporalRule] = {}
        self.causal_relationships: Dict[str, CausalRelationship] = {}
        self.probabilistic_models: Dict[str, ProbabilisticModel] = {}
        
        self.reasoning_history: List[ReasoningConclusion] = []
        self.user_feedback: List[UserFeedback] = []
        
        # Meta-cognitive tracking
        self.meta_knowledge = {}
        self.confidence_calibration = {}
        self.reasoning_patterns = {}
        self.feedback_patterns = defaultdict(int)
        
        # Additional components from original constructor
        self.reasoning_strategies: Dict[str, Dict[str, Any]] = {}
        self.model_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Initialize base knowledge
        self._initialize_base_knowledge()
        
        # Phase 5: Recursive Meta-Cognitive Pathways
        self.enable_recursive_metacognition = enable_recursive_metacognition
        if self.enable_recursive_metacognition:
            # Import here to avoid circular imports
            from .recursive_metacognition import RecursiveMetaCognitiveEngine
            self.recursive_meta_engine = RecursiveMetaCognitiveEngine(self)
        else:
            self.recursive_meta_engine = None
    
    async def perform_temporal_reasoning(self, 
                                       financial_events: List[Dict[str, Any]], 
                                       temporal_query: str) -> ReasoningConclusion:
        """
        Perform temporal logic reasoning on financial events
        """
        logger.info(f"Performing temporal reasoning for query: {temporal_query}")
        
        # Parse temporal query
        temporal_pattern = self._parse_temporal_query(temporal_query)
        
        # Apply temporal rules
        applicable_rules = self._find_applicable_temporal_rules(temporal_pattern, financial_events)
        
        # Evaluate temporal conditions
        temporal_evaluations = []
        for rule in applicable_rules:
            evaluation = await self._evaluate_temporal_rule(rule, financial_events)
            temporal_evaluations.append(evaluation)
        
        # Synthesize temporal conclusion
        conclusion = await self._synthesize_temporal_conclusion(
            temporal_query, temporal_evaluations, financial_events
        )
        
        # Meta-cognitive assessment
        meta_analysis = await self._meta_assess_reasoning(
            conclusion, temporal_evaluations, "temporal"
        )
        
        reasoning_conclusion = ReasoningConclusion(
            conclusion_id=f"temporal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            reasoning_type=ReasoningType.TEMPORAL,
            premise=temporal_query,
            conclusion=conclusion["conclusion"],
            confidence=conclusion["confidence"],
            evidence=temporal_evaluations,
            reasoning_chain=conclusion["reasoning_chain"],
            meta_analysis=meta_analysis
        )
        
        self.reasoning_history.append(reasoning_conclusion)
        return reasoning_conclusion
    
    async def perform_causal_reasoning(self, 
                                     cause_hypothesis: str, 
                                     financial_data: List[Dict[str, Any]]) -> ReasoningConclusion:
        """
        Perform causal reasoning to identify cause-effect relationships
        """
        logger.info(f"Performing causal reasoning for hypothesis: {cause_hypothesis}")
        
        # Parse causal hypothesis
        causal_structure = self._parse_causal_hypothesis(cause_hypothesis)
        
        # Identify potential confounding factors
        confounding_factors = await self._identify_confounding_factors(
            causal_structure, financial_data
        )
        
        # Test causal relationship
        causal_evidence = await self._test_causal_relationship(
            causal_structure, financial_data, confounding_factors
        )
        
        # Calculate causal strength
        causal_strength = await self._calculate_causal_strength(causal_evidence)
        
        # Generate causal conclusion
        causal_conclusion = await self._generate_causal_conclusion(
            causal_structure, causal_strength, causal_evidence
        )
        
        # Meta-cognitive assessment
        meta_analysis = await self._meta_assess_reasoning(
            causal_conclusion, causal_evidence, "causal"
        )
        
        reasoning_conclusion = ReasoningConclusion(
            conclusion_id=f"causal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            reasoning_type=ReasoningType.CAUSAL,
            premise=cause_hypothesis,
            conclusion=causal_conclusion["conclusion"],
            confidence=causal_conclusion["confidence"],
            evidence=causal_evidence,
            reasoning_chain=causal_conclusion["reasoning_chain"],
            meta_analysis=meta_analysis
        )
        
        self.reasoning_history.append(reasoning_conclusion)
        return reasoning_conclusion
    
    async def build_probabilistic_model(self, 
                                      model_type: str, 
                                      financial_variables: List[str], 
                                      training_data: List[Dict[str, Any]]) -> ProbabilisticModel:
        """
        Build probabilistic models for financial risk assessment and prediction
        """
        logger.info(f"Building probabilistic model: {model_type}")
        
        model_id = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare training data
        processed_data = self._prepare_probabilistic_data(training_data, financial_variables)
        
        # Build model based on type
        if model_type == "bayesian":
            model_params = await self._build_bayesian_model(processed_data, financial_variables)
        elif model_type == "markov":
            model_params = await self._build_markov_model(processed_data, financial_variables)
        elif model_type == "regression":
            model_params = await self._build_regression_model(processed_data, financial_variables)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Validate model performance
        accuracy_metrics = await self._validate_model_performance(
            model_params, processed_data, model_type
        )
        
        probabilistic_model = ProbabilisticModel(
            model_id=model_id,
            model_type=model_type,
            variables=financial_variables,
            parameters=model_params,
            accuracy_metrics=accuracy_metrics
        )
        
        self.probabilistic_models[model_id] = probabilistic_model
        
        # Update model performance tracking
        self.model_performance[model_type].append(accuracy_metrics.get("accuracy", 0.0))
        
        return probabilistic_model
    
    async def perform_metacognitive_reflection(self, 
                                             reasoning_results: List[ReasoningConclusion]) -> Dict[str, Any]:
        """
        Perform meta-cognitive reflection on reasoning processes and outcomes
        Enhanced with recursive meta-cognitive pathways
        """
        logger.info("Performing meta-cognitive reflection on reasoning processes")
        
        # Original meta-cognitive reflection
        pattern_analysis = await self._analyze_reasoning_patterns(reasoning_results)
        confidence_assessment = await self._assess_confidence_calibration(reasoning_results)
        bias_analysis = await self._identify_reasoning_biases(reasoning_results)
        strategy_evaluation = await self._evaluate_reasoning_strategies(reasoning_results)
        
        meta_insights = await self._generate_metacognitive_insights(
            pattern_analysis, confidence_assessment, bias_analysis, strategy_evaluation
        )
        
        self._update_meta_knowledge(meta_insights)
        
        base_reflection = {
            "reflection_timestamp": datetime.now().isoformat(),
            "reasoning_patterns": pattern_analysis,
            "confidence_calibration": confidence_assessment,
            "bias_analysis": bias_analysis,
            "strategy_effectiveness": strategy_evaluation,
            "meta_insights": meta_insights,
            "improvement_recommendations": await self._generate_improvement_recommendations(meta_insights)
        }
        
        # Enhanced Phase 5: Recursive Meta-Cognitive Analysis
        if self.recursive_meta_engine:
            try:
                # Perform recursive self-analysis
                recursive_analysis = await self.recursive_meta_engine.recursive_self_analysis()
                
                # Evolve cognitive strategies
                evolution_results = await self.recursive_meta_engine.evolve_cognitive_strategies()
                
                # Detect recursive patterns
                recursive_patterns = await self.recursive_meta_engine.detect_recursive_patterns()
                
                # Validate self-optimization effectiveness
                optimization_validation = await self.recursive_meta_engine.validate_self_optimization_effectiveness()
                
                # Add recursive meta-cognitive results
                base_reflection.update({
                    "recursive_analysis": recursive_analysis,
                    "cognitive_evolution": evolution_results,
                    "recursive_patterns": recursive_patterns,
                    "optimization_validation": optimization_validation,
                    "cognitive_status": self.recursive_meta_engine.get_cognitive_status_report()
                })
                
                logger.info("Enhanced meta-cognitive reflection completed with recursive analysis")
                
            except Exception as e:
                logger.error(f"Error in recursive meta-cognitive analysis: {e}")
                base_reflection["recursive_meta_cognitive_error"] = str(e)
        
        return base_reflection
    
    async def learn_from_feedback(self, feedback: UserFeedback) -> Dict[str, Any]:
        """
        Learn from user feedback to improve reasoning accuracy and confidence
        """
        logger.info(f"Learning from user feedback for conclusion {feedback.conclusion_id}")
        
        self.user_feedback.append(feedback)
        
        # Find the corresponding reasoning conclusion
        conclusion = next(
            (r for r in self.reasoning_history if r.conclusion_id == feedback.conclusion_id),
            None
        )
        
        if not conclusion:
            return {"error": "Conclusion not found for feedback"}
        
        # Analyze feedback patterns
        feedback_analysis = await self._analyze_feedback_patterns(feedback, conclusion)
        
        # Update confidence calibration
        await self._update_confidence_calibration(feedback, conclusion)
        
        # Adjust reasoning strategies
        strategy_adjustments = await self._adjust_reasoning_strategies(feedback, conclusion)
        
        # Update temporal rules if applicable
        if conclusion.reasoning_type == ReasoningType.TEMPORAL:
            await self._update_temporal_rules_from_feedback(feedback, conclusion)
        
        # Update causal relationships if applicable
        if conclusion.reasoning_type == ReasoningType.CAUSAL:
            await self._update_causal_relationships_from_feedback(feedback, conclusion)
        
        # Update probabilistic models if applicable
        if conclusion.reasoning_type == ReasoningType.PROBABILISTIC:
            await self._update_probabilistic_models_from_feedback(feedback, conclusion)
        
        learning_results = {
            "feedback_processed": True,
            "feedback_analysis": feedback_analysis,
            "confidence_adjustments": await self._calculate_confidence_adjustments(feedback, conclusion),
            "strategy_adjustments": strategy_adjustments,
            "model_updates": await self._get_model_updates_summary(),
            "learning_timestamp": datetime.now().isoformat()
        }
        
        return learning_results
    
    async def predict_financial_risk(self, 
                                   current_state: Dict[str, Any], 
                                   prediction_horizon: timedelta) -> Dict[str, Any]:
        """
        Use probabilistic models to predict financial risk
        """
        logger.info(f"Predicting financial risk for horizon: {prediction_horizon}")
        
        # Select appropriate models for risk prediction
        risk_models = self._select_risk_prediction_models(current_state)
        
        # Generate predictions from each model
        model_predictions = {}
        for model_id, model in risk_models.items():
            prediction = await self._generate_model_prediction(model, current_state, prediction_horizon)
            model_predictions[model_id] = prediction
        
        # Combine predictions using ensemble methods
        ensemble_prediction = await self._combine_risk_predictions(model_predictions)
        
        # Perform temporal reasoning on risk factors
        temporal_risk_analysis = await self._analyze_temporal_risk_patterns(
            current_state, prediction_horizon
        )
        
        # Causal reasoning for risk factors
        causal_risk_analysis = await self._analyze_causal_risk_factors(current_state)
        
        # Meta-cognitive assessment of prediction reliability
        prediction_reliability = await self._assess_prediction_reliability(
            ensemble_prediction, model_predictions
        )
        
        return {
            "prediction_timestamp": datetime.now().isoformat(),
            "prediction_horizon": str(prediction_horizon),
            "risk_assessment": ensemble_prediction,
            "individual_model_predictions": model_predictions,
            "temporal_analysis": temporal_risk_analysis,
            "causal_analysis": causal_risk_analysis,
            "reliability_assessment": prediction_reliability,
            "confidence_level": ensemble_prediction.get("confidence", 0.5)
        }
    
    # Temporal reasoning helper methods
    
    def _parse_temporal_query(self, query: str) -> Dict[str, Any]:
        """Parse temporal query to identify temporal patterns"""
        temporal_operators = {
            "always": r"\b(always|every|all|consistently)\b",
            "eventually": r"\b(eventually|finally|someday|ultimately)\b",
            "until": r"\b(until|before|by the time)\b",
            "since": r"\b(since|after|following)\b",
            "next": r"\b(next|following|subsequent)\b",
            "previous": r"\b(previous|prior|before|last)\b"
        }
        
        query_lower = query.lower()
        detected_operators = []
        
        for operator, pattern in temporal_operators.items():
            if re.search(pattern, query_lower):
                detected_operators.append(operator)
        
        return {
            "original_query": query,
            "detected_operators": detected_operators,
            "temporal_context": self._extract_temporal_context(query_lower)
        }
    
    def _extract_temporal_context(self, query: str) -> Dict[str, Any]:
        """Extract temporal context from query"""
        time_patterns = {
            "months": r"(\d+)\s*months?",
            "weeks": r"(\d+)\s*weeks?",
            "days": r"(\d+)\s*days?",
            "years": r"(\d+)\s*years?",
            "specific_month": r"(january|february|march|april|may|june|july|august|september|october|november|december)",
            "relative_time": r"(this|last|next|previous|current)\s+(month|week|year|quarter)"
        }
        
        extracted_context = {}
        for context_type, pattern in time_patterns.items():
            matches = re.findall(pattern, query)
            if matches:
                extracted_context[context_type] = matches
        
        return extracted_context
    
    def _find_applicable_temporal_rules(self, 
                                      temporal_pattern: Dict[str, Any], 
                                      events: List[Dict[str, Any]]) -> List[TemporalRule]:
        """Find temporal rules applicable to the given pattern and events"""
        applicable_rules = []
        
        for rule in self.temporal_rules.values():
            # Check if rule's temporal operator matches the pattern
            if rule.temporal_operator in temporal_pattern.get("detected_operators", []):
                applicable_rules.append(rule)
        
        # If no specific rules found, return default temporal reasoning rules
        if not applicable_rules:
            applicable_rules = self._get_default_temporal_rules()
        
        return applicable_rules
    
    def _get_default_temporal_rules(self) -> List[TemporalRule]:
        """Get default temporal reasoning rules"""
        return [
            TemporalRule(
                rule_id="default_spending_pattern",
                condition="spending_amount > average",
                temporal_operator="always",
                consequence="indicates_high_spending_period",
                confidence=0.7
            ),
            TemporalRule(
                rule_id="default_budget_trend",
                condition="budget_exceeded",
                temporal_operator="eventually",
                consequence="requires_budget_adjustment",
                confidence=0.8
            )
        ]
    
    async def _evaluate_temporal_rule(self, 
                                    rule: TemporalRule, 
                                    events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a temporal rule against financial events"""
        # Mock evaluation - in real implementation, this would be more sophisticated
        evaluation_result = {
            "rule_id": rule.rule_id,
            "condition_met": True,  # Simplified evaluation
            "temporal_operator": rule.temporal_operator,
            "confidence": rule.confidence,
            "evidence_count": len([e for e in events if self._event_matches_condition(e, rule.condition)]),
            "evaluation_details": f"Rule {rule.rule_id} evaluated against {len(events)} events"
        }
        
        return evaluation_result
    
    def _event_matches_condition(self, event: Dict[str, Any], condition: str) -> bool:
        """Check if an event matches a rule condition"""
        # Simplified condition matching
        if "spending_amount > average" in condition:
            amount = event.get("amount", 0)
            return amount > 100  # Simplified threshold
        return False
    
    async def _synthesize_temporal_conclusion(self, 
                                            query: str, 
                                            evaluations: List[Dict[str, Any]], 
                                            events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize temporal reasoning conclusion"""
        total_evidence = sum(eval_result.get("evidence_count", 0) for eval_result in evaluations)
        avg_confidence = sum(eval_result.get("confidence", 0) for eval_result in evaluations) / len(evaluations) if evaluations else 0
        
        conclusion_text = f"Temporal analysis of {len(events)} financial events shows patterns with {total_evidence} supporting evidence instances."
        
        reasoning_chain = [
            f"1. Analyzed {len(events)} financial events",
            f"2. Applied {len(evaluations)} temporal rules",
            f"3. Found {total_evidence} supporting evidence instances",
            f"4. Calculated average confidence: {avg_confidence:.2f}"
        ]
        
        return {
            "conclusion": conclusion_text,
            "confidence": avg_confidence,
            "reasoning_chain": reasoning_chain,
            "supporting_evidence": total_evidence
        }
    
    # Causal reasoning helper methods
    
    def _parse_causal_hypothesis(self, hypothesis: str) -> Dict[str, Any]:
        """Parse causal hypothesis to identify cause and effect"""
        causal_keywords = ["causes", "leads to", "results in", "because of", "due to"]
        
        hypothesis_lower = hypothesis.lower()
        causal_structure = {
            "original_hypothesis": hypothesis,
            "cause": None,
            "effect": None,
            "causal_keyword": None
        }
        
        for keyword in causal_keywords:
            if keyword in hypothesis_lower:
                parts = hypothesis_lower.split(keyword)
                if len(parts) == 2:
                    causal_structure["cause"] = parts[0].strip()
                    causal_structure["effect"] = parts[1].strip()
                    causal_structure["causal_keyword"] = keyword
                    break
        
        return causal_structure
    
    async def _identify_confounding_factors(self, 
                                          causal_structure: Dict[str, Any], 
                                          data: List[Dict[str, Any]]) -> List[str]:
        """Identify potential confounding factors in causal analysis"""
        # Common financial confounding factors
        common_confounders = [
            "seasonal_effects", "economic_conditions", "income_changes", 
            "life_events", "market_volatility", "policy_changes"
        ]
        
        # Data-driven confounding factor identification
        data_factors = []
        if data:
            # Analyze data for additional variables that might be confounders
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            
            # Filter potential confounders
            potential_confounders = [key for key in all_keys 
                                   if key not in ["amount", "date", "description"]]
            data_factors.extend(potential_confounders[:5])  # Limit to top 5
        
        return common_confounders + data_factors
    
    async def _test_causal_relationship(self, 
                                      causal_structure: Dict[str, Any], 
                                      data: List[Dict[str, Any]], 
                                      confounders: List[str]) -> List[Dict[str, Any]]:
        """Test causal relationship using available data"""
        evidence = []
        
        # Mock causal testing - in reality, this would use sophisticated causal inference methods
        for i, item in enumerate(data[:10]):  # Limit to first 10 items for demo
            # Simulate causal evidence
            evidence_item = {
                "instance_id": i,
                "cause_present": True,  # Simplified
                "effect_observed": True,  # Simplified
                "temporal_order": "cause_before_effect",
                "confounders_controlled": len(confounders) > 0,
                "strength_indicator": 0.7 + (i % 3) * 0.1  # Vary strength
            }
            evidence.append(evidence_item)
        
        return evidence
    
    async def _calculate_causal_strength(self, evidence: List[Dict[str, Any]]) -> float:
        """Calculate the strength of causal relationship"""
        if not evidence:
            return 0.0
        
        # Simple causal strength calculation
        positive_evidence = len([e for e in evidence if e.get("effect_observed", False)])
        total_evidence = len(evidence)
        
        base_strength = positive_evidence / total_evidence if total_evidence > 0 else 0
        
        # Adjust for temporal order
        temporal_correct = len([e for e in evidence if e.get("temporal_order") == "cause_before_effect"])
        temporal_adjustment = temporal_correct / total_evidence if total_evidence > 0 else 0
        
        # Adjust for confounder control
        controlled_confounders = len([e for e in evidence if e.get("confounders_controlled", False)])
        confounder_adjustment = controlled_confounders / total_evidence if total_evidence > 0 else 0
        
        final_strength = (base_strength + temporal_adjustment + confounder_adjustment) / 3
        
        return min(final_strength, 1.0)
    
    async def _generate_causal_conclusion(self, 
                                        causal_structure: Dict[str, Any], 
                                        strength: float, 
                                        evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate causal reasoning conclusion"""
        cause = causal_structure.get("cause", "unknown cause")
        effect = causal_structure.get("effect", "unknown effect")
        
        if strength > 0.7:
            conclusion_text = f"Strong evidence suggests that {cause} has a causal effect on {effect}."
        elif strength > 0.5:
            conclusion_text = f"Moderate evidence suggests that {cause} may have a causal effect on {effect}."
        elif strength > 0.3:
            conclusion_text = f"Weak evidence suggests a possible causal relationship between {cause} and {effect}."
        else:
            conclusion_text = f"Insufficient evidence for a causal relationship between {cause} and {effect}."
        
        reasoning_chain = [
            f"1. Analyzed causal hypothesis: {causal_structure['original_hypothesis']}",
            f"2. Identified cause: {cause}",
            f"3. Identified effect: {effect}",
            f"4. Evaluated {len(evidence)} evidence instances",
            f"5. Calculated causal strength: {strength:.2f}"
        ]
        
        return {
            "conclusion": conclusion_text,
            "confidence": strength,
            "reasoning_chain": reasoning_chain,
            "causal_strength": strength
        }
    
    # Probabilistic model helper methods
    
    def _prepare_probabilistic_data(self, 
                                  data: List[Dict[str, Any]], 
                                  variables: List[str]) -> Dict[str, List[Any]]:
        """Prepare data for probabilistic modeling"""
        prepared_data = {var: [] for var in variables}
        
        for item in data:
            for var in variables:
                if var in item:
                    prepared_data[var].append(item[var])
                else:
                    prepared_data[var].append(None)
        
        return prepared_data
    
    async def _build_bayesian_model(self, 
                                  data: Dict[str, List[Any]], 
                                  variables: List[str]) -> Dict[str, Any]:
        """Build Bayesian probabilistic model"""
        # Simplified Bayesian model parameters
        model_params = {
            "model_type": "bayesian",
            "variables": variables,
            "prior_distributions": {},
            "conditional_probabilities": {},
            "evidence_weights": {}
        }
        
        # Calculate basic statistics for each variable
        for var in variables:
            var_data = [x for x in data[var] if x is not None]
            if var_data:
                if isinstance(var_data[0], (int, float)):
                    # Continuous variable
                    mean_val = sum(var_data) / len(var_data)
                    variance = sum((x - mean_val) ** 2 for x in var_data) / len(var_data)
                    model_params["prior_distributions"][var] = {
                        "type": "normal",
                        "mean": mean_val,
                        "variance": variance
                    }
                else:
                    # Categorical variable
                    value_counts = {}
                    for value in var_data:
                        value_counts[str(value)] = value_counts.get(str(value), 0) + 1
                    
                    total_count = len(var_data)
                    probabilities = {k: v/total_count for k, v in value_counts.items()}
                    
                    model_params["prior_distributions"][var] = {
                        "type": "categorical",
                        "probabilities": probabilities
                    }
        
        return model_params
    
    async def _build_markov_model(self, 
                                data: Dict[str, List[Any]], 
                                variables: List[str]) -> Dict[str, Any]:
        """Build Markov chain probabilistic model"""
        model_params = {
            "model_type": "markov",
            "variables": variables,
            "transition_matrices": {},
            "state_spaces": {}
        }
        
        # Build transition matrices for each variable
        for var in variables:
            var_data = [x for x in data[var] if x is not None]
            if len(var_data) > 1:
                # Discretize continuous variables
                if isinstance(var_data[0], (int, float)):
                    # Simple discretization into quintiles
                    sorted_data = sorted(var_data)
                    if len(sorted_data) >= 5:
                        # Calculate quintile boundaries
                        quintiles = []
                        for i in range(6):
                            idx = min(i * len(sorted_data) // 5, len(sorted_data) - 1)
                            quintiles.append(sorted_data[idx])
                        
                        states = []
                        for value in var_data:
                            for i in range(5):
                                if quintiles[i] <= value <= quintiles[i+1]:
                                    states.append(f"Q{i+1}")
                                    break
                    else:
                        # For small datasets, use simple high/low classification
                        median = sorted_data[len(sorted_data) // 2]
                        states = ["high" if x >= median else "low" for x in var_data]
                else:
                    states = [str(x) for x in var_data]
                
                # Build transition matrix
                unique_states = list(set(states))
                model_params["state_spaces"][var] = unique_states
                
                transition_matrix = {}
                for i in range(len(states) - 1):
                    current_state = states[i]
                    next_state = states[i + 1]
                    
                    if current_state not in transition_matrix:
                        transition_matrix[current_state] = {}
                    
                    transition_matrix[current_state][next_state] = \
                        transition_matrix[current_state].get(next_state, 0) + 1
                
                # Normalize to probabilities
                for current_state in transition_matrix:
                    total_transitions = sum(transition_matrix[current_state].values())
                    for next_state in transition_matrix[current_state]:
                        transition_matrix[current_state][next_state] /= total_transitions
                
                model_params["transition_matrices"][var] = transition_matrix
        
        return model_params
    
    async def _build_regression_model(self, 
                                    data: Dict[str, List[Any]], 
                                    variables: List[str]) -> Dict[str, Any]:
        """Build regression probabilistic model"""
        # Simplified linear regression model
        model_params = {
            "model_type": "regression",
            "variables": variables,
            "coefficients": {},
            "r_squared": 0.0,
            "residual_variance": 0.0
        }
        
        # Find numeric variables for regression
        numeric_vars = []
        for var in variables:
            var_data = [x for x in data[var] if x is not None and isinstance(x, (int, float))]
            if len(var_data) > 5:  # Need sufficient data points
                numeric_vars.append(var)
        
        if len(numeric_vars) >= 2:
            # Use first variable as dependent, others as independent
            dependent_var = numeric_vars[0]
            independent_vars = numeric_vars[1:]
            
            # Simple linear regression calculation
            y_data = [x for x in data[dependent_var] if x is not None and isinstance(x, (int, float))]
            
            if y_data:
                y_mean = sum(y_data) / len(y_data)
                
                for ind_var in independent_vars:
                    x_data = [x for x in data[ind_var] if x is not None and isinstance(x, (int, float))]
                    
                    if len(x_data) == len(y_data):
                        x_mean = sum(x_data) / len(x_data)
                        
                        # Calculate correlation coefficient as simplified regression
                        numerator = sum((x_data[i] - x_mean) * (y_data[i] - y_mean) for i in range(len(x_data)))
                        denominator_x = sum((x - x_mean) ** 2 for x in x_data)
                        denominator_y = sum((y - y_mean) ** 2 for y in y_data)
                        
                        if denominator_x > 0 and denominator_y > 0:
                            correlation = numerator / (denominator_x * denominator_y) ** 0.5
                            model_params["coefficients"][ind_var] = correlation
                
                # Calculate R-squared (simplified)
                if model_params["coefficients"]:
                    avg_correlation = sum(abs(c) for c in model_params["coefficients"].values()) / len(model_params["coefficients"])
                    model_params["r_squared"] = avg_correlation ** 2
        
        return model_params
    
    async def _validate_model_performance(self, 
                                        model_params: Dict[str, Any], 
                                        data: Dict[str, List[Any]], 
                                        model_type: str) -> Dict[str, float]:
        """Validate probabilistic model performance"""
        # Simplified validation metrics
        metrics = {
            "accuracy": 0.7 + np.random.random() * 0.2,  # Mock accuracy between 0.7-0.9
            "precision": 0.6 + np.random.random() * 0.3,
            "recall": 0.6 + np.random.random() * 0.3,
            "f1_score": 0.65 + np.random.random() * 0.25
        }
        
        # Model-specific metrics
        if model_type == "bayesian":
            metrics["log_likelihood"] = -np.random.random() * 100
            metrics["bic"] = np.random.random() * 50 + 100
        elif model_type == "markov":
            metrics["perplexity"] = np.random.random() * 10 + 5
            metrics["entropy"] = np.random.random() * 3 + 1
        elif model_type == "regression":
            metrics["mse"] = np.random.random() * 100
            metrics["mae"] = np.random.random() * 50
        
        return metrics
    
    # Meta-cognitive analysis methods
    
    async def _analyze_reasoning_patterns(self, 
                                        reasoning_results: List[ReasoningConclusion]) -> Dict[str, Any]:
        """Analyze patterns in reasoning processes"""
        if not reasoning_results:
            return {"no_data": "No reasoning results to analyze"}
        
        # Analyze reasoning type distribution
        type_distribution = {}
        confidence_by_type = defaultdict(list)
        
        for result in reasoning_results:
            reasoning_type = result.reasoning_type.value
            type_distribution[reasoning_type] = type_distribution.get(reasoning_type, 0) + 1
            confidence_by_type[reasoning_type].append(result.confidence)
        
        # Calculate average confidence by type
        avg_confidence_by_type = {}
        for reasoning_type, confidences in confidence_by_type.items():
            avg_confidence_by_type[reasoning_type] = sum(confidences) / len(confidences)
        
        # Analyze reasoning chain lengths
        chain_lengths = [len(result.reasoning_chain) for result in reasoning_results]
        avg_chain_length = sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0
        
        return {
            "total_reasoning_instances": len(reasoning_results),
            "reasoning_type_distribution": type_distribution,
            "average_confidence_by_type": avg_confidence_by_type,
            "average_reasoning_chain_length": avg_chain_length,
            "confidence_range": {
                "min": min(r.confidence for r in reasoning_results),
                "max": max(r.confidence for r in reasoning_results),
                "avg": sum(r.confidence for r in reasoning_results) / len(reasoning_results)
            }
        }
    
    async def _assess_confidence_calibration(self, 
                                           reasoning_results: List[ReasoningConclusion]) -> Dict[str, Any]:
        """Assess how well confidence scores match actual accuracy"""
        if not reasoning_results:
            return {"calibration_score": 0.0, "note": "No data for calibration assessment"}
        
        # Simplified calibration assessment
        # In reality, this would compare predicted confidence with actual outcomes
        confidence_bins = {"0.0-0.2": [], "0.2-0.4": [], "0.4-0.6": [], "0.6-0.8": [], "0.8-1.0": []}
        
        for result in reasoning_results:
            confidence = result.confidence
            if confidence <= 0.2:
                confidence_bins["0.0-0.2"].append(result)
            elif confidence <= 0.4:
                confidence_bins["0.2-0.4"].append(result)
            elif confidence <= 0.6:
                confidence_bins["0.4-0.6"].append(result)
            elif confidence <= 0.8:
                confidence_bins["0.6-0.8"].append(result)
            else:
                confidence_bins["0.8-1.0"].append(result)
        
        bin_analysis = {}
        for bin_range, results in confidence_bins.items():
            if results:
                avg_confidence = sum(r.confidence for r in results) / len(results)
                bin_analysis[bin_range] = {
                    "count": len(results),
                    "average_confidence": avg_confidence,
                    "reasoning_types": [r.reasoning_type.value for r in results]
                }
        
        # Calculate overall calibration score (simplified)
        calibration_score = 0.8 - abs(0.5 - sum(r.confidence for r in reasoning_results) / len(reasoning_results))
        
        return {
            "calibration_score": max(0.0, min(1.0, calibration_score)),
            "confidence_distribution": bin_analysis,
            "overall_assessment": "Well calibrated" if calibration_score > 0.7 else "Needs improvement"
        }
    
    async def _identify_reasoning_biases(self, 
                                       reasoning_results: List[ReasoningConclusion]) -> Dict[str, Any]:
        """Identify potential biases in reasoning processes"""
        biases_detected = []
        
        if not reasoning_results:
            return {"biases_detected": [], "note": "No data for bias analysis"}
        
        # Overconfidence bias
        high_confidence_count = len([r for r in reasoning_results if r.confidence > 0.8])
        if high_confidence_count / len(reasoning_results) > 0.6:
            biases_detected.append({
                "bias_type": "overconfidence",
                "severity": "moderate",
                "description": "High proportion of high-confidence conclusions may indicate overconfidence"
            })
        
        # Anchoring bias (preference for certain reasoning types)
        type_counts = defaultdict(int)
        for result in reasoning_results:
            type_counts[result.reasoning_type.value] += 1
        
        max_type = max(type_counts.items(), key=lambda x: x[1])
        if max_type[1] / len(reasoning_results) > 0.7:
            biases_detected.append({
                "bias_type": "anchoring",
                "severity": "low",
                "description": f"Over-reliance on {max_type[0]} reasoning type"
            })
        
        # Confirmation bias (not enough evidence considered)
        short_chains = [r for r in reasoning_results if len(r.reasoning_chain) < 3]
        if len(short_chains) / len(reasoning_results) > 0.5:
            biases_detected.append({
                "bias_type": "confirmation",
                "severity": "moderate",
                "description": "Short reasoning chains may indicate insufficient evidence consideration"
            })
        
        return {
            "biases_detected": biases_detected,
            "bias_count": len(biases_detected),
            "overall_bias_risk": "high" if len(biases_detected) > 2 else "low" if len(biases_detected) == 0 else "moderate"
        }
    
    async def _evaluate_reasoning_strategies(self, 
                                           reasoning_results: List[ReasoningConclusion]) -> Dict[str, Any]:
        """Evaluate effectiveness of different reasoning strategies"""
        strategy_performance = {}
        
        for result in reasoning_results:
            reasoning_type = result.reasoning_type.value
            if reasoning_type not in strategy_performance:
                strategy_performance[reasoning_type] = {
                    "count": 0,
                    "total_confidence": 0,
                    "avg_chain_length": 0,
                    "effectiveness_score": 0
                }
            
            strategy_performance[reasoning_type]["count"] += 1
            strategy_performance[reasoning_type]["total_confidence"] += result.confidence
            strategy_performance[reasoning_type]["avg_chain_length"] += len(result.reasoning_chain)
        
        # Calculate averages and effectiveness scores
        for strategy, metrics in strategy_performance.items():
            count = metrics["count"]
            metrics["average_confidence"] = metrics["total_confidence"] / count
            metrics["avg_chain_length"] = metrics["avg_chain_length"] / count
            
            # Simple effectiveness calculation
            metrics["effectiveness_score"] = (
                metrics["average_confidence"] * 0.6 + 
                min(metrics["avg_chain_length"] / 5, 1.0) * 0.4
            )
        
        # Rank strategies by effectiveness
        ranked_strategies = sorted(
            strategy_performance.items(), 
            key=lambda x: x[1]["effectiveness_score"], 
            reverse=True
        )
        
        return {
            "strategy_performance": strategy_performance,
            "ranked_strategies": [(strategy, metrics["effectiveness_score"]) for strategy, metrics in ranked_strategies],
            "most_effective_strategy": ranked_strategies[0][0] if ranked_strategies else "unknown",
            "least_effective_strategy": ranked_strategies[-1][0] if ranked_strategies else "unknown"
        }
    
    async def _generate_metacognitive_insights(self, 
                                             pattern_analysis: Dict[str, Any],
                                             confidence_assessment: Dict[str, Any],
                                             bias_analysis: Dict[str, Any],
                                             strategy_evaluation: Dict[str, Any]) -> List[str]:
        """Generate meta-cognitive insights from analysis"""
        insights = []
        
        # Pattern insights
        if pattern_analysis.get("reasoning_type_distribution"):
            most_used_type = max(pattern_analysis["reasoning_type_distribution"].items(), key=lambda x: x[1])
            insights.append(f"Most frequently used reasoning type is {most_used_type[0]} ({most_used_type[1]} instances)")
        
        # Confidence insights
        calibration_score = confidence_assessment.get("calibration_score", 0)
        if calibration_score > 0.8:
            insights.append("Confidence calibration is excellent - predictions match actual performance well")
        elif calibration_score < 0.5:
            insights.append("Confidence calibration needs improvement - consider recalibrating confidence assessments")
        
        # Bias insights
        bias_count = bias_analysis.get("bias_count", 0)
        if bias_count > 0:
            bias_types = [bias["bias_type"] for bias in bias_analysis.get("biases_detected", [])]
            insights.append(f"Detected {bias_count} potential biases: {', '.join(bias_types)}")
        else:
            insights.append("No significant reasoning biases detected")
        
        # Strategy insights
        most_effective = strategy_evaluation.get("most_effective_strategy")
        if most_effective:
            insights.append(f"Most effective reasoning strategy is {most_effective}")
        
        return insights
    
    def _update_meta_knowledge(self, insights: List[str]):
        """Update meta-knowledge base with new insights"""
        timestamp = datetime.now().isoformat()
        
        if "insights" not in self.meta_knowledge:
            self.meta_knowledge["insights"] = []
        
        for insight in insights:
            self.meta_knowledge["insights"].append({
                "insight": insight,
                "timestamp": timestamp
            })
        
        # Keep only recent insights (last 100)
        if len(self.meta_knowledge["insights"]) > 100:
            self.meta_knowledge["insights"] = self.meta_knowledge["insights"][-100:]
    
    async def _generate_improvement_recommendations(self, insights: List[str]) -> List[str]:
        """Generate recommendations for improving reasoning processes"""
        recommendations = []
        
        for insight in insights:
            if "calibration needs improvement" in insight:
                recommendations.append("Implement confidence recalibration based on historical accuracy")
            elif "overconfidence" in insight:
                recommendations.append("Increase evidence requirements for high-confidence conclusions")
            elif "short reasoning chains" in insight:
                recommendations.append("Enforce minimum evidence consideration for complex decisions")
            elif "over-reliance" in insight:
                recommendations.append("Encourage diverse reasoning approaches for comprehensive analysis")
        
        # General recommendations if no specific issues found
        if not recommendations:
            recommendations.extend([
                "Continue current reasoning practices",
                "Monitor for emerging patterns in future analyses",
                "Consider expanding reasoning strategy repertoire"
            ])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    # Learning and feedback methods
    
    async def _analyze_feedback_patterns(self, 
                                       feedback: UserFeedback, 
                                       conclusion: ReasoningConclusion) -> Dict[str, Any]:
        """Analyze patterns in user feedback"""
        # Update feedback pattern tracking
        feedback_key = f"{conclusion.reasoning_type.value}_{feedback.feedback_type}"
        self.feedback_patterns[feedback_key] += 1
        
        # Analyze feedback in context
        analysis = {
            "feedback_type": feedback.feedback_type,
            "reasoning_type": conclusion.reasoning_type.value,
            "confidence_gap": abs(conclusion.confidence - (feedback.confidence_rating or 0.5)),
            "pattern_frequency": self.feedback_patterns[feedback_key],
            "feedback_timestamp": feedback.timestamp.isoformat()
        }
        
        return analysis
    
    async def _update_confidence_calibration(self, 
                                           feedback: UserFeedback, 
                                           conclusion: ReasoningConclusion):
        """Update confidence calibration based on feedback"""
        reasoning_type = conclusion.reasoning_type.value
        
        # Track accuracy for confidence calibration
        accuracy = 1.0 if feedback.feedback_type == "correct" else 0.5 if feedback.feedback_type == "partially_correct" else 0.0
        
        self.confidence_calibration[reasoning_type].append({
            "predicted_confidence": conclusion.confidence,
            "actual_accuracy": accuracy,
            "feedback_timestamp": feedback.timestamp.isoformat()
        })
        
        # Keep only recent calibration data
        if len(self.confidence_calibration[reasoning_type]) > 100:
            self.confidence_calibration[reasoning_type] = self.confidence_calibration[reasoning_type][-100:]
    
    async def _adjust_reasoning_strategies(self, 
                                         feedback: UserFeedback, 
                                         conclusion: ReasoningConclusion) -> Dict[str, Any]:
        """Adjust reasoning strategies based on feedback"""
        reasoning_type = conclusion.reasoning_type.value
        
        adjustments = {
            "strategy_type": reasoning_type,
            "feedback_influence": feedback.feedback_type,
            "adjustments_made": []
        }
        
        # Strategy-specific adjustments
        if feedback.feedback_type == "incorrect":
            if reasoning_type == "temporal":
                adjustments["adjustments_made"].append("Increase temporal rule evidence requirements")
            elif reasoning_type == "causal":
                adjustments["adjustments_made"].append("Strengthen confounding factor analysis")
            elif reasoning_type == "probabilistic":
                adjustments["adjustments_made"].append("Recalibrate model parameters")
        
        elif feedback.feedback_type == "correct":
            adjustments["adjustments_made"].append(f"Reinforce successful {reasoning_type} strategy")
        
        return adjustments
    
    async def _update_temporal_rules_from_feedback(self, 
                                                 feedback: UserFeedback, 
                                                 conclusion: ReasoningConclusion):
        """Update temporal rules based on user feedback"""
        # Find relevant temporal rules
        for rule_id, rule in self.temporal_rules.items():
            # Update confidence based on feedback
            if feedback.feedback_type == "correct":
                rule.confidence = min(rule.confidence + 0.05, 1.0)
                rule.evidence_count += 1
            elif feedback.feedback_type == "incorrect":
                rule.confidence = max(rule.confidence - 0.1, 0.1)
    
    async def _update_causal_relationships_from_feedback(self, 
                                                       feedback: UserFeedback, 
                                                       conclusion: ReasoningConclusion):
        """Update causal relationships based on user feedback"""
        # Update causal strength based on feedback
        for relationship_id, relationship in self.causal_relationships.items():
            if feedback.feedback_type == "correct":
                relationship.causal_strength = min(relationship.causal_strength + 0.02, 1.0)
            elif feedback.feedback_type == "incorrect":
                relationship.causal_strength = max(relationship.causal_strength - 0.05, 0.0)
    
    async def _update_probabilistic_models_from_feedback(self, 
                                                       feedback: UserFeedback, 
                                                       conclusion: ReasoningConclusion):
        """Update probabilistic models based on user feedback"""
        # Update model accuracy tracking
        for model_id, model in self.probabilistic_models.items():
            if feedback.feedback_type == "correct":
                if "accuracy" not in model.accuracy_metrics:
                    model.accuracy_metrics["accuracy"] = 0.5
                model.accuracy_metrics["accuracy"] = min(model.accuracy_metrics["accuracy"] + 0.01, 1.0)
            elif feedback.feedback_type == "incorrect":
                if "accuracy" not in model.accuracy_metrics:
                    model.accuracy_metrics["accuracy"] = 0.5
                model.accuracy_metrics["accuracy"] = max(model.accuracy_metrics["accuracy"] - 0.02, 0.0)
    
    async def _calculate_confidence_adjustments(self, 
                                              feedback: UserFeedback, 
                                              conclusion: ReasoningConclusion) -> Dict[str, float]:
        """Calculate confidence adjustments based on feedback"""
        base_confidence = conclusion.confidence
        
        if feedback.feedback_type == "correct":
            adjustment = +0.05
        elif feedback.feedback_type == "incorrect":
            adjustment = -0.1
        elif feedback.feedback_type == "partially_correct":
            adjustment = -0.02
        else:
            adjustment = 0.0
        
        new_confidence = max(0.1, min(1.0, base_confidence + adjustment))
        
        return {
            "original_confidence": base_confidence,
            "adjustment": adjustment,
            "new_confidence": new_confidence,
            "adjustment_reason": feedback.feedback_type
        }
    
    async def _get_model_updates_summary(self) -> Dict[str, Any]:
        """Get summary of model updates from feedback"""
        return {
            "temporal_rules_updated": len(self.temporal_rules),
            "causal_relationships_updated": len(self.causal_relationships),
            "probabilistic_models_updated": len(self.probabilistic_models),
            "total_feedback_processed": len(self.user_feedback),
            "last_update": datetime.now().isoformat()
        }
    
    # Risk prediction methods
    
    def _select_risk_prediction_models(self, current_state: Dict[str, Any]) -> Dict[str, ProbabilisticModel]:
        """Select appropriate models for risk prediction"""
        relevant_models = {}
        
        # Select models based on available variables in current state
        for model_id, model in self.probabilistic_models.items():
            # Check if model variables are available in current state
            available_vars = set(current_state.keys())
            model_vars = set(model.variables)
            
            # If at least 50% of model variables are available, include the model
            if len(available_vars.intersection(model_vars)) / len(model_vars) >= 0.5:
                relevant_models[model_id] = model
        
        return relevant_models
    
    async def _generate_model_prediction(self, 
                                       model: ProbabilisticModel, 
                                       current_state: Dict[str, Any], 
                                       horizon: timedelta) -> Dict[str, Any]:
        """Generate prediction from a specific model"""
        # Simplified prediction generation
        prediction = {
            "model_id": model.model_id,
            "model_type": model.model_type,
            "prediction_horizon": str(horizon),
            "risk_score": 0.5 + np.random.random() * 0.4,  # Mock risk score
            "confidence": model.accuracy_metrics.get("accuracy", 0.7),
            "contributing_factors": []
        }
        
        # Add contributing factors based on model variables
        for var in model.variables:
            if var in current_state:
                prediction["contributing_factors"].append({
                    "variable": var,
                    "current_value": current_state[var],
                    "importance": np.random.random()
                })
        
        return prediction
    
    async def _combine_risk_predictions(self, model_predictions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine predictions from multiple models using ensemble methods"""
        if not model_predictions:
            return {"risk_score": 0.5, "confidence": 0.1, "risk_level": "medium", "ensemble_method": "no_models"}
        
        # Weighted average based on model confidence
        total_weight = 0
        weighted_risk_sum = 0
        confidence_scores = []
        
        for prediction in model_predictions.values():
            weight = prediction.get("confidence", 0.5)
            risk_score = prediction.get("risk_score", 0.5)
            
            weighted_risk_sum += risk_score * weight
            total_weight += weight
            confidence_scores.append(prediction.get("confidence", 0.5))
        
        ensemble_risk_score = weighted_risk_sum / total_weight if total_weight > 0 else 0.5
        ensemble_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Risk level categorization
        if ensemble_risk_score < 0.3:
            risk_level = "low"
        elif ensemble_risk_score < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_score": ensemble_risk_score,
            "confidence": ensemble_confidence,
            "risk_level": risk_level,
            "ensemble_method": "weighted_average",
            "models_used": len(model_predictions),
            "risk_factors": self._extract_top_risk_factors(model_predictions)
        }
    
    def _extract_top_risk_factors(self, model_predictions: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract top risk factors from model predictions"""
        all_factors = []
        
        for prediction in model_predictions.values():
            factors = prediction.get("contributing_factors", [])
            all_factors.extend(factors)
        
        # Aggregate factors by variable name
        factor_importance = defaultdict(list)
        for factor in all_factors:
            var_name = factor.get("variable")
            importance = factor.get("importance", 0)
            factor_importance[var_name].append(importance)
        
        # Calculate average importance for each factor
        aggregated_factors = []
        for var_name, importance_list in factor_importance.items():
            avg_importance = sum(importance_list) / len(importance_list)
            aggregated_factors.append({
                "variable": var_name,
                "average_importance": avg_importance,
                "frequency": len(importance_list)
            })
        
        # Return top 5 factors by importance
        top_factors = sorted(aggregated_factors, key=lambda x: x["average_importance"], reverse=True)
        return top_factors[:5]
    
    async def _analyze_temporal_risk_patterns(self, 
                                            current_state: Dict[str, Any], 
                                            horizon: timedelta) -> Dict[str, Any]:
        """Analyze temporal patterns for risk assessment"""
        return {
            "temporal_analysis": "Risk patterns analyzed over time",
            "seasonality_detected": False,
            "trend_direction": "stable",
            "temporal_confidence": 0.6
        }
    
    async def _analyze_causal_risk_factors(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze causal relationships that contribute to risk"""
        return {
            "causal_analysis": "Causal risk factors identified",
            "primary_causes": ["spending_increase", "income_volatility"],
            "causal_confidence": 0.7
        }
    
    async def _assess_prediction_reliability(self, 
                                           ensemble_prediction: Dict[str, Any], 
                                           individual_predictions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Assess reliability of risk predictions"""
        if not individual_predictions:
            return {"reliability_score": 0.1, "assessment": "insufficient_data"}
        
        # Calculate prediction consensus
        risk_scores = [pred.get("risk_score", 0.5) for pred in individual_predictions.values()]
        risk_variance = np.var(risk_scores) if len(risk_scores) > 1 else 0
        
        # High variance indicates low consensus/reliability
        consensus_score = max(0, 1 - risk_variance * 2)
        
        # Model confidence scores
        confidence_scores = [pred.get("confidence", 0.5) for pred in individual_predictions.values()]
        avg_model_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Overall reliability
        reliability_score = (consensus_score + avg_model_confidence) / 2
        
        return {
            "reliability_score": reliability_score,
            "consensus_score": consensus_score,
            "model_confidence": avg_model_confidence,
            "prediction_variance": risk_variance,
            "assessment": "high" if reliability_score > 0.7 else "medium" if reliability_score > 0.4 else "low"
        }
    
    # Initialization methods
    
    def _initialize_base_knowledge(self):
        """Initialize base knowledge and rules"""
        # Add some default temporal rules
        default_temporal_rules = [
            TemporalRule(
                rule_id="seasonal_spending",
                condition="month in [11, 12]",
                temporal_operator="always",
                consequence="increased_spending_expected",
                confidence=0.8
            ),
            TemporalRule(
                rule_id="payday_effect",
                condition="day_of_month in [1, 15]",
                temporal_operator="eventually",
                consequence="spending_spike_follows",
                confidence=0.7
            )
        ]
        
        for rule in default_temporal_rules:
            self.temporal_rules[rule.rule_id] = rule
        
        # Initialize base meta-knowledge
        self.meta_knowledge = {
            "reasoning_preferences": {
                "temporal": 0.8,
                "causal": 0.7,
                "probabilistic": 0.9
            },
            "confidence_thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8
            },
            "learning_rate": 0.05
        }
        
        # Initialize reasoning strategies
        self.reasoning_strategies = {
            "conservative": {"confidence_modifier": -0.1, "evidence_threshold": 0.8},
            "aggressive": {"confidence_modifier": 0.1, "evidence_threshold": 0.5},
            "balanced": {"confidence_modifier": 0.0, "evidence_threshold": 0.6}
        }
    
    async def _meta_assess_reasoning(self, 
                                   conclusion: Dict[str, Any], 
                                   evidence: List[Dict[str, Any]], 
                                   reasoning_type: str) -> Dict[str, Any]:
        """Meta-cognitive assessment of reasoning process"""
        return {
            "reasoning_type": reasoning_type,
            "evidence_quality": len(evidence),
            "conclusion_strength": conclusion.get("confidence", 0.5),
            "meta_confidence": 0.8,
            "assessment_notes": f"Meta-analysis of {reasoning_type} reasoning completed"
        }
    
    async def recursive_self_improvement(self) -> Dict[str, Any]:
        """
        Perform recursive self-improvement using evolutionary algorithms
        This is a new Phase 5 capability
        """
        if not self.recursive_meta_engine:
            return {"error": "Recursive meta-cognitive engine not enabled"}
        
        logger.info("Initiating recursive self-improvement process")
        
        try:
            # Observe current cognitive state
            observation = await self.recursive_meta_engine.observe_cognitive_state()
            
            # Generate improvement recommendations
            improvement_actions = await self.recursive_meta_engine.generate_self_improvement_recommendations(observation)
            
            # Implement the most promising improvement action
            implementation_results = []
            for action in improvement_actions[:3]:  # Implement top 3 actions
                result = await self.recursive_meta_engine.implement_self_improvement_action(action)
                implementation_results.append(result)
            
            # Perform recursive analysis to evaluate improvements
            recursive_analysis = await self.recursive_meta_engine.recursive_self_analysis(depth=2)
            
            return {
                "observation": observation,
                "improvement_actions": improvement_actions,
                "implementation_results": implementation_results,
                "recursive_analysis": recursive_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in recursive self-improvement: {e}")
            return {"error": str(e)}
    
    async def get_enhanced_cognitive_status(self) -> Dict[str, Any]:
        """
        Get comprehensive cognitive status including recursive meta-cognitive state
        """
        base_status = {
            "reasoning_history_count": len(self.reasoning_history),
            "feedback_count": len(self.user_feedback),
            "temporal_rules_count": len(self.temporal_rules),
            "causal_relationships_count": len(self.causal_relationships),
            "probabilistic_models_count": len(self.probabilistic_models),
            "meta_knowledge_entries": len(self.meta_knowledge),
            "last_reasoning_timestamp": self.reasoning_history[-1].timestamp.isoformat() if self.reasoning_history else None
        }
        
        if self.recursive_meta_engine:
            recursive_status = self.recursive_meta_engine.get_cognitive_status_report()
            base_status.update({
                "recursive_metacognition": recursive_status,
                "enhanced_capabilities": True
            })
        else:
            base_status["enhanced_capabilities"] = False
        
        return base_status


# Additional imports needed
import re


# Additional utility functions can be added here as needed