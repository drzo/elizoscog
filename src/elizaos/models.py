"""
ElizaOS Multi-Model Support

Provides support for multiple LLM providers including OpenAI, Anthropic, 
Google Gemini, and others, integrated with the cognitive-financial framework.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ModelProvider(ABC):
    """Base class for all model providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.model_name = config.get('model_name', 'default')
        self.is_initialized = False
        self.rate_limiter = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the model provider"""
        pass
        
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text from prompt"""
        pass
        
    @abstractmethod
    async def generate_chat_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response from message history"""
        pass
        
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate text embedding"""
        pass
    
    def _prepare_context_with_financial_data(self, prompt: str, context: Dict = None) -> str:
        """Enhance prompt with financial context from cognitive framework"""
        if not context:
            context = {}
            
        # Add financial intelligence context
        financial_context = context.get('financial_context', {})
        if financial_context:
            enhanced_prompt = f"""
You are a cognitive financial intelligence assistant with access to real financial data and reasoning capabilities.

Financial Context:
- Current Account Balance: {financial_context.get('balance', 'Not available')}
- Recent Transactions: {financial_context.get('recent_transactions', 'Not available')}
- Budget Status: {financial_context.get('budget_status', 'Not available')}
- Financial Goals: {financial_context.get('goals', 'Not available')}

User Query: {prompt}

Please provide a helpful, accurate response that considers the financial context and uses cognitive reasoning to provide insights and recommendations.
"""
            return enhanced_prompt
        
        return prompt

class OpenAIProvider(ModelProvider):
    """OpenAI model provider (GPT-3.5, GPT-4, etc.)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.organization = config.get('organization')
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            if not self.api_key:
                logger.error("OpenAI API key not provided")
                return False
                
            # Mock OpenAI client initialization
            self.client = MockOpenAIClient(self.api_key, self.config)
            self.is_initialized = True
            logger.info(f"✅ OpenAI provider initialized with model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI provider: {e}")
            return False
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using OpenAI"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            # Enhance prompt with financial context
            enhanced_prompt = self._prepare_context_with_financial_data(
                prompt, kwargs.get('context', {})
            )
            
            # Generate response
            response = await self.client.generate_completion(
                prompt=enhanced_prompt,
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'text': response['text'],
                'model': self.model_name,
                'provider': 'openai',
                'usage': response.get('usage', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI text generation failed: {e}")
            return {'error': str(e)}
    
    async def generate_chat_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response using OpenAI"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            # Add system message with financial context if available
            context = kwargs.get('context', {})
            enhanced_messages = messages.copy()
            
            if context.get('financial_context'):
                system_message = {
                    "role": "system",
                    "content": f"You are a cognitive financial intelligence assistant. {json.dumps(context['financial_context'])}"
                }
                enhanced_messages.insert(0, system_message)
            
            response = await self.client.generate_chat_completion(
                messages=enhanced_messages,
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'message': response['message'],
                'model': self.model_name,
                'provider': 'openai',
                'usage': response.get('usage', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI chat generation failed: {e}")
            return {'error': str(e)}
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            embedding = await self.client.generate_embedding(text)
            return embedding
            
        except Exception as e:
            logger.error(f"❌ OpenAI embedding generation failed: {e}")
            return []

class AnthropicProvider(ModelProvider):
    """Anthropic Claude model provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.anthropic.com')
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize Anthropic client"""
        try:
            if not self.api_key:
                logger.error("Anthropic API key not provided")
                return False
                
            self.client = MockAnthropicClient(self.api_key, self.config)
            self.is_initialized = True
            logger.info(f"✅ Anthropic provider initialized with model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic provider: {e}")
            return False
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using Anthropic Claude"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            enhanced_prompt = self._prepare_context_with_financial_data(
                prompt, kwargs.get('context', {})
            )
            
            response = await self.client.generate_completion(
                prompt=enhanced_prompt,
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'text': response['text'],
                'model': self.model_name,
                'provider': 'anthropic',
                'usage': response.get('usage', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic text generation failed: {e}")
            return {'error': str(e)}
    
    async def generate_chat_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response using Anthropic Claude"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            # Convert messages to Anthropic format
            anthropic_messages = self._convert_to_anthropic_format(messages, kwargs.get('context', {}))
            
            response = await self.client.generate_chat_completion(
                messages=anthropic_messages,
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'message': response['message'],
                'model': self.model_name,
                'provider': 'anthropic',
                'usage': response.get('usage', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic chat generation failed: {e}")
            return {'error': str(e)}
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding (Anthropic doesn't have embeddings, use alternative)"""
        logger.warning("Anthropic doesn't provide embeddings, using mock implementation")
        # In real implementation, might use a different service for embeddings
        return [0.0] * 1536  # Mock embedding
    
    def _convert_to_anthropic_format(self, messages: List[Dict], context: Dict) -> List[Dict]:
        """Convert OpenAI-style messages to Anthropic format"""
        # Anthropic has different message format, adapt accordingly
        converted = []
        
        if context.get('financial_context'):
            system_prompt = f"You are a cognitive financial intelligence assistant. {json.dumps(context['financial_context'])}"
            converted.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            if msg.get('role') == 'system' and not context.get('financial_context'):
                converted.append(msg)
            elif msg.get('role') in ['user', 'assistant']:
                converted.append(msg)
                
        return converted

class GeminiProvider(ModelProvider):
    """Google Gemini model provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://generativelanguage.googleapis.com')
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize Gemini client"""
        try:
            if not self.api_key:
                logger.error("Gemini API key not provided")
                return False
                
            self.client = MockGeminiClient(self.api_key, self.config)
            self.is_initialized = True
            logger.info(f"✅ Gemini provider initialized with model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini provider: {e}")
            return False
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using Google Gemini"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            enhanced_prompt = self._prepare_context_with_financial_data(
                prompt, kwargs.get('context', {})
            )
            
            response = await self.client.generate_completion(
                prompt=enhanced_prompt,
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'text': response['text'],
                'model': self.model_name,
                'provider': 'gemini',
                'usage': response.get('usage', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Gemini text generation failed: {e}")
            return {'error': str(e)}
    
    async def generate_chat_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response using Google Gemini"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            # Gemini has its own message format
            gemini_messages = self._convert_to_gemini_format(messages, kwargs.get('context', {}))
            
            response = await self.client.generate_chat_completion(
                messages=gemini_messages,
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return {
                'message': response['message'],
                'model': self.model_name,
                'provider': 'gemini',
                'usage': response.get('usage', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Gemini chat generation failed: {e}")
            return {'error': str(e)}
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini"""
        try:
            if not self.is_initialized:
                await self.initialize()
                
            embedding = await self.client.generate_embedding(text)
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Gemini embedding generation failed: {e}")
            return []
    
    def _convert_to_gemini_format(self, messages: List[Dict], context: Dict) -> List[Dict]:
        """Convert messages to Gemini format"""
        converted = []
        
        if context.get('financial_context'):
            system_content = f"Financial Intelligence Context: {json.dumps(context['financial_context'])}"
            converted.append({"role": "system", "parts": [{"text": system_content}]})
        
        for msg in messages:
            gemini_msg = {
                "role": msg.get('role', 'user'),
                "parts": [{"text": msg.get('content', '')}]
            }
            converted.append(gemini_msg)
            
        return converted


# Mock clients for demonstration
class MockOpenAIClient:
    """Mock OpenAI client"""
    
    def __init__(self, api_key: str, config: Dict):
        self.api_key = api_key
        self.config = config
    
    async def generate_completion(self, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.1)  # Simulate API delay
        return {
            'text': f"[MOCK OpenAI Response] This is a simulated response to: {kwargs.get('prompt', '')[:50]}...",
            'usage': {'prompt_tokens': 100, 'completion_tokens': 50, 'total_tokens': 150}
        }
    
    async def generate_chat_completion(self, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        last_message = kwargs.get('messages', [])[-1] if kwargs.get('messages') else {}
        return {
            'message': {
                'role': 'assistant',
                'content': f"[MOCK OpenAI Chat] Response to: {last_message.get('content', '')[:50]}..."
            },
            'usage': {'prompt_tokens': 120, 'completion_tokens': 60, 'total_tokens': 180}
        }
    
    async def generate_embedding(self, text: str) -> List[float]:
        await asyncio.sleep(0.1)
        # Generate mock embedding
        return [0.1] * 1536

class MockAnthropicClient:
    """Mock Anthropic client"""
    
    def __init__(self, api_key: str, config: Dict):
        self.api_key = api_key
        self.config = config
    
    async def generate_completion(self, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            'text': f"[MOCK Anthropic Response] Claude's response to: {kwargs.get('prompt', '')[:50]}...",
            'usage': {'input_tokens': 100, 'output_tokens': 50}
        }
    
    async def generate_chat_completion(self, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        last_message = kwargs.get('messages', [])[-1] if kwargs.get('messages') else {}
        return {
            'message': {
                'role': 'assistant',
                'content': f"[MOCK Anthropic Chat] Claude's response to: {last_message.get('content', '')[:50]}..."
            },
            'usage': {'input_tokens': 120, 'output_tokens': 60}
        }

class MockGeminiClient:
    """Mock Gemini client"""
    
    def __init__(self, api_key: str, config: Dict):
        self.api_key = api_key
        self.config = config
    
    async def generate_completion(self, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            'text': f"[MOCK Gemini Response] Gemini's response to: {kwargs.get('prompt', '')[:50]}...",
            'usage': {'prompt_tokens': 100, 'completion_tokens': 50}
        }
    
    async def generate_chat_completion(self, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        last_message = kwargs.get('messages', [])[-1] if kwargs.get('messages') else {}
        return {
            'message': {
                'role': 'model',
                'content': f"[MOCK Gemini Chat] Response to: {last_message.get('content', '')[:50]}..."
            },
            'usage': {'input_tokens': 120, 'output_tokens': 60}
        }
    
    async def generate_embedding(self, text: str) -> List[float]:
        await asyncio.sleep(0.1)
        return [0.2] * 768  # Different embedding size for Gemini


class ModelManager:
    """Manages multiple model providers"""
    
    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self.default_provider = None
        
    def add_provider(self, name: str, provider: ModelProvider):
        """Add a model provider"""
        self.providers[name] = provider
        
        # Set first provider as default
        if not self.default_provider:
            self.default_provider = name
    
    def set_default_provider(self, name: str):
        """Set the default provider"""
        if name in self.providers:
            self.default_provider = name
        else:
            raise ValueError(f"Provider {name} not found")
    
    def get_provider(self, name: Optional[str] = None) -> Optional[ModelProvider]:
        """Get a specific provider or the default"""
        if name:
            return self.providers.get(name)
        return self.providers.get(self.default_provider)
    
    async def initialize_all(self) -> Dict[str, bool]:
        """Initialize all providers"""
        results = {}
        for name, provider in self.providers.items():
            try:
                results[name] = await provider.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize provider {name}: {e}")
                results[name] = False
        return results
    
    async def generate_with_fallback(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text with fallback to other providers if primary fails"""
        provider_order = kwargs.get('provider_order', [self.default_provider])
        
        for provider_name in provider_order:
            provider = self.get_provider(provider_name)
            if provider and provider.is_initialized:
                try:
                    result = await provider.generate_text(prompt, **kwargs)
                    if 'error' not in result:
                        result['provider_used'] = provider_name
                        return result
                except Exception as e:
                    logger.warning(f"Provider {provider_name} failed: {e}")
                    continue
        
        return {'error': 'All providers failed'}
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by provider"""
        models = {}
        for name, provider in self.providers.items():
            if provider.is_initialized:
                models[name] = [provider.model_name]
        return models