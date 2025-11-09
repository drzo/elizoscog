"""
ElizaOS Core Features Integration

This module provides the core ElizaOS features integrated with the
OpenCog-GnuCash cognitive-financial intelligence framework.
"""

from .connectors import DiscordConnector, TelegramConnector
from .models import ModelProvider, OpenAIProvider, AnthropicProvider
from .memory import EnhancedMemoryManager
from .actions import ActionRegistry, ActionExecutor
from .dashboard import WebDashboard

__version__ = "1.0.0"
__all__ = [
    "DiscordConnector",
    "TelegramConnector", 
    "ModelProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "EnhancedMemoryManager",
    "ActionRegistry",
    "ActionExecutor",
    "WebDashboard"
]