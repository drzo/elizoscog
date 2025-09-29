"""
ElizaOS Action System

Provides an extensible action framework for agents to perform various tasks
including financial operations, data analysis, and system integrations.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
from dataclasses import dataclass
import json
import inspect

logger = logging.getLogger(__name__)

@dataclass
class ActionResult:
    """Result of an action execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'metadata': self.metadata or {},
            'execution_time': self.execution_time
        }

@dataclass
class ActionParameter:
    """Definition of an action parameter"""
    name: str
    type: type
    description: str
    required: bool = True
    default: Any = None
    validation_regex: Optional[str] = None

class BaseAction(ABC):
    """Base class for all actions"""
    
    def __init__(self, name: str, description: str, parameters: List[ActionParameter] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or []
        self.cognitive_framework = None
        self.execution_count = 0
        self.total_execution_time = 0.0
        
    @abstractmethod
    async def execute(self, **kwargs) -> ActionResult:
        """Execute the action with given parameters"""
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """Validate input parameters and return list of errors"""
        errors = []
        
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in params:
                errors.append(f"Required parameter '{param.name}' is missing")
            
            # Type checking
            if param.name in params:
                value = params[param.name]
                if not isinstance(value, param.type) and value is not None:
                    errors.append(f"Parameter '{param.name}' must be of type {param.type.__name__}")
        
        return errors
    
    def set_cognitive_framework(self, framework):
        """Set the cognitive framework for enhanced processing"""
        self.cognitive_framework = framework
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get action execution statistics"""
        avg_time = self.total_execution_time / max(1, self.execution_count)
        return {
            'name': self.name,
            'execution_count': self.execution_count,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': avg_time
        }

class FinancialQueryAction(BaseAction):
    """Action for querying financial data"""
    
    def __init__(self):
        parameters = [
            ActionParameter('query', str, 'Natural language financial query'),
            ActionParameter('account_filter', str, 'Optional account filter', required=False),
            ActionParameter('date_range', dict, 'Optional date range filter', required=False)
        ]
        super().__init__(
            name='financial_query',
            description='Query financial data using natural language',
            parameters=parameters
        )
    
    async def execute(self, **kwargs) -> ActionResult:
        """Execute financial query"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate parameters
            errors = self.validate_parameters(kwargs)
            if errors:
                return ActionResult(
                    success=False,
                    error=f"Parameter validation failed: {', '.join(errors)}"
                )
            
            query = kwargs['query']
            account_filter = kwargs.get('account_filter')
            date_range = kwargs.get('date_range')
            
            logger.info(f"🔍 Executing financial query: {query}")
            
            # Use cognitive framework for enhanced query processing
            if self.cognitive_framework:
                # Route to financial chat agent
                agent = self.cognitive_framework.cognitive_agents.get('financial_chat_agent')
                if agent:
                    context = {
                        'action': 'financial_query',
                        'account_filter': account_filter,
                        'date_range': date_range
                    }
                    
                    result = await agent.process_message(query, context)
                    
                    execution_time = asyncio.get_event_loop().time() - start_time
                    self.execution_count += 1
                    self.total_execution_time += execution_time
                    
                    return ActionResult(
                        success=True,
                        data=result,
                        metadata={'query': query, 'context': context},
                        execution_time=execution_time
                    )
            
            # Fallback implementation
            result = f"[MOCK] Financial query result for: {query}"
            
            execution_time = asyncio.get_event_loop().time() - start_time
            self.execution_count += 1
            self.total_execution_time += execution_time
            
            return ActionResult(
                success=True,
                data=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Financial query action failed: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

class BudgetAnalysisAction(BaseAction):
    """Action for budget analysis and planning"""
    
    def __init__(self):
        parameters = [
            ActionParameter('analysis_type', str, 'Type of analysis: summary, trends, forecast'),
            ActionParameter('time_period', str, 'Time period: monthly, quarterly, yearly', required=False, default='monthly'),
            ActionParameter('categories', list, 'Expense categories to analyze', required=False)
        ]
        super().__init__(
            name='budget_analysis',
            description='Perform budget analysis and generate insights',
            parameters=parameters
        )
    
    async def execute(self, **kwargs) -> ActionResult:
        """Execute budget analysis"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            errors = self.validate_parameters(kwargs)
            if errors:
                return ActionResult(success=False, error=f"Validation failed: {', '.join(errors)}")
            
            analysis_type = kwargs['analysis_type']
            time_period = kwargs.get('time_period', 'monthly')
            categories = kwargs.get('categories', [])
            
            logger.info(f"📊 Executing budget analysis: {analysis_type}")
            
            if self.cognitive_framework:
                agent = self.cognitive_framework.cognitive_agents.get('budget_planning_agent')
                if agent:
                    context = {
                        'action': 'budget_analysis',
                        'analysis_type': analysis_type,
                        'time_period': time_period,
                        'categories': categories
                    }
                    
                    prompt = f"Perform {analysis_type} budget analysis for {time_period} period"
                    if categories:
                        prompt += f" focusing on categories: {', '.join(categories)}"
                    
                    result = await agent.process_message(prompt, context)
                    
                    execution_time = asyncio.get_event_loop().time() - start_time
                    self.execution_count += 1
                    self.total_execution_time += execution_time
                    
                    return ActionResult(
                        success=True,
                        data=result,
                        metadata=context,
                        execution_time=execution_time
                    )
            
            # Mock result
            result = {
                'analysis_type': analysis_type,
                'time_period': time_period,
                'summary': f'Budget analysis for {time_period} period completed',
                'insights': ['Mock insight 1', 'Mock insight 2'],
                'recommendations': ['Mock recommendation 1']
            }
            
            execution_time = asyncio.get_event_loop().time() - start_time
            self.execution_count += 1
            self.total_execution_time += execution_time
            
            return ActionResult(
                success=True,
                data=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Budget analysis action failed: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

class TransactionAnalysisAction(BaseAction):
    """Action for analyzing transaction patterns"""
    
    def __init__(self):
        parameters = [
            ActionParameter('transaction_id', str, 'Specific transaction ID to analyze', required=False),
            ActionParameter('pattern_type', str, 'Pattern type: spending, income, anomaly', required=False, default='spending'),
            ActionParameter('lookback_days', int, 'Number of days to look back', required=False, default=30)
        ]
        super().__init__(
            name='transaction_analysis',
            description='Analyze transaction patterns and detect anomalies',
            parameters=parameters
        )
    
    async def execute(self, **kwargs) -> ActionResult:
        """Execute transaction analysis"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            errors = self.validate_parameters(kwargs)
            if errors:
                return ActionResult(success=False, error=f"Validation failed: {', '.join(errors)}")
            
            transaction_id = kwargs.get('transaction_id')
            pattern_type = kwargs.get('pattern_type', 'spending')
            lookback_days = kwargs.get('lookback_days', 30)
            
            logger.info(f"🔍 Executing transaction analysis: {pattern_type}")
            
            if self.cognitive_framework:
                agent = self.cognitive_framework.cognitive_agents.get('transaction_analysis_agent')
                if agent:
                    context = {
                        'action': 'transaction_analysis',
                        'transaction_id': transaction_id,
                        'pattern_type': pattern_type,
                        'lookback_days': lookback_days
                    }
                    
                    if transaction_id:
                        prompt = f"Analyze transaction {transaction_id}"
                    else:
                        prompt = f"Analyze {pattern_type} patterns over the last {lookback_days} days"
                    
                    result = await agent.process_message(prompt, context)
                    
                    execution_time = asyncio.get_event_loop().time() - start_time
                    self.execution_count += 1
                    self.total_execution_time += execution_time
                    
                    return ActionResult(
                        success=True,
                        data=result,
                        metadata=context,
                        execution_time=execution_time
                    )
            
            # Mock implementation
            result = {
                'pattern_type': pattern_type,
                'lookback_days': lookback_days,
                'patterns_found': 3,
                'anomalies_detected': 1 if pattern_type == 'anomaly' else 0,
                'summary': f'Transaction analysis completed for {pattern_type} patterns'
            }
            
            execution_time = asyncio.get_event_loop().time() - start_time
            self.execution_count += 1
            self.total_execution_time += execution_time
            
            return ActionResult(
                success=True,
                data=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Transaction analysis action failed: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

class SendMessageAction(BaseAction):
    """Action for sending messages through various platforms"""
    
    def __init__(self):
        parameters = [
            ActionParameter('platform', str, 'Platform to send message to: discord, telegram'),
            ActionParameter('channel_id', str, 'Channel or chat ID'),
            ActionParameter('message', str, 'Message content to send'),
            ActionParameter('message_type', str, 'Message type: text, embed, file', required=False, default='text')
        ]
        super().__init__(
            name='send_message',
            description='Send message through social platforms',
            parameters=parameters
        )
    
    async def execute(self, **kwargs) -> ActionResult:
        """Execute send message action"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            errors = self.validate_parameters(kwargs)
            if errors:
                return ActionResult(success=False, error=f"Validation failed: {', '.join(errors)}")
            
            platform = kwargs['platform']
            channel_id = kwargs['channel_id']
            message = kwargs['message']
            message_type = kwargs.get('message_type', 'text')
            
            logger.info(f"📤 Sending message to {platform}:{channel_id}")
            
            # Get connector from cognitive framework
            if self.cognitive_framework and hasattr(self.cognitive_framework, 'connector_manager'):
                connector = self.cognitive_framework.connector_manager.get_connector(platform)
                if connector:
                    success = await connector.send_message(channel_id, message, message_type=message_type)
                    
                    execution_time = asyncio.get_event_loop().time() - start_time
                    self.execution_count += 1
                    self.total_execution_time += execution_time
                    
                    return ActionResult(
                        success=success,
                        data={'message_sent': success, 'platform': platform, 'channel_id': channel_id},
                        metadata={'platform': platform, 'message_type': message_type},
                        execution_time=execution_time
                    )
            
            # Mock implementation
            logger.info(f"[MOCK] Message sent to {platform}:{channel_id}: {message[:50]}...")
            
            execution_time = asyncio.get_event_loop().time() - start_time
            self.execution_count += 1
            self.total_execution_time += execution_time
            
            return ActionResult(
                success=True,
                data={'message_sent': True, 'platform': platform, 'channel_id': channel_id},
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Send message action failed: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

class WebSearchAction(BaseAction):
    """Action for searching the web"""
    
    def __init__(self):
        parameters = [
            ActionParameter('query', str, 'Search query'),
            ActionParameter('max_results', int, 'Maximum number of results', required=False, default=5),
            ActionParameter('site_filter', str, 'Filter to specific site', required=False)
        ]
        super().__init__(
            name='web_search',
            description='Search the web for information',
            parameters=parameters
        )
    
    async def execute(self, **kwargs) -> ActionResult:
        """Execute web search"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            errors = self.validate_parameters(kwargs)
            if errors:
                return ActionResult(success=False, error=f"Validation failed: {', '.join(errors)}")
            
            query = kwargs['query']
            max_results = kwargs.get('max_results', 5)
            site_filter = kwargs.get('site_filter')
            
            logger.info(f"🔍 Searching web for: {query}")
            
            # Mock search results
            results = []
            for i in range(min(max_results, 3)):
                results.append({
                    'title': f'Search result {i+1} for {query}',
                    'url': f'https://example.com/result{i+1}',
                    'snippet': f'This is a mock snippet for result {i+1} about {query}',
                    'relevance_score': 0.9 - (i * 0.1)
                })
            
            execution_time = asyncio.get_event_loop().time() - start_time
            self.execution_count += 1
            self.total_execution_time += execution_time
            
            return ActionResult(
                success=True,
                data={
                    'query': query,
                    'results': results,
                    'total_results': len(results)
                },
                metadata={'site_filter': site_filter},
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Web search action failed: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )

class ActionRegistry:
    """Registry for managing actions"""
    
    def __init__(self):
        self.actions: Dict[str, BaseAction] = {}
        self.action_history: List[Dict[str, Any]] = []
        self.cognitive_framework = None
        
        # Register built-in actions
        self._register_builtin_actions()
    
    def _register_builtin_actions(self):
        """Register built-in actions"""
        builtin_actions = [
            FinancialQueryAction(),
            BudgetAnalysisAction(),
            TransactionAnalysisAction(),
            SendMessageAction(),
            WebSearchAction()
        ]
        
        for action in builtin_actions:
            self.register_action(action)
    
    def register_action(self, action: BaseAction):
        """Register a new action"""
        self.actions[action.name] = action
        if self.cognitive_framework:
            action.set_cognitive_framework(self.cognitive_framework)
        logger.info(f"📝 Registered action: {action.name}")
    
    def unregister_action(self, name: str) -> bool:
        """Unregister an action"""
        if name in self.actions:
            del self.actions[name]
            logger.info(f"🗑️ Unregistered action: {name}")
            return True
        return False
    
    def get_action(self, name: str) -> Optional[BaseAction]:
        """Get an action by name"""
        return self.actions.get(name)
    
    def list_actions(self) -> List[Dict[str, Any]]:
        """List all registered actions"""
        return [
            {
                'name': action.name,
                'description': action.description,
                'parameters': [
                    {
                        'name': param.name,
                        'type': param.type.__name__,
                        'description': param.description,
                        'required': param.required,
                        'default': param.default
                    }
                    for param in action.parameters
                ]
            }
            for action in self.actions.values()
        ]
    
    def set_cognitive_framework(self, framework):
        """Set cognitive framework for all actions"""
        self.cognitive_framework = framework
        for action in self.actions.values():
            action.set_cognitive_framework(framework)
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics for all actions"""
        stats = {}
        for name, action in self.actions.items():
            stats[name] = action.get_statistics()
        return stats

class ActionExecutor:
    """Executes actions with proper error handling and logging"""
    
    def __init__(self, registry: ActionRegistry):
        self.registry = registry
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
    
    async def execute_action(self, action_name: str, parameters: Dict[str, Any] = None) -> ActionResult:
        """Execute an action by name"""
        start_time = datetime.now()
        
        try:
            action = self.registry.get_action(action_name)
            if not action:
                return ActionResult(
                    success=False,
                    error=f"Action '{action_name}' not found"
                )
            
            parameters = parameters or {}
            logger.info(f"⚡ Executing action: {action_name} with params: {parameters}")
            
            # Execute the action
            result = await action.execute(**parameters)
            
            # Log execution
            execution_record = {
                'action_name': action_name,
                'parameters': parameters,
                'result': result.to_dict(),
                'timestamp': start_time.isoformat(),
                'execution_time': result.execution_time
            }
            
            self.execution_history.append(execution_record)
            
            # Maintain history size
            if len(self.execution_history) > self.max_history_size:
                self.execution_history = self.execution_history[-self.max_history_size:]
            
            if result.success:
                logger.info(f"✅ Action {action_name} completed successfully in {result.execution_time:.3f}s")
            else:
                logger.error(f"❌ Action {action_name} failed: {result.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Action execution failed: {e}")
            return ActionResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    async def execute_action_chain(self, actions: List[Dict[str, Any]]) -> List[ActionResult]:
        """Execute a chain of actions"""
        results = []
        
        for action_config in actions:
            action_name = action_config.get('name')
            parameters = action_config.get('parameters', {})
            
            if not action_name:
                results.append(ActionResult(
                    success=False,
                    error="Action name not specified in chain"
                ))
                continue
            
            result = await self.execute_action(action_name, parameters)
            results.append(result)
            
            # Stop chain on failure if configured
            if not result.success and action_config.get('stop_on_failure', False):
                logger.warning(f"Action chain stopped at {action_name} due to failure")
                break
        
        return results
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for record in self.execution_history if record['result']['success'])
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failure_rate': (total_executions - successful_executions) / total_executions,
            'average_execution_time': sum(record['execution_time'] for record in self.execution_history) / total_executions
        }

# Decorator for creating actions from functions
def action(name: str, description: str, parameters: List[ActionParameter] = None):
    """Decorator to create actions from functions"""
    def decorator(func: Callable) -> BaseAction:
        
        class FunctionAction(BaseAction):
            def __init__(self):
                super().__init__(name, description, parameters)
                self.func = func
            
            async def execute(self, **kwargs) -> ActionResult:
                start_time = asyncio.get_event_loop().time()
                
                try:
                    errors = self.validate_parameters(kwargs)
                    if errors:
                        return ActionResult(success=False, error=f"Validation failed: {', '.join(errors)}")
                    
                    # Call the function
                    if inspect.iscoroutinefunction(func):
                        result = await func(**kwargs)
                    else:
                        result = func(**kwargs)
                    
                    execution_time = asyncio.get_event_loop().time() - start_time
                    self.execution_count += 1
                    self.total_execution_time += execution_time
                    
                    return ActionResult(
                        success=True,
                        data=result,
                        execution_time=execution_time
                    )
                    
                except Exception as e:
                    execution_time = asyncio.get_event_loop().time() - start_time
                    return ActionResult(
                        success=False,
                        error=str(e),
                        execution_time=execution_time
                    )
        
        return FunctionAction()
    
    return decorator

# Example usage of the decorator
@action(
    name="calculate_sum",
    description="Calculate sum of two numbers",
    parameters=[
        ActionParameter('a', float, 'First number'),
        ActionParameter('b', float, 'Second number')
    ]
)
async def calculate_sum(a: float, b: float) -> float:
    """Example action function"""
    return a + b