"""
ElizaOS Integration Module

Integrates all core ElizaOS features with the existing OpenCog-GnuCash
cognitive-financial intelligence framework.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

from .connectors import ConnectorManager, DiscordConnector, TelegramConnector
from .models import ModelManager, OpenAIProvider, AnthropicProvider, GeminiProvider
from .memory import EnhancedMemoryManager
from .actions import ActionRegistry, ActionExecutor
from .dashboard import WebDashboard

logger = logging.getLogger(__name__)

class ElizaOSFramework:
    """Complete ElizaOS framework integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Core ElizaOS components
        self.connector_manager = ConnectorManager()
        self.model_manager = ModelManager()
        self.memory_manager = EnhancedMemoryManager(
            self.config.get('memory', {})
        )
        self.action_registry = ActionRegistry()
        self.action_executor = ActionExecutor(self.action_registry)
        self.dashboard = WebDashboard(
            self.config.get('dashboard', {'port': 3000})
        )
        
        # Integration with existing cognitive framework
        self.cognitive_framework = None
        
        # Initialization status
        self.is_initialized = False
        self.components_status = {}
    
    async def initialize(self, cognitive_framework=None) -> bool:
        """Initialize the complete ElizaOS framework"""
        try:
            logger.info("🚀 Initializing ElizaOS Framework...")
            
            # Set cognitive framework
            if cognitive_framework:
                self.cognitive_framework = cognitive_framework
                self._integrate_with_cognitive_framework()
            
            # Initialize core components
            await self._initialize_memory_manager()
            await self._initialize_model_providers()
            await self._initialize_connectors()
            await self._initialize_dashboard()
            
            # Setup cross-component integrations
            self._setup_integrations()
            
            self.is_initialized = True
            logger.info("✅ ElizaOS Framework initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ElizaOS Framework: {e}")
            return False
    
    async def _initialize_memory_manager(self) -> bool:
        """Initialize enhanced memory management"""
        try:
            success = await self.memory_manager.initialize()
            self.components_status['memory'] = success
            
            if success:
                logger.info("✅ Enhanced memory manager initialized")
            else:
                logger.error("❌ Failed to initialize memory manager")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Memory manager initialization error: {e}")
            self.components_status['memory'] = False
            return False
    
    async def _initialize_model_providers(self) -> bool:
        """Initialize model providers"""
        try:
            providers_config = self.config.get('models', {})
            success_count = 0
            
            # OpenAI provider
            if providers_config.get('openai', {}).get('enabled', False):
                openai_config = providers_config['openai']
                openai_config['api_key'] = os.getenv('OPENAI_API_KEY', openai_config.get('api_key'))
                
                if openai_config.get('api_key'):
                    openai_provider = OpenAIProvider(openai_config)
                    self.model_manager.add_provider('openai', openai_provider)
                    if await openai_provider.initialize():
                        success_count += 1
            
            # Anthropic provider
            if providers_config.get('anthropic', {}).get('enabled', False):
                anthropic_config = providers_config['anthropic']
                anthropic_config['api_key'] = os.getenv('ANTHROPIC_API_KEY', anthropic_config.get('api_key'))
                
                if anthropic_config.get('api_key'):
                    anthropic_provider = AnthropicProvider(anthropic_config)
                    self.model_manager.add_provider('anthropic', anthropic_provider)
                    if await anthropic_provider.initialize():
                        success_count += 1
            
            # Gemini provider
            if providers_config.get('gemini', {}).get('enabled', False):
                gemini_config = providers_config['gemini']
                gemini_config['api_key'] = os.getenv('GEMINI_API_KEY', gemini_config.get('api_key'))
                
                if gemini_config.get('api_key'):
                    gemini_provider = GeminiProvider(gemini_config)
                    self.model_manager.add_provider('gemini', gemini_provider)
                    if await gemini_provider.initialize():
                        success_count += 1
            
            self.components_status['models'] = success_count > 0
            
            if success_count > 0:
                logger.info(f"✅ Initialized {success_count} model providers")
                
                # Set embedding provider for memory manager
                default_provider = self.model_manager.get_provider()
                if default_provider:
                    self.memory_manager.set_embedding_provider(default_provider)
            else:
                logger.warning("⚠️ No model providers initialized")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Model providers initialization error: {e}")
            self.components_status['models'] = False
            return False
    
    async def _initialize_connectors(self) -> bool:
        """Initialize social platform connectors"""
        try:
            connectors_config = self.config.get('connectors', {})
            success_count = 0
            
            # Discord connector
            if connectors_config.get('discord', {}).get('enabled', False):
                discord_config = connectors_config['discord']
                discord_config['bot_token'] = os.getenv('DISCORD_API_TOKEN', discord_config.get('bot_token'))
                discord_config['application_id'] = os.getenv('DISCORD_APPLICATION_ID', discord_config.get('application_id'))
                
                if discord_config.get('bot_token'):
                    discord_connector = DiscordConnector(discord_config)
                    self.connector_manager.add_connector('discord', discord_connector)
                    if await discord_connector.connect():
                        success_count += 1
            
            # Telegram connector
            if connectors_config.get('telegram', {}).get('enabled', False):
                telegram_config = connectors_config['telegram']
                telegram_config['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN', telegram_config.get('bot_token'))
                
                if telegram_config.get('bot_token'):
                    telegram_connector = TelegramConnector(telegram_config)
                    self.connector_manager.add_connector('telegram', telegram_connector)
                    if await telegram_connector.connect():
                        success_count += 1
            
            self.components_status['connectors'] = success_count > 0
            
            if success_count > 0:
                logger.info(f"✅ Initialized {success_count} social platform connectors")
            else:
                logger.warning("⚠️ No social platform connectors initialized")
            
            return True  # Return True even if no connectors, as this is optional
            
        except Exception as e:
            logger.error(f"❌ Connectors initialization error: {e}")
            self.components_status['connectors'] = False
            return False
    
    async def _initialize_dashboard(self) -> bool:
        """Initialize web dashboard"""
        try:
            success = await self.dashboard.initialize()
            
            if success:
                # Start dashboard server
                await self.dashboard.start()
                self.components_status['dashboard'] = True
                logger.info("✅ Web dashboard initialized and started")
            else:
                self.components_status['dashboard'] = False
                logger.error("❌ Failed to initialize web dashboard")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Dashboard initialization error: {e}")
            self.components_status['dashboard'] = False
            return False
    
    def _integrate_with_cognitive_framework(self):
        """Integrate with existing cognitive-financial framework"""
        try:
            if not self.cognitive_framework:
                return
            
            logger.info("🔗 Integrating with cognitive-financial framework...")
            
            # Set cognitive framework in components
            self.connector_manager.set_cognitive_framework(self.cognitive_framework)
            self.memory_manager.set_cognitive_framework(self.cognitive_framework)
            self.action_registry.set_cognitive_framework(self.cognitive_framework)
            self.dashboard.set_cognitive_framework(self.cognitive_framework)
            
            # Add ElizaOS framework to cognitive framework
            if hasattr(self.cognitive_framework, 'elizaos_framework'):
                self.cognitive_framework.elizaos_framework = self
            
            logger.info("✅ Successfully integrated with cognitive framework")
            
        except Exception as e:
            logger.error(f"❌ Cognitive framework integration error: {e}")
    
    def _setup_integrations(self):
        """Setup cross-component integrations"""
        try:
            # Connect dashboard to other components
            self.dashboard.set_connector_manager(self.connector_manager)
            self.dashboard.set_model_manager(self.model_manager)
            self.dashboard.set_memory_manager(self.memory_manager)
            self.dashboard.set_action_executor(self.action_executor)
            
            # Setup action-connector integration
            if hasattr(self.cognitive_framework, 'connector_manager'):
                self.cognitive_framework.connector_manager = self.connector_manager
            
            logger.info("✅ Cross-component integrations setup complete")
            
        except Exception as e:
            logger.error(f"❌ Integration setup error: {e}")
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message through the complete ElizaOS pipeline"""
        try:
            context = context or {}
            
            # Store message in memory
            if self.memory_manager:
                memory_id = await self.memory_manager.store_memory(
                    content=message,
                    content_type='conversation',
                    source=context.get('source', 'api'),
                    metadata=context
                )
                context['memory_id'] = memory_id
            
            # Route to cognitive framework if available
            if self.cognitive_framework:
                # Determine appropriate agent
                agent_name = self._determine_agent(message, context)
                
                if agent_name and hasattr(self.cognitive_framework, 'cognitive_agents'):
                    agents = self.cognitive_framework.cognitive_agents
                    if agent_name in agents:
                        agent = agents[agent_name]
                        
                        # Add ElizaOS context
                        elizaos_context = {
                            'elizaos_available': True,
                            'connectors': list(self.connector_manager.connectors.keys()),
                            'models': list(self.model_manager.providers.keys()),
                            'memory_enabled': bool(self.memory_manager)
                        }
                        context.update(elizaos_context)
                        
                        # Process with agent
                        result = await agent.process_message(message, context)
                        
                        # Store response in memory
                        if self.memory_manager and result.get('response'):
                            await self.memory_manager.store_memory(
                                content=result['response'],
                                content_type='conversation',
                                source=f'{agent_name}_response',
                                metadata={'original_message_id': memory_id}
                            )
                        
                        return result
            
            # Fallback: use model directly
            if self.model_manager:
                provider = self.model_manager.get_provider()
                if provider:
                    result = await provider.generate_text(
                        message, 
                        context=context,
                        max_tokens=500
                    )
                    
                    return {
                        'response': result.get('text', ''),
                        'source': 'elizaos_direct',
                        'model': result.get('model'),
                        'provider': result.get('provider')
                    }
            
            return {
                'response': 'ElizaOS framework is available but no processing capability is configured.',
                'source': 'elizaos_fallback'
            }
            
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
            return {
                'response': f'Sorry, I encountered an error: {str(e)}',
                'source': 'elizaos_error'
            }
    
    def _determine_agent(self, message: str, context: Dict) -> Optional[str]:
        """Determine which cognitive agent to use"""
        message_lower = message.lower()
        
        # Financial keywords -> financial agents
        financial_keywords = ['money', 'budget', 'spend', 'account', 'balance', 'transaction', 'payment']
        if any(keyword in message_lower for keyword in financial_keywords):
            return 'financial_chat_agent'
        
        # Budget keywords -> budget planning
        budget_keywords = ['budget', 'plan', 'save', 'goal', 'target', 'forecast']
        if any(keyword in message_lower for keyword in budget_keywords):
            return 'budget_planning_agent'
        
        # Analysis keywords -> transaction analysis
        analysis_keywords = ['analyze', 'pattern', 'trend', 'anomaly', 'unusual']
        if any(keyword in message_lower for keyword in analysis_keywords):
            return 'transaction_analysis_agent'
        
        # Default to financial chat agent
        return 'financial_chat_agent'
    
    async def execute_action(self, action_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an action through the action system"""
        if self.action_executor:
            result = await self.action_executor.execute_action(action_name, parameters)
            return result.to_dict()
        
        return {'success': False, 'error': 'Action executor not available'}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'elizaos': {
                'initialized': self.is_initialized,
                'components': self.components_status,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Add component-specific status
        if self.memory_manager:
            status['memory'] = await self.memory_manager.get_memory_statistics()
        
        if self.connector_manager:
            status['connectors'] = {
                name: connector.is_connected
                for name, connector in self.connector_manager.connectors.items()
            }
        
        if self.model_manager:
            status['models'] = {
                name: provider.is_initialized
                for name, provider in self.model_manager.providers.items()
            }
        
        if self.action_executor:
            status['actions'] = self.action_executor.get_execution_statistics()
        
        if self.dashboard:
            status['dashboard'] = {
                'running': self.dashboard.is_running,
                'host': self.dashboard.host,
                'port': self.dashboard.port
            }
        
        return status
    
    async def shutdown(self) -> bool:
        """Shutdown the ElizaOS framework"""
        try:
            logger.info("📴 Shutting down ElizaOS Framework...")
            
            # Stop dashboard
            if self.dashboard:
                await self.dashboard.stop()
            
            # Disconnect connectors
            if self.connector_manager:
                await self.connector_manager.disconnect_all()
            
            # Close memory manager
            if self.memory_manager:
                await self.memory_manager.close()
            
            self.is_initialized = False
            logger.info("✅ ElizaOS Framework shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")
            return False

def create_default_elizaos_config() -> Dict[str, Any]:
    """Create default ElizaOS configuration"""
    return {
        'models': {
            'openai': {
                'enabled': True,
                'model_name': 'gpt-3.5-turbo',
                'api_key': None  # Will be read from environment
            },
            'anthropic': {
                'enabled': False,
                'model_name': 'claude-3-sonnet',
                'api_key': None
            },
            'gemini': {
                'enabled': False,
                'model_name': 'gemini-pro',
                'api_key': None
            }
        },
        'connectors': {
            'discord': {
                'enabled': False,
                'bot_token': None,
                'application_id': None
            },
            'telegram': {
                'enabled': False,
                'bot_token': None
            }
        },
        'memory': {
            'db_path': 'data/elizaos_memory.db',
            'max_memory_items': 10000,
            'retention_days': 365,
            'importance_threshold': 0.5
        },
        'dashboard': {
            'host': '0.0.0.0',
            'port': 3000,
            'debug': False
        }
    }

async def integrate_elizaos_with_cognitive_framework(cognitive_framework, config: Dict[str, Any] = None):
    """Helper function to integrate ElizaOS with existing cognitive framework"""
    try:
        # Use provided config or create default
        elizaos_config = config or create_default_elizaos_config()
        
        # Create ElizaOS framework
        elizaos = ElizaOSFramework(elizaos_config)
        
        # Initialize with cognitive framework
        success = await elizaos.initialize(cognitive_framework)
        
        if success:
            logger.info("🎉 ElizaOS successfully integrated with cognitive framework!")
            
            # Add ElizaOS methods to cognitive framework
            cognitive_framework.elizaos = elizaos
            cognitive_framework.process_elizaos_message = elizaos.process_message
            cognitive_framework.execute_elizaos_action = elizaos.execute_action
            cognitive_framework.get_elizaos_status = elizaos.get_system_status
            
            return elizaos
        else:
            logger.error("❌ Failed to integrate ElizaOS with cognitive framework")
            return None
            
    except Exception as e:
        logger.error(f"❌ ElizaOS integration error: {e}")
        return None