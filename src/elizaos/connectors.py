"""
ElizaOS Social Platform Connectors

Provides Discord, Telegram, and other platform integrations for the
cognitive-financial intelligence framework.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    """Base class for all social platform connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_connected = False
        self.message_handlers = []
        self.cognitive_framework = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the platform"""
        pass
        
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the platform"""
        pass
        
    @abstractmethod
    async def send_message(self, channel_id: str, message: str, **kwargs) -> bool:
        """Send a message to a channel"""
        pass
        
    def add_message_handler(self, handler: Callable):
        """Add a message handler function"""
        self.message_handlers.append(handler)
        
    def set_cognitive_framework(self, framework):
        """Set the cognitive framework for AI processing"""
        self.cognitive_framework = framework

class DiscordConnector(BaseConnector):
    """Discord bot connector for ElizaOS cognitive agents"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self.bot_token = config.get('bot_token')
        self.application_id = config.get('application_id')
        self.guilds = {}
        self.channels = {}
        
    async def connect(self) -> bool:
        """Connect to Discord using bot token"""
        try:
            if not self.bot_token:
                logger.error("Discord bot token not provided")
                return False
                
            logger.info("🤖 Connecting to Discord...")
            
            # Mock Discord connection for now - in real implementation would use discord.py
            self.client = MockDiscordClient(self.bot_token, self)
            await self.client.connect()
            
            self.is_connected = True
            logger.info("✅ Successfully connected to Discord")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Discord: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Discord"""
        try:
            if self.client:
                await self.client.disconnect()
            self.is_connected = False
            logger.info("📴 Disconnected from Discord")
            return True
        except Exception as e:
            logger.error(f"❌ Error disconnecting from Discord: {e}")
            return False
    
    async def send_message(self, channel_id: str, message: str, **kwargs) -> bool:
        """Send message to Discord channel"""
        try:
            if not self.is_connected:
                logger.error("Not connected to Discord")
                return False
                
            # Add cognitive enhancement to messages
            if self.cognitive_framework:
                enhanced_message = await self._enhance_message_with_ai(message, kwargs)
                message = enhanced_message
                
            await self.client.send_message(channel_id, message, **kwargs)
            logger.info(f"📤 Sent Discord message to channel {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send Discord message: {e}")
            return False
    
    async def _enhance_message_with_ai(self, message: str, context: Dict) -> str:
        """Enhance message using cognitive-financial intelligence"""
        try:
            if not self.cognitive_framework:
                return message
                
            # Use the financial chat agent for enhanced responses
            if hasattr(self.cognitive_framework, 'cognitive_agents'):
                chat_agent = self.cognitive_framework.cognitive_agents.get('financial_chat_agent')
                if chat_agent:
                    enhanced = await chat_agent.process_message(message, context)
                    return enhanced.get('response', message)
            
            return message
        except Exception as e:
            logger.error(f"Error enhancing message: {e}")
            return message
    
    async def handle_message(self, message_data: Dict[str, Any]):
        """Handle incoming Discord message"""
        try:
            content = message_data.get('content', '')
            author = message_data.get('author', {})
            channel_id = message_data.get('channel_id', '')
            
            # Skip bot messages
            if author.get('bot', False):
                return
                
            logger.info(f"📥 Received Discord message: {content[:100]}...")
            
            # Process with cognitive framework
            if self.cognitive_framework and content:
                context = {
                    'platform': 'discord',
                    'channel_id': channel_id,
                    'author': author,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Route to appropriate cognitive agent
                response = await self._route_to_cognitive_agent(content, context)
                
                if response:
                    await self.send_message(channel_id, response)
            
            # Call additional handlers
            for handler in self.message_handlers:
                try:
                    await handler(message_data)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling Discord message: {e}")
    
    async def _route_to_cognitive_agent(self, message: str, context: Dict) -> Optional[str]:
        """Route message to appropriate cognitive agent"""
        try:
            if not self.cognitive_framework:
                return None
                
            # Determine intent and route to appropriate agent
            message_lower = message.lower()
            
            # Financial queries go to financial chat agent
            financial_keywords = ['money', 'budget', 'spend', 'account', 'balance', 'transaction']
            if any(keyword in message_lower for keyword in financial_keywords):
                agent = self.cognitive_framework.cognitive_agents.get('financial_chat_agent')
                if agent:
                    result = await agent.process_message(message, context)
                    return result.get('response')
            
            # Budget planning queries
            budget_keywords = ['budget', 'plan', 'save', 'goal', 'target']
            if any(keyword in message_lower for keyword in budget_keywords):
                agent = self.cognitive_framework.cognitive_agents.get('budget_planning_agent')
                if agent:
                    result = await agent.process_message(message, context)
                    return result.get('response')
            
            # Default to general financial chat agent
            agent = self.cognitive_framework.cognitive_agents.get('financial_chat_agent')
            if agent:
                result = await agent.process_message(message, context)
                return result.get('response')
                
        except Exception as e:
            logger.error(f"Error routing to cognitive agent: {e}")
            
        return None

class TelegramConnector(BaseConnector):
    """Telegram bot connector for ElizaOS cognitive agents"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get('bot_token')
        self.webhook_url = config.get('webhook_url')
        
    async def connect(self) -> bool:
        """Connect to Telegram using bot token"""
        try:
            if not self.bot_token:
                logger.error("Telegram bot token not provided")
                return False
                
            logger.info("📱 Connecting to Telegram...")
            
            # Mock Telegram connection for now
            self.client = MockTelegramClient(self.bot_token, self)
            await self.client.connect()
            
            self.is_connected = True
            logger.info("✅ Successfully connected to Telegram")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Telegram: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Telegram"""
        try:
            if hasattr(self, 'client') and self.client:
                await self.client.disconnect()
            self.is_connected = False
            logger.info("📴 Disconnected from Telegram")
            return True
        except Exception as e:
            logger.error(f"❌ Error disconnecting from Telegram: {e}")
            return False
    
    async def send_message(self, chat_id: str, message: str, **kwargs) -> bool:
        """Send message to Telegram chat"""
        try:
            if not self.is_connected:
                logger.error("Not connected to Telegram")
                return False
                
            # Add cognitive enhancement
            if self.cognitive_framework:
                enhanced_message = await self._enhance_message_with_ai(message, kwargs)
                message = enhanced_message
                
            await self.client.send_message(chat_id, message, **kwargs)
            logger.info(f"📤 Sent Telegram message to chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            return False
    
    async def _enhance_message_with_ai(self, message: str, context: Dict) -> str:
        """Enhance message using cognitive-financial intelligence"""
        # Similar to Discord implementation
        try:
            if not self.cognitive_framework:
                return message
                
            if hasattr(self.cognitive_framework, 'cognitive_agents'):
                chat_agent = self.cognitive_framework.cognitive_agents.get('financial_chat_agent')
                if chat_agent:
                    enhanced = await chat_agent.process_message(message, context)
                    return enhanced.get('response', message)
            
            return message
        except Exception as e:
            logger.error(f"Error enhancing Telegram message: {e}")
            return message


# Mock clients for demonstration (in real implementation, would use actual libraries)
class MockDiscordClient:
    """Mock Discord client for demonstration"""
    
    def __init__(self, token: str, connector: DiscordConnector):
        self.token = token
        self.connector = connector
        
    async def connect(self):
        """Mock connection"""
        await asyncio.sleep(0.1)  # Simulate connection delay
        
    async def disconnect(self):
        """Mock disconnection"""
        await asyncio.sleep(0.1)
        
    async def send_message(self, channel_id: str, message: str, **kwargs):
        """Mock send message"""
        logger.info(f"[MOCK] Discord message sent to {channel_id}: {message[:50]}...")

class MockTelegramClient:
    """Mock Telegram client for demonstration"""
    
    def __init__(self, token: str, connector: TelegramConnector):
        self.token = token
        self.connector = connector
        
    async def connect(self):
        """Mock connection"""
        await asyncio.sleep(0.1)
        
    async def disconnect(self):
        """Mock disconnection"""
        await asyncio.sleep(0.1)
        
    async def send_message(self, chat_id: str, message: str, **kwargs):
        """Mock send message"""
        logger.info(f"[MOCK] Telegram message sent to {chat_id}: {message[:50]}...")


class ConnectorManager:
    """Manages multiple social platform connectors"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.cognitive_framework = None
        
    def add_connector(self, name: str, connector: BaseConnector):
        """Add a platform connector"""
        self.connectors[name] = connector
        if self.cognitive_framework:
            connector.set_cognitive_framework(self.cognitive_framework)
            
    def set_cognitive_framework(self, framework):
        """Set cognitive framework for all connectors"""
        self.cognitive_framework = framework
        for connector in self.connectors.values():
            connector.set_cognitive_framework(framework)
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect all configured connectors"""
        results = {}
        for name, connector in self.connectors.items():
            try:
                results[name] = await connector.connect()
            except Exception as e:
                logger.error(f"Failed to connect {name}: {e}")
                results[name] = False
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect all connectors"""
        results = {}
        for name, connector in self.connectors.items():
            try:
                results[name] = await connector.disconnect()
            except Exception as e:
                logger.error(f"Failed to disconnect {name}: {e}")
                results[name] = False
        return results
    
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """Get a specific connector"""
        return self.connectors.get(name)