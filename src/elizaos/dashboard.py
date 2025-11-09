"""
ElizaOS Web Dashboard

Provides a modern web interface for managing agents, monitoring system status,
and interacting with the cognitive-financial intelligence framework.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

# Mock FastAPI imports (in real implementation would use actual FastAPI)
logger = logging.getLogger(__name__)

class WebDashboard:
    """Web dashboard for ElizaOS management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get('host', '0.0.0.0')
        self.port = config.get('port', 3000)
        self.debug = config.get('debug', False)
        
        self.cognitive_framework = None
        self.connector_manager = None
        self.model_manager = None
        self.memory_manager = None
        self.action_executor = None
        
        self.app = None
        self.server_task = None
        self.is_running = False
        
        # Dashboard state
        self.active_sessions = {}
        self.system_metrics = {}
        self.recent_activities = []
        
    async def initialize(self) -> bool:
        """Initialize the web dashboard"""
        try:
            # Setup web application
            self.app = MockFastAPIApp(self)
            
            # Setup routes
            self._setup_routes()
            
            logger.info(f"✅ Web dashboard initialized on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize web dashboard: {e}")
            return False
    
    def set_cognitive_framework(self, framework):
        """Set the cognitive framework"""
        self.cognitive_framework = framework
    
    def set_connector_manager(self, manager):
        """Set the connector manager"""
        self.connector_manager = manager
    
    def set_model_manager(self, manager):
        """Set the model manager"""
        self.model_manager = manager
    
    def set_memory_manager(self, manager):
        """Set the memory manager"""
        self.memory_manager = manager
    
    def set_action_executor(self, executor):
        """Set the action executor"""
        self.action_executor = executor
    
    async def start(self) -> bool:
        """Start the web dashboard server"""
        try:
            if self.is_running:
                logger.warning("Dashboard is already running")
                return True
            
            # Start the server
            self.server_task = asyncio.create_task(self._run_server())
            self.is_running = True
            
            logger.info(f"🚀 Web dashboard started at http://{self.host}:{self.port}")
            logger.info(f"📊 Dashboard interface: http://{self.host}:{self.port}")
            logger.info(f"🔌 API endpoint: http://{self.host}:{self.port}/api")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start web dashboard: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the web dashboard server"""
        try:
            if not self.is_running:
                return True
            
            if self.server_task:
                self.server_task.cancel()
                try:
                    await self.server_task
                except asyncio.CancelledError:
                    pass
            
            self.is_running = False
            logger.info("📴 Web dashboard stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop web dashboard: {e}")
            return False
    
    async def _run_server(self):
        """Run the web server"""
        try:
            # Mock server running
            logger.info(f"Mock web server running on {self.host}:{self.port}")
            
            # In real implementation, would use:
            # import uvicorn
            # await uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")
            
            # Keep running until cancelled
            while True:
                await asyncio.sleep(1)
                await self._update_system_metrics()
                
        except asyncio.CancelledError:
            logger.info("Web server task cancelled")
        except Exception as e:
            logger.error(f"Web server error: {e}")
    
    def _setup_routes(self):
        """Setup web application routes"""
        # In real implementation, would setup FastAPI routes here
        routes = [
            # Dashboard
            ('GET', '/', self.dashboard_home),
            ('GET', '/agents', self.agents_page),
            ('GET', '/memory', self.memory_page),
            ('GET', '/actions', self.actions_page),
            ('GET', '/settings', self.settings_page),
            
            # API endpoints
            ('GET', '/api/status', self.api_get_status),
            ('GET', '/api/agents', self.api_get_agents),
            ('POST', '/api/agents/{agent_id}/message', self.api_send_message),
            ('GET', '/api/memory/stats', self.api_get_memory_stats),
            ('GET', '/api/memory/search', self.api_search_memory),
            ('GET', '/api/actions', self.api_get_actions),
            ('POST', '/api/actions/execute', self.api_execute_action),
            ('GET', '/api/connectors', self.api_get_connectors),
            ('POST', '/api/connectors/{connector}/connect', self.api_connect_platform),
            ('GET', '/api/models', self.api_get_models),
            ('GET', '/api/metrics', self.api_get_metrics)
        ]
        
        logger.info(f"📋 Setup {len(routes)} dashboard routes")
    
    # Dashboard Pages
    
    async def dashboard_home(self, request):
        """Main dashboard page"""
        return {
            'template': 'dashboard.html',
            'context': {
                'title': 'ElizaOS Dashboard',
                'system_status': await self._get_system_status(),
                'recent_activities': self.recent_activities[-10:],
                'active_agents': await self._get_active_agents_summary()
            }
        }
    
    async def agents_page(self, request):
        """Agents management page"""
        agents = await self._get_agents_info()
        return {
            'template': 'agents.html',
            'context': {
                'title': 'Agent Management',
                'agents': agents,
                'total_agents': len(agents)
            }
        }
    
    async def memory_page(self, request):
        """Memory management page"""
        memory_stats = await self._get_memory_statistics()
        return {
            'template': 'memory.html',
            'context': {
                'title': 'Memory Management',
                'stats': memory_stats,
                'recent_memories': await self._get_recent_memories()
            }
        }
    
    async def actions_page(self, request):
        """Actions management page"""
        actions = await self._get_actions_info()
        return {
            'template': 'actions.html',
            'context': {
                'title': 'Action Management',
                'actions': actions,
                'execution_stats': await self._get_action_statistics()
            }
        }
    
    async def settings_page(self, request):
        """Settings page"""
        return {
            'template': 'settings.html',
            'context': {
                'title': 'System Settings',
                'config': await self._get_system_config(),
                'providers': await self._get_provider_status()
            }
        }
    
    # API Endpoints
    
    async def api_get_status(self, request):
        """Get system status API"""
        return await self._get_system_status()
    
    async def api_get_agents(self, request):
        """Get agents information API"""
        return {
            'agents': await self._get_agents_info(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def api_send_message(self, request):
        """Send message to agent API"""
        try:
            agent_id = request.path_params.get('agent_id')
            body = await request.json()
            message = body.get('message', '')
            
            if not message:
                return {'error': 'Message is required'}
            
            # Send to cognitive framework
            if self.cognitive_framework and agent_id in self.cognitive_framework.cognitive_agents:
                agent = self.cognitive_framework.cognitive_agents[agent_id]
                result = await agent.process_message(message, {'source': 'dashboard'})
                
                # Log activity
                self._log_activity(f"Message sent to {agent_id}", 'message')
                
                return {
                    'success': True,
                    'agent_id': agent_id,
                    'response': result
                }
            
            return {'error': f'Agent {agent_id} not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    async def api_get_memory_stats(self, request):
        """Get memory statistics API"""
        return await self._get_memory_statistics()
    
    async def api_search_memory(self, request):
        """Search memory API"""
        try:
            query = request.query_params.get('q', '')
            limit = int(request.query_params.get('limit', 10))
            
            if self.memory_manager:
                memories = await self.memory_manager.retrieve_memories(
                    query=query, limit=limit
                )
                return {
                    'query': query,
                    'results': [
                        {
                            'id': memory.id,
                            'content': memory.content[:200] + '...' if len(memory.content) > 200 else memory.content,
                            'type': memory.content_type,
                            'source': memory.source,
                            'timestamp': memory.timestamp.isoformat(),
                            'importance': memory.importance_score
                        }
                        for memory in memories
                    ],
                    'total': len(memories)
                }
            
            return {'error': 'Memory manager not available'}
            
        except Exception as e:
            return {'error': str(e)}
    
    async def api_get_actions(self, request):
        """Get available actions API"""
        return await self._get_actions_info()
    
    async def api_execute_action(self, request):
        """Execute action API"""
        try:
            body = await request.json()
            action_name = body.get('action')
            parameters = body.get('parameters', {})
            
            if not action_name:
                return {'error': 'Action name is required'}
            
            if self.action_executor:
                result = await self.action_executor.execute_action(action_name, parameters)
                
                # Log activity
                self._log_activity(f"Action executed: {action_name}", 'action')
                
                return result.to_dict()
            
            return {'error': 'Action executor not available'}
            
        except Exception as e:
            return {'error': str(e)}
    
    async def api_get_connectors(self, request):
        """Get connector status API"""
        if self.connector_manager:
            connectors = {}
            for name, connector in self.connector_manager.connectors.items():
                connectors[name] = {
                    'name': name,
                    'connected': connector.is_connected,
                    'type': connector.__class__.__name__
                }
            return {'connectors': connectors}
        
        return {'error': 'Connector manager not available'}
    
    async def api_connect_platform(self, request):
        """Connect to platform API"""
        try:
            connector_name = request.path_params.get('connector')
            
            if self.connector_manager:
                connector = self.connector_manager.get_connector(connector_name)
                if connector:
                    success = await connector.connect()
                    
                    # Log activity
                    status = 'connected' if success else 'failed to connect'
                    self._log_activity(f"Platform {connector_name} {status}", 'connector')
                    
                    return {
                        'success': success,
                        'connector': connector_name,
                        'status': 'connected' if success else 'failed'
                    }
            
            return {'error': f'Connector {connector_name} not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    async def api_get_models(self, request):
        """Get model providers API"""
        if self.model_manager:
            providers = {}
            for name, provider in self.model_manager.providers.items():
                providers[name] = {
                    'name': name,
                    'model': provider.model_name,
                    'initialized': provider.is_initialized,
                    'type': provider.__class__.__name__
                }
            return {'providers': providers}
        
        return {'error': 'Model manager not available'}
    
    async def api_get_metrics(self, request):
        """Get system metrics API"""
        return self.system_metrics
    
    # Helper methods
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'uptime': self._get_uptime(),
            'status': 'running' if self.is_running else 'stopped',
            'components': {}
        }
        
        # Check component status
        if self.cognitive_framework:
            status['components']['cognitive_framework'] = 'active'
        
        if self.connector_manager:
            connected_count = sum(1 for c in self.connector_manager.connectors.values() if c.is_connected)
            status['components']['connectors'] = f"{connected_count}/{len(self.connector_manager.connectors)} connected"
        
        if self.model_manager:
            initialized_count = sum(1 for p in self.model_manager.providers.values() if p.is_initialized)
            status['components']['models'] = f"{initialized_count}/{len(self.model_manager.providers)} initialized"
        
        if self.memory_manager:
            status['components']['memory'] = 'active'
        
        if self.action_executor:
            status['components']['actions'] = 'active'
        
        return status
    
    async def _get_agents_info(self) -> List[Dict[str, Any]]:
        """Get information about all agents"""
        agents = []
        
        if self.cognitive_framework and hasattr(self.cognitive_framework, 'cognitive_agents'):
            for agent_id, agent in self.cognitive_framework.cognitive_agents.items():
                agents.append({
                    'id': agent_id,
                    'name': agent_id.replace('_', ' ').title(),
                    'status': 'active',
                    'type': agent.__class__.__name__,
                    'description': getattr(agent, 'description', 'Cognitive agent')
                })
        
        return agents
    
    async def _get_active_agents_summary(self) -> Dict[str, Any]:
        """Get summary of active agents"""
        agents = await self._get_agents_info()
        return {
            'total': len(agents),
            'active': len([a for a in agents if a['status'] == 'active']),
            'types': list(set(a['type'] for a in agents))
        }
    
    async def _get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if self.memory_manager:
            return await self.memory_manager.get_memory_statistics()
        
        return {
            'total_memories': 0,
            'by_type': {},
            'by_source': {},
            'average_importance': 0,
            'recent_memories_24h': 0
        }
    
    async def _get_recent_memories(self) -> List[Dict[str, Any]]:
        """Get recent memories for display"""
        if self.memory_manager:
            memories = await self.memory_manager.retrieve_memories(limit=5)
            return [
                {
                    'id': memory.id[:8],
                    'content': memory.content[:100] + '...' if len(memory.content) > 100 else memory.content,
                    'type': memory.content_type,
                    'timestamp': memory.timestamp.strftime('%Y-%m-%d %H:%M')
                }
                for memory in memories
            ]
        
        return []
    
    async def _get_actions_info(self) -> Dict[str, Any]:
        """Get information about available actions"""
        if self.action_executor and self.action_executor.registry:
            actions = self.action_executor.registry.list_actions()
            return {
                'available_actions': actions,
                'total_actions': len(actions)
            }
        
        return {'available_actions': [], 'total_actions': 0}
    
    async def _get_action_statistics(self) -> Dict[str, Any]:
        """Get action execution statistics"""
        if self.action_executor:
            return self.action_executor.get_execution_statistics()
        
        return {
            'total_executions': 0,
            'successful_executions': 0,
            'failure_rate': 0,
            'average_execution_time': 0
        }
    
    async def _get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return {
            'dashboard': {
                'host': self.host,
                'port': self.port,
                'debug': self.debug
            },
            'framework': self.config
        }
    
    async def _get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        if self.model_manager:
            status['models'] = {
                name: {
                    'initialized': provider.is_initialized,
                    'model': provider.model_name
                }
                for name, provider in self.model_manager.providers.items()
            }
        
        if self.connector_manager:
            status['connectors'] = {
                name: {
                    'connected': connector.is_connected,
                    'type': connector.__class__.__name__
                }
                for name, connector in self.connector_manager.connectors.items()
            }
        
        return status
    
    async def _update_system_metrics(self):
        """Update system metrics"""
        self.system_metrics = {
            'timestamp': datetime.now().isoformat(),
            'memory_usage': await self._get_memory_usage(),
            'active_connections': await self._get_active_connections(),
            'recent_activity_count': len(self.recent_activities),
            'uptime_seconds': self._get_uptime_seconds()
        }
    
    async def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage metrics"""
        # Mock implementation
        return {
            'total_mb': 512,
            'used_mb': 256,
            'free_mb': 256,
            'usage_percent': 50
        }
    
    async def _get_active_connections(self) -> int:
        """Get number of active connections"""
        count = 0
        if self.connector_manager:
            count = sum(1 for c in self.connector_manager.connectors.values() if c.is_connected)
        return count
    
    def _get_uptime(self) -> str:
        """Get human-readable uptime"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
        
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return f"{days}d {hours}h {minutes}m"
    
    def _get_uptime_seconds(self) -> int:
        """Get uptime in seconds"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
        
        return int((datetime.now() - self.start_time).total_seconds())
    
    def _log_activity(self, message: str, activity_type: str):
        """Log system activity"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': activity_type
        }
        
        self.recent_activities.append(activity)
        
        # Keep only recent activities
        if len(self.recent_activities) > 100:
            self.recent_activities = self.recent_activities[-100:]
        
        logger.info(f"📊 Activity: {message}")

# Mock FastAPI application for demonstration
class MockFastAPIApp:
    """Mock FastAPI application"""
    
    def __init__(self, dashboard: WebDashboard):
        self.dashboard = dashboard
        self.routes = []
    
    def add_route(self, method: str, path: str, handler):
        """Add route to application"""
        self.routes.append((method, path, handler))
    
    async def handle_request(self, method: str, path: str, request):
        """Handle incoming request"""
        for route_method, route_path, handler in self.routes:
            if method == route_method and path == route_path:
                return await handler(request)
        
        return {'error': 'Route not found', 'status': 404}

# Mock request object
class MockRequest:
    """Mock request object"""
    
    def __init__(self, method: str, path: str, query_params: Dict = None, 
                 path_params: Dict = None, body: Any = None):
        self.method = method
        self.path = path
        self.query_params = query_params or {}
        self.path_params = path_params or {}
        self._body = body
    
    async def json(self):
        """Get JSON body"""
        return self._body or {}

# Dashboard template generator (mock)
class DashboardTemplates:
    """Generate dashboard HTML templates"""
    
    @staticmethod
    def generate_dashboard_html(context: Dict) -> str:
        """Generate main dashboard HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{context['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .status.running {{ background-color: #d4edda; }}
                .card {{ border: 1px solid #ddd; padding: 15px; margin: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>{context['title']}</h1>
            <div class="status running">
                <h3>System Status: {context['system_status']['status']}</h3>
                <p>Uptime: {context['system_status']['uptime']}</p>
            </div>
            <div class="card">
                <h3>Active Agents: {context['active_agents']['total']}</h3>
                <p>Types: {', '.join(context['active_agents']['types'])}</p>
            </div>
            <div class="card">
                <h3>Recent Activities</h3>
                <ul>
                    {''.join(f"<li>{activity['message']} - {activity['timestamp']}</li>" for activity in context['recent_activities'])}
                </ul>
            </div>
        </body>
        </html>
        """