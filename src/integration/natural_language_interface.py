"""
Natural Language Interface - Phase 3 Implementation
Advanced conversational interface for financial queries with intent recognition,
report generation, and context-aware dialogue management
"""

import re
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
from difflib import get_close_matches

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of financial intents that can be recognized"""
    QUERY_SPENDING = "query_spending"
    QUERY_BUDGET = "query_budget"
    QUERY_TRENDS = "query_trends"
    QUERY_PREDICTIONS = "query_predictions"
    QUERY_ANOMALIES = "query_anomalies"
    REQUEST_REPORT = "request_report"
    REQUEST_ADVICE = "request_advice"
    SET_BUDGET = "set_budget"
    CREATE_ALERT = "create_alert"
    GENERAL_HELP = "general_help"
    UNKNOWN = "unknown"


class EntityType(Enum):
    """Types of entities that can be extracted from user input"""
    AMOUNT = "amount"
    CATEGORY = "category"
    TIME_PERIOD = "time_period"
    ACCOUNT = "account"
    MERCHANT = "merchant"
    COMPARISON = "comparison"
    THRESHOLD = "threshold"


@dataclass
class ExtractedEntity:
    """Represents an extracted entity from user input"""
    entity_type: EntityType
    value: Any
    confidence: float
    start_position: int
    end_position: int
    normalized_value: Any = None


@dataclass
class RecognizedIntent:
    """Represents a recognized user intent"""
    intent_type: IntentType
    confidence: float
    entities: List[ExtractedEntity]
    parameters: Dict[str, Any] = field(default_factory=dict)
    context_clues: List[str] = field(default_factory=list)


@dataclass
class ConversationContext:
    """Maintains conversation context and history"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    current_topic: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    last_query_time: datetime = field(default_factory=datetime.now)
    follow_up_suggestions: List[str] = field(default_factory=list)


class NaturalLanguageInterface:
    """
    Advanced natural language interface for financial queries and commands
    Supports intent recognition, entity extraction, context-aware dialogue,
    and natural language report generation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Intent recognition patterns
        self.intent_patterns = self._initialize_intent_patterns()
        
        # Entity extraction patterns
        self.entity_patterns = self._initialize_entity_patterns()
        
        # Financial vocabulary
        self.financial_terms = self._load_financial_vocabulary()
        
        # Context management
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        # Response templates
        self.response_templates = self._initialize_response_templates()
        
        # Report generators
        self.report_generators = {
            "spending_summary": self._generate_spending_summary,
            "budget_analysis": self._generate_budget_analysis,
            "trend_report": self._generate_trend_report,
            "prediction_report": self._generate_prediction_report,
            "anomaly_report": self._generate_anomaly_report
        }
    
    async def process_user_input(self, 
                               user_input: str, 
                               user_id: str, 
                               session_id: str = None,
                               context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process natural language user input and return structured response
        """
        session_id = session_id or f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Processing user input for user {user_id}, session {session_id}")
        
        # Get or create conversation context
        context = self._get_conversation_context(user_id, session_id)
        
        # Preprocess input
        preprocessed_input = self._preprocess_input(user_input)
        
        # Intent recognition
        recognized_intent = await self._recognize_intent(preprocessed_input, context)
        
        # Entity extraction
        entities = await self._extract_entities(preprocessed_input, recognized_intent)
        recognized_intent.entities = entities
        
        # Context-aware processing
        enhanced_intent = await self._enhance_with_context(recognized_intent, context, context_data)
        
        # Generate response
        response = await self._generate_response(enhanced_intent, context)
        
        # Update conversation context
        self._update_context(context, user_input, recognized_intent, response)
        
        return {
            "session_id": session_id,
            "recognized_intent": {
                "type": enhanced_intent.intent_type.value,
                "confidence": enhanced_intent.confidence,
                "entities": [self._entity_to_dict(e) for e in enhanced_intent.entities],
                "parameters": enhanced_intent.parameters
            },
            "response": response,
            "context": {
                "current_topic": context.current_topic,
                "follow_up_suggestions": context.follow_up_suggestions
            },
            "processing_metadata": {
                "timestamp": datetime.now().isoformat(),
                "preprocessed_input": preprocessed_input
            }
        }
    
    async def generate_natural_language_report(self, 
                                             report_type: str, 
                                             data: Dict[str, Any],
                                             format_preferences: Dict[str, Any] = None) -> str:
        """
        Generate natural language reports from financial data
        """
        logger.info(f"Generating natural language report: {report_type}")
        
        format_prefs = format_preferences or {}
        
        if report_type in self.report_generators:
            generator = self.report_generators[report_type]
            return await generator(data, format_prefs)
        else:
            return await self._generate_generic_report(report_type, data, format_prefs)
    
    async def recognize_financial_intent(self, text: str) -> RecognizedIntent:
        """
        Recognize financial intent from natural language text
        """
        preprocessed = self._preprocess_input(text)
        return await self._recognize_intent(preprocessed, None)
    
    async def extract_financial_entities(self, text: str) -> List[ExtractedEntity]:
        """
        Extract financial entities from natural language text
        """
        preprocessed = self._preprocess_input(text)
        return await self._extract_entities(preprocessed, None)
    
    def get_conversation_suggestions(self, 
                                   user_id: str, 
                                   session_id: str = None) -> List[str]:
        """
        Get contextual conversation suggestions for the user
        """
        context = self.active_contexts.get(f"{user_id}_{session_id}")
        if context:
            return context.follow_up_suggestions
        
        # Default suggestions for new conversations
        return [
            "How much did I spend on groceries this month?",
            "Show me my spending trends",
            "What are my biggest expenses?",
            "Am I over budget in any category?",
            "Generate a monthly spending report"
        ]
    
    # Intent recognition methods
    
    def _initialize_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Initialize intent recognition patterns"""
        return {
            IntentType.QUERY_SPENDING: [
                r"how much.*spend.*(?:on|for)?\s*(.+?)(?:\s+(?:this|last|in))?",
                r"what.*(?:spend|spent).*(?:on|for)?\s*(.+?)",
                r"total.*spending.*(?:on|for)?\s*(.+?)",
                r"expenses.*(?:on|for)?\s*(.+?)",
                r"(?:money|amount).*spent.*(?:on|for)?\s*(.+?)"
            ],
            IntentType.QUERY_BUDGET: [
                r"budget.*(?:for)?\s*(.+?)",
                r"am i.*(?:over|under).*budget",
                r"budget.*status",
                r"how.*budget.*(?:doing|performing)",
                r"remaining.*budget"
            ],
            IntentType.QUERY_TRENDS: [
                r"trend.*(?:in|for)?\s*(.+?)",
                r"spending.*trend",
                r"pattern.*(?:in|for)?\s*(.+?)",
                r"how.*spending.*chang",
                r"(?:increase|decrease).*spending"
            ],
            IntentType.QUERY_PREDICTIONS: [
                r"predict.*(?:spending|expenses)",
                r"forecast.*(?:spending|expenses)",
                r"what.*expect.*(?:spend|cost)",
                r"future.*(?:spending|expenses)",
                r"will.*spend"
            ],
            IntentType.QUERY_ANOMALIES: [
                r"unusual.*(?:spending|transaction)",
                r"anomal.*(?:spending|transaction)",
                r"strange.*(?:spending|transaction)",
                r"unexpected.*(?:spending|transaction)",
                r"outlier.*(?:spending|transaction)"
            ],
            IntentType.REQUEST_REPORT: [
                r"generate.*report",
                r"create.*report",
                r"show.*report",
                r"(?:monthly|weekly|yearly).*(?:report|summary)",
                r"financial.*(?:report|summary)"
            ],
            IntentType.REQUEST_ADVICE: [
                r"advice.*(?:on|about)?\s*(.+?)",
                r"recommend.*(?:for)?\s*(.+?)",
                r"suggest.*(?:for)?\s*(.+?)",
                r"what.*should.*do.*(?:about)?\s*(.+?)",
                r"help.*(?:with)?\s*(.+?)"
            ],
            IntentType.SET_BUDGET: [
                r"set.*budget.*(?:for)?\s*(.+?)",
                r"create.*budget.*(?:for)?\s*(.+?)",
                r"budget.*(?:for)?\s*(.+?).*(?:is|should be).*(\d+)",
                r"limit.*spending.*(?:on|for)?\s*(.+?)"
            ],
            IntentType.CREATE_ALERT: [
                r"alert.*(?:when|if).*(.+?)",
                r"notify.*(?:when|if).*(.+?)",
                r"warn.*(?:when|if).*(.+?)",
                r"remind.*(?:when|if).*(.+?)"
            ],
            IntentType.GENERAL_HELP: [
                r"help",
                r"what.*(?:can|do).*(?:you|this)",
                r"how.*(?:use|work)",
                r"commands?",
                r"options?"
            ]
        }
    
    def _initialize_entity_patterns(self) -> Dict[EntityType, List[str]]:
        """Initialize entity extraction patterns"""
        return {
            EntityType.AMOUNT: [
                r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:\.\d{2})?)\s*dollars?',
                r'(\d+(?:\.\d{2})?)\s*bucks?'
            ],
            EntityType.CATEGORY: [
                r'(?:on|for)\s+(groceries?|food|dining|restaurants?)',
                r'(?:on|for)\s+(gas|fuel|gasoline)',
                r'(?:on|for)\s+(utilities?|electric|water|internet)',
                r'(?:on|for)\s+(entertainment|movies?|games?)',
                r'(?:on|for)\s+(shopping|clothes|clothing)',
                r'(?:on|for)\s+(healthcare|medical|doctor)',
                r'(?:on|for)\s+(transportation|uber|lyft|taxi)'
            ],
            EntityType.TIME_PERIOD: [
                r'(this|last|past)\s+(month|week|year|quarter)',
                r'(today|yesterday|tomorrow)',
                r'(\d{1,2}\/\d{1,2}\/\d{4})',
                r'(january|february|march|april|may|june|july|august|september|october|november|december)',
                r'(\d{4})',
                r'(last|past)\s+(\d+)\s+(days?|weeks?|months?|years?)'
            ],
            EntityType.ACCOUNT: [
                r'(?:in|from)\s+(checking|savings|credit card?)',
                r'(?:account|acct)\s*(\w+)',
                r'(main|primary|secondary)\s+account'
            ],
            EntityType.MERCHANT: [
                r'(?:at|from)\s+([A-Za-z0-9\s]+?)(?:\s+(?:store|shop|restaurant|cafe))?',
                r'(?:store|shop|restaurant|cafe)\s+([A-Za-z0-9\s]+?)'
            ],
            EntityType.COMPARISON: [
                r'(more|less|higher|lower|above|below|over|under)\s+than',
                r'(compared?\s+to|versus|vs\.?)',
                r'(increase|decrease|change)\s+(?:from|since)'
            ],
            EntityType.THRESHOLD: [
                r'(?:above|over|more than|exceeds?)\s+\$?(\d+(?:\.\d{2})?)',
                r'(?:below|under|less than)\s+\$?(\d+(?:\.\d{2})?)',
                r'limit\s+(?:of|is)?\s*\$?(\d+(?:\.\d{2})?)'
            ]
        }
    
    def _load_financial_vocabulary(self) -> Dict[str, List[str]]:
        """Load financial vocabulary for better recognition"""
        return {
            "spending_synonyms": ["spending", "expenses", "costs", "outgoing", "payments", "charges"],
            "income_synonyms": ["income", "earnings", "salary", "wages", "revenue", "deposits"],
            "categories": ["groceries", "gas", "dining", "entertainment", "utilities", "healthcare", 
                          "shopping", "transportation", "insurance", "education", "savings"],
            "time_modifiers": ["daily", "weekly", "monthly", "yearly", "annual", "quarterly"],
            "comparison_words": ["more", "less", "higher", "lower", "increase", "decrease", "change"],
            "action_words": ["show", "display", "calculate", "analyze", "predict", "forecast", "compare"]
        }
    
    async def _recognize_intent(self, text: str, context: Optional[ConversationContext]) -> RecognizedIntent:
        """Recognize intent from preprocessed text"""
        text_lower = text.lower()
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        context_clues = []
        
        # Check each intent pattern
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Calculate confidence based on pattern specificity and context
                    pattern_confidence = 0.8  # Base confidence for pattern match
                    
                    # Boost confidence if context supports this intent
                    if context and self._context_supports_intent(context, intent_type):
                        pattern_confidence += 0.1
                        context_clues.append("context_support")
                    
                    # Boost confidence for more specific patterns
                    if len(match.groups()) > 0:
                        pattern_confidence += 0.05
                        context_clues.append("entity_extraction")
                    
                    if pattern_confidence > best_confidence:
                        best_confidence = pattern_confidence
                        best_intent = intent_type
        
        # Fallback: keyword-based intent recognition
        if best_confidence < 0.5:
            keyword_intent, keyword_confidence = self._keyword_based_intent(text_lower)
            if keyword_confidence > best_confidence:
                best_intent = keyword_intent
                best_confidence = keyword_confidence
                context_clues.append("keyword_matching")
        
        return RecognizedIntent(
            intent_type=best_intent,
            confidence=best_confidence,
            entities=[],  # Will be filled by entity extraction
            context_clues=context_clues
        )
    
    def _keyword_based_intent(self, text: str) -> Tuple[IntentType, float]:
        """Fallback keyword-based intent recognition"""
        intent_keywords = {
            IntentType.QUERY_SPENDING: ["spend", "spent", "expense", "cost", "paid", "purchase"],
            IntentType.QUERY_BUDGET: ["budget", "limit", "allowance", "allocation"],
            IntentType.QUERY_TRENDS: ["trend", "pattern", "change", "increase", "decrease"],
            IntentType.QUERY_PREDICTIONS: ["predict", "forecast", "future", "expect", "estimate"],
            IntentType.QUERY_ANOMALIES: ["unusual", "strange", "unexpected", "anomaly", "outlier"],
            IntentType.REQUEST_REPORT: ["report", "summary", "overview", "statement"],
            IntentType.REQUEST_ADVICE: ["advice", "recommend", "suggest", "help", "guidance"],
            IntentType.SET_BUDGET: ["set", "create", "establish", "define"],
            IntentType.CREATE_ALERT: ["alert", "notify", "remind", "warn"]
        }
        
        best_intent = IntentType.UNKNOWN
        best_score = 0.0
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            normalized_score = score / len(keywords)
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_intent = intent
        
        return best_intent, min(best_score * 0.6, 0.8)  # Cap at 0.8 for keyword matching
    
    async def _extract_entities(self, text: str, intent: Optional[RecognizedIntent]) -> List[ExtractedEntity]:
        """Extract entities from text based on patterns and context"""
        entities = []
        text_lower = text.lower()
        
        # Extract entities based on patterns
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    entity_value = match.group(1) if match.groups() else match.group(0)
                    
                    # Normalize entity value
                    normalized_value = self._normalize_entity_value(entity_type, entity_value)
                    
                    entities.append(ExtractedEntity(
                        entity_type=entity_type,
                        value=entity_value,
                        confidence=0.8,
                        start_position=match.start(),
                        end_position=match.end(),
                        normalized_value=normalized_value
                    ))
        
        # Intent-specific entity extraction
        if intent and intent.intent_type != IntentType.UNKNOWN:
            intent_entities = await self._extract_intent_specific_entities(text, intent.intent_type)
            entities.extend(intent_entities)
        
        # Remove duplicates and overlapping entities
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _normalize_entity_value(self, entity_type: EntityType, value: str) -> Any:
        """Normalize extracted entity values"""
        if entity_type == EntityType.AMOUNT:
            # Clean and convert to float
            cleaned = re.sub(r'[,$]', '', value)
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
                
        elif entity_type == EntityType.TIME_PERIOD:
            # Normalize time periods
            value_lower = value.lower()
            if "month" in value_lower:
                if "this" in value_lower:
                    return "current_month"
                elif "last" in value_lower:
                    return "last_month"
                else:
                    return "month"
            elif "week" in value_lower:
                if "this" in value_lower:
                    return "current_week"
                elif "last" in value_lower:
                    return "last_week"
                else:
                    return "week"
            return value_lower
            
        elif entity_type == EntityType.CATEGORY:
            # Normalize category names
            category_mappings = {
                "groceries": "groceries", "food": "groceries", "grocery": "groceries",
                "gas": "gas", "fuel": "gas", "gasoline": "gas",
                "dining": "dining", "restaurant": "dining", "restaurants": "dining",
                "entertainment": "entertainment", "movies": "entertainment", "games": "entertainment",
                "utilities": "utilities", "electric": "utilities", "water": "utilities",
                "shopping": "shopping", "clothes": "shopping", "clothing": "shopping"
            }
            return category_mappings.get(value.lower(), value.lower())
            
        return value
    
    async def _extract_intent_specific_entities(self, text: str, intent_type: IntentType) -> List[ExtractedEntity]:
        """Extract entities specific to the recognized intent"""
        entities = []
        
        if intent_type == IntentType.QUERY_SPENDING:
            # Look for implicit categories in spending queries
            category_hints = ["groceries", "gas", "dining", "entertainment", "utilities"]
            for hint in category_hints:
                if hint in text.lower():
                    entities.append(ExtractedEntity(
                        entity_type=EntityType.CATEGORY,
                        value=hint,
                        confidence=0.7,
                        start_position=text.lower().find(hint),
                        end_position=text.lower().find(hint) + len(hint),
                        normalized_value=hint
                    ))
                    
        elif intent_type == IntentType.SET_BUDGET:
            # Look for budget amounts
            amount_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
            matches = re.finditer(amount_pattern, text)
            for match in matches:
                entities.append(ExtractedEntity(
                    entity_type=EntityType.AMOUNT,
                    value=match.group(1),
                    confidence=0.8,
                    start_position=match.start(),
                    end_position=match.end(),
                    normalized_value=float(re.sub(r'[,$]', '', match.group(1)))
                ))
        
        return entities
    
    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate and overlapping entities"""
        if not entities:
            return entities
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e.start_position)
        
        deduplicated = []
        for entity in sorted_entities:
            # Check for overlap with existing entities
            overlap = False
            for existing in deduplicated:
                if (entity.start_position < existing.end_position and 
                    entity.end_position > existing.start_position):
                    # Keep entity with higher confidence
                    if entity.confidence > existing.confidence:
                        deduplicated.remove(existing)
                        deduplicated.append(entity)
                    overlap = True
                    break
            
            if not overlap:
                deduplicated.append(entity)
        
        return deduplicated
    
    # Context management methods
    
    def _get_conversation_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Get or create conversation context"""
        context_key = f"{user_id}_{session_id}"
        
        if context_key not in self.active_contexts:
            self.active_contexts[context_key] = ConversationContext(
                user_id=user_id,
                session_id=session_id
            )
        
        return self.active_contexts[context_key]
    
    def _context_supports_intent(self, context: ConversationContext, intent_type: IntentType) -> bool:
        """Check if conversation context supports the recognized intent"""
        if not context.conversation_history:
            return False
        
        recent_intents = [entry.get("intent", {}).get("type") for entry in context.conversation_history[-3:]]
        
        # Context patterns that support specific intents
        supporting_patterns = {
            IntentType.QUERY_SPENDING: [IntentType.QUERY_BUDGET.value, IntentType.QUERY_TRENDS.value],
            IntentType.QUERY_BUDGET: [IntentType.QUERY_SPENDING.value, IntentType.SET_BUDGET.value],
            IntentType.QUERY_TRENDS: [IntentType.QUERY_SPENDING.value, IntentType.QUERY_PREDICTIONS.value],
            IntentType.REQUEST_ADVICE: [IntentType.QUERY_ANOMALIES.value, IntentType.QUERY_BUDGET.value]
        }
        
        supported_by = supporting_patterns.get(intent_type, [])
        return any(intent in supported_by for intent in recent_intents)
    
    async def _enhance_with_context(self, 
                                  intent: RecognizedIntent, 
                                  context: ConversationContext,
                                  context_data: Optional[Dict[str, Any]]) -> RecognizedIntent:
        """Enhance intent with conversation context and external data"""
        
        # Fill in missing entities from context
        if not any(e.entity_type == EntityType.TIME_PERIOD for e in intent.entities):
            # Default to current month if no time period specified
            intent.entities.append(ExtractedEntity(
                entity_type=EntityType.TIME_PERIOD,
                value="this month",
                confidence=0.5,
                start_position=-1,
                end_position=-1,
                normalized_value="current_month"
            ))
        
        # Add context-based parameters
        if context.current_topic:
            intent.parameters["context_topic"] = context.current_topic
        
        if context_data:
            intent.parameters["external_context"] = context_data
        
        # Enhance based on conversation history
        if context.conversation_history:
            last_interaction = context.conversation_history[-1]
            if last_interaction.get("intent", {}).get("type") == intent.intent_type.value:
                intent.parameters["follow_up"] = True
        
        return intent
    
    def _update_context(self, 
                       context: ConversationContext, 
                       user_input: str, 
                       intent: RecognizedIntent, 
                       response: Dict[str, Any]):
        """Update conversation context with new interaction"""
        
        # Add to conversation history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent": {
                "type": intent.intent_type.value,
                "confidence": intent.confidence
            },
            "response_type": response.get("type", "unknown")
        }
        
        context.conversation_history.append(interaction)
        
        # Keep only last 10 interactions
        if len(context.conversation_history) > 10:
            context.conversation_history = context.conversation_history[-10:]
        
        # Update current topic
        if intent.intent_type != IntentType.UNKNOWN:
            context.current_topic = intent.intent_type.value
        
        # Generate follow-up suggestions
        context.follow_up_suggestions = self._generate_follow_up_suggestions(intent)
        
        context.last_query_time = datetime.now()
    
    def _generate_follow_up_suggestions(self, intent: RecognizedIntent) -> List[str]:
        """Generate contextual follow-up suggestions"""
        suggestions_map = {
            IntentType.QUERY_SPENDING: [
                "Show me spending trends for this category",
                "Compare this to last month",
                "Set a budget limit for this category"
            ],
            IntentType.QUERY_BUDGET: [
                "Show detailed spending breakdown",
                "Get budget optimization advice",
                "Set up alerts for budget overruns"
            ],
            IntentType.QUERY_TRENDS: [
                "Predict future spending patterns",
                "Identify causes of spending changes",
                "Get recommendations to improve trends"
            ],
            IntentType.REQUEST_REPORT: [
                "Generate report for different time period",
                "Export report to email",
                "Schedule regular reports"
            ]
        }
        
        return suggestions_map.get(intent.intent_type, [
            "Ask about spending in specific categories",
            "Check budget status",
            "View spending trends"
        ])
    
    # Response generation methods
    
    def _initialize_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize response templates for different intents"""
        return {
            IntentType.QUERY_SPENDING.value: {
                "with_data": "You spent ${amount:.2f} on {category} {time_period}. {additional_info}",
                "no_data": "I couldn't find any spending data for {category} {time_period}. {suggestion}",
                "error": "I'm having trouble accessing your spending data right now. Please try again."
            },
            IntentType.QUERY_BUDGET.value: {
                "with_data": "Your {category} budget is ${budget:.2f}. You've spent ${spent:.2f} ({percentage:.1f}%). {status}",
                "no_data": "You haven't set a budget for {category} yet. Would you like me to help you create one?",
                "error": "I couldn't retrieve your budget information at the moment."
            },
            IntentType.GENERAL_HELP.value: {
                "default": "I can help you with financial queries, budget tracking, spending analysis, and more. Try asking: 'How much did I spend on groceries this month?' or 'Show me my budget status'."
            }
        }
    
    async def _generate_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate natural language response based on intent and context"""
        
        # Route to appropriate response generator
        if intent.intent_type == IntentType.QUERY_SPENDING:
            return await self._generate_spending_response(intent, context)
        elif intent.intent_type == IntentType.QUERY_BUDGET:
            return await self._generate_budget_response(intent, context)
        elif intent.intent_type == IntentType.QUERY_TRENDS:
            return await self._generate_trends_response(intent, context)
        elif intent.intent_type == IntentType.REQUEST_REPORT:
            return await self._generate_report_response(intent, context)
        elif intent.intent_type == IntentType.REQUEST_ADVICE:
            return await self._generate_advice_response(intent, context)
        elif intent.intent_type == IntentType.GENERAL_HELP:
            return await self._generate_help_response(intent, context)
        else:
            return await self._generate_fallback_response(intent, context)
    
    async def _generate_spending_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate response for spending queries"""
        # Extract parameters from entities
        category = None
        time_period = "this month"
        amount = None
        
        for entity in intent.entities:
            if entity.entity_type == EntityType.CATEGORY:
                category = entity.normalized_value
            elif entity.entity_type == EntityType.TIME_PERIOD:
                time_period = entity.normalized_value
            elif entity.entity_type == EntityType.AMOUNT:
                amount = entity.normalized_value
        
        # Mock spending data lookup (in real implementation, this would query actual data)
        mock_spending_data = {
            "groceries": {"current_month": 450.75, "last_month": 420.30},
            "gas": {"current_month": 120.50, "last_month": 135.20},
            "dining": {"current_month": 280.25, "last_month": 195.80}
        }
        
        category_key = category or "total"
        period_key = self._normalize_time_period_for_lookup(time_period)
        
        if category and category in mock_spending_data:
            spent_amount = mock_spending_data[category].get(period_key, 0)
            
            # Generate contextual additional information
            additional_info = ""
            if period_key == "current_month" and "last_month" in mock_spending_data[category]:
                last_month_amount = mock_spending_data[category]["last_month"]
                if spent_amount > last_month_amount:
                    difference = spent_amount - last_month_amount
                    additional_info = f"That's ${difference:.2f} more than last month."
                elif spent_amount < last_month_amount:
                    difference = last_month_amount - spent_amount
                    additional_info = f"That's ${difference:.2f} less than last month."
            
            response_text = f"You spent ${spent_amount:.2f} on {category} {time_period}. {additional_info}"
            
            return {
                "type": "spending_query_response",
                "text": response_text.strip(),
                "data": {
                    "category": category,
                    "time_period": time_period,
                    "amount": spent_amount,
                    "comparison": additional_info
                },
                "confidence": intent.confidence
            }
        else:
            return {
                "type": "spending_query_response",
                "text": f"I couldn't find spending data for {category or 'that category'} {time_period}. You might want to check if you have transactions in that category.",
                "data": None,
                "confidence": intent.confidence
            }
    
    async def _generate_budget_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate response for budget queries"""
        return {
            "type": "budget_query_response",
            "text": "Budget analysis functionality is available. You can ask about specific category budgets or overall budget status.",
            "data": {"message": "Budget feature ready"},
            "confidence": intent.confidence
        }
    
    async def _generate_trends_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate response for trend queries"""
        return {
            "type": "trends_query_response",
            "text": "I can analyze your spending trends over time. Try asking about trends in specific categories like 'Show me my grocery spending trends'.",
            "data": {"message": "Trends analysis ready"},
            "confidence": intent.confidence
        }
    
    async def _generate_report_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate response for report requests"""
        return {
            "type": "report_request_response",
            "text": "I can generate various financial reports for you. What type of report would you like? Monthly summary, spending breakdown, or budget analysis?",
            "data": {"available_reports": ["monthly_summary", "spending_breakdown", "budget_analysis"]},
            "confidence": intent.confidence
        }
    
    async def _generate_advice_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate response for advice requests"""
        return {
            "type": "advice_request_response",
            "text": "I can provide financial advice based on your spending patterns and goals. What specific area would you like advice on?",
            "data": {"advice_areas": ["budgeting", "saving", "spending_optimization", "debt_management"]},
            "confidence": intent.confidence
        }
    
    async def _generate_help_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate response for help requests"""
        help_text = """I can help you with:
• Spending queries: "How much did I spend on groceries this month?"
• Budget tracking: "Am I over budget on dining?"
• Trend analysis: "Show me my spending trends"
• Report generation: "Generate a monthly spending report"
• Financial advice: "Give me advice on reducing expenses"

Just ask me in natural language!"""
        
        return {
            "type": "help_response",
            "text": help_text,
            "data": {"capabilities": ["spending_queries", "budget_tracking", "trend_analysis", "reports", "advice"]},
            "confidence": 1.0
        }
    
    async def _generate_fallback_response(self, intent: RecognizedIntent, context: ConversationContext) -> Dict[str, Any]:
        """Generate fallback response for unrecognized intents"""
        fallback_text = "I'm not sure I understood that correctly. Could you try rephrasing your question? For example, you could ask about your spending, budget status, or request a financial report."
        
        return {
            "type": "fallback_response",
            "text": fallback_text,
            "data": {"suggestions": context.follow_up_suggestions or self.get_conversation_suggestions(context.user_id, context.session_id)},
            "confidence": 0.1
        }
    
    # Report generation methods
    
    async def _generate_spending_summary(self, data: Dict[str, Any], format_prefs: Dict[str, Any]) -> str:
        """Generate natural language spending summary"""
        total_spending = data.get("total_spending", 0)
        time_period = data.get("time_period", "this month")
        categories = data.get("categories", {})
        
        summary = f"Here's your spending summary for {time_period}:\n\n"
        summary += f"Total spending: ${total_spending:.2f}\n\n"
        
        if categories:
            summary += "Breakdown by category:\n"
            for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                summary += f"• {category.title()}: ${amount:.2f} ({percentage:.1f}%)\n"
        
        return summary
    
    async def _generate_budget_analysis(self, data: Dict[str, Any], format_prefs: Dict[str, Any]) -> str:
        """Generate natural language budget analysis"""
        budget_items = data.get("budget_items", [])
        
        analysis = "Budget Analysis:\n\n"
        
        over_budget_items = []
        under_budget_items = []
        
        for item in budget_items:
            category = item.get("category", "Unknown")
            budgeted = item.get("budgeted", 0)
            spent = item.get("spent", 0)
            percentage = (spent / budgeted * 100) if budgeted > 0 else 0
            
            status_text = f"• {category.title()}: ${spent:.2f} / ${budgeted:.2f} ({percentage:.1f}%)"
            
            if percentage > 100:
                over_budget_items.append(status_text + " - OVER BUDGET")
            elif percentage > 80:
                analysis += status_text + " - Close to limit\n"
            else:
                under_budget_items.append(status_text + " - On track\n")
        
        if over_budget_items:
            analysis += "\n⚠️ Over budget categories:\n"
            analysis += "\n".join(over_budget_items) + "\n"
        
        if under_budget_items:
            analysis += "\n✅ On track categories:\n"
            analysis += "".join(under_budget_items)
        
        return analysis
    
    async def _generate_trend_report(self, data: Dict[str, Any], format_prefs: Dict[str, Any]) -> str:
        """Generate natural language trend report"""
        trends = data.get("trends", [])
        
        report = "Spending Trends Analysis:\n\n"
        
        for trend in trends:
            category = trend.get("category", "Unknown")
            direction = trend.get("direction", "stable")
            percentage_change = trend.get("percentage_change", 0)
            
            if direction == "increasing":
                report += f"📈 {category.title()}: Increased by {percentage_change:.1f}%\n"
            elif direction == "decreasing":
                report += f"📉 {category.title()}: Decreased by {abs(percentage_change):.1f}%\n"
            else:
                report += f"➡️ {category.title()}: Stable spending pattern\n"
        
        return report
    
    async def _generate_prediction_report(self, data: Dict[str, Any], format_prefs: Dict[str, Any]) -> str:
        """Generate natural language prediction report"""
        predictions = data.get("predictions", [])
        
        report = "Spending Predictions:\n\n"
        
        for prediction in predictions:
            category = prediction.get("category", "Unknown")
            predicted_amount = prediction.get("predicted_amount", 0)
            confidence = prediction.get("confidence", 0)
            
            report += f"• {category.title()}: ${predicted_amount:.2f} (confidence: {confidence*100:.0f}%)\n"
        
        return report
    
    async def _generate_anomaly_report(self, data: Dict[str, Any], format_prefs: Dict[str, Any]) -> str:
        """Generate natural language anomaly report"""
        anomalies = data.get("anomalies", [])
        
        if not anomalies:
            return "No unusual spending patterns detected. Your spending appears to be consistent with your typical patterns."
        
        report = f"Detected {len(anomalies)} unusual spending pattern(s):\n\n"
        
        for anomaly in anomalies:
            transaction = anomaly.get("transaction", {})
            reason = anomaly.get("reason", "Unknown reason")
            severity = anomaly.get("severity", "medium")
            
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
            
            amount = transaction.get("amount", 0)
            description = transaction.get("description", "Unknown transaction")
            
            report += f"{severity_emoji} ${amount:.2f} - {description}\n"
            report += f"   Reason: {reason}\n\n"
        
        return report
    
    async def _generate_generic_report(self, report_type: str, data: Dict[str, Any], format_prefs: Dict[str, Any]) -> str:
        """Generate generic natural language report"""
        return f"Report '{report_type}' has been generated with the provided data. This is a generic report format."
    
    # Utility methods
    
    def _preprocess_input(self, text: str) -> str:
        """Preprocess user input for better recognition"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Expand contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "i'm": "i am", "i've": "i have", "i'll": "i will",
            "what's": "what is", "how's": "how is", "where's": "where is"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        # Normalize currency symbols
        text = re.sub(r'\$(\d)', r'dollar \1', text)
        
        # Normalize time expressions
        text = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', r'\1/\2/\3', text)
        
        return text
    
    def _normalize_time_period_for_lookup(self, time_period: str) -> str:
        """Normalize time period for data lookup"""
        period_mappings = {
            "current_month": "current_month",
            "this month": "current_month",
            "last_month": "last_month",
            "previous month": "last_month",
            "current_week": "current_week",
            "this week": "current_week",
            "last_week": "last_week",
            "month": "current_month",
            "week": "current_week"
        }
        
        return period_mappings.get(time_period.lower(), "current_month")
    
    def _entity_to_dict(self, entity: ExtractedEntity) -> Dict[str, Any]:
        """Convert ExtractedEntity to dictionary"""
        return {
            "type": entity.entity_type.value,
            "value": entity.value,
            "normalized_value": entity.normalized_value,
            "confidence": entity.confidence,
            "position": [entity.start_position, entity.end_position]
        }