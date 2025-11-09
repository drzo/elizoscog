"""
Service Discovery and Registry for ElizaOS-OpenCog-GnuCash Microservices

Provides dynamic service registration, discovery, and health monitoring
with sub-100ms response times for cognitive financial services.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib


@dataclass
class ServiceInfo:
    """Service information structure"""
    service_id: str
    service_name: str
    host: str
    port: int
    protocol: str = "http"
    version: str = "1.0.0"
    metadata: Dict[str, Any] = None
    health_check_path: str = "/health"
    tags: List[str] = None
    last_heartbeat: float = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = []
        if self.last_heartbeat is None:
            self.last_heartbeat = time.time()
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def health_url(self) -> str:
        return f"{self.url}{self.health_check_path}"
    
    def is_healthy(self, timeout_seconds: int = 30) -> bool:
        """Check if service is considered healthy based on heartbeat"""
        return time.time() - self.last_heartbeat < timeout_seconds


class ServiceRegistry:
    """
    In-memory service registry with automatic cleanup and health monitoring
    Designed for sub-100ms service discovery performance
    """
    
    def __init__(self, cleanup_interval: int = 60, service_timeout: int = 30):
        self._services: Dict[str, ServiceInfo] = {}
        self._service_names: Dict[str, List[str]] = {}  # name -> [service_ids]
        self._cleanup_interval = cleanup_interval
        self._service_timeout = service_timeout
        self._cleanup_task: Optional[asyncio.Task] = None
        self._subscribers: List[Callable[[str, ServiceInfo], None]] = []
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the registry and cleanup tasks"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.logger.info("Service registry started")
    
    async def stop(self):
        """Stop the registry"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            self.logger.info("Service registry stopped")
    
    def register_service(self, service: ServiceInfo) -> bool:
        """
        Register a service in the registry
        Returns True if registration successful
        """
        try:
            # Update heartbeat
            service.last_heartbeat = time.time()
            
            # Store service
            self._services[service.service_id] = service
            
            # Update name index
            if service.service_name not in self._service_names:
                self._service_names[service.service_name] = []
            
            if service.service_id not in self._service_names[service.service_name]:
                self._service_names[service.service_name].append(service.service_id)
            
            # Notify subscribers
            self._notify_subscribers('register', service)
            
            self.logger.info(f"Registered service {service.service_name}:{service.service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service.service_id}: {e}")
            return False
    
    def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service from the registry
        Returns True if deregistration successful
        """
        try:
            service = self._services.get(service_id)
            if not service:
                return False
            
            # Remove from services
            del self._services[service_id]
            
            # Remove from name index
            if service.service_name in self._service_names:
                if service_id in self._service_names[service.service_name]:
                    self._service_names[service.service_name].remove(service_id)
                
                # Clean up empty name entries
                if not self._service_names[service.service_name]:
                    del self._service_names[service.service_name]
            
            # Notify subscribers
            self._notify_subscribers('deregister', service)
            
            self.logger.info(f"Deregistered service {service.service_name}:{service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deregister service {service_id}: {e}")
            return False
    
    def discover_services(self, service_name: str, healthy_only: bool = True) -> List[ServiceInfo]:
        """
        Discover services by name
        Returns list of matching services, filtered by health if requested
        """
        start_time = time.time()
        
        try:
            service_ids = self._service_names.get(service_name, [])
            services = []
            
            for service_id in service_ids:
                service = self._services.get(service_id)
                if service:
                    if not healthy_only or service.is_healthy(self._service_timeout):
                        services.append(service)
            
            discovery_time = (time.time() - start_time) * 1000  # Convert to ms
            self.logger.debug(f"Discovered {len(services)} services for '{service_name}' in {discovery_time:.2f}ms")
            
            return services
            
        except Exception as e:
            self.logger.error(f"Failed to discover services for {service_name}: {e}")
            return []
    
    def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get specific service by ID"""
        return self._services.get(service_id)
    
    def get_all_services(self, healthy_only: bool = True) -> List[ServiceInfo]:
        """Get all registered services"""
        services = list(self._services.values())
        if healthy_only:
            services = [s for s in services if s.is_healthy(self._service_timeout)]
        return services
    
    def heartbeat(self, service_id: str) -> bool:
        """Update service heartbeat"""
        service = self._services.get(service_id)
        if service:
            service.last_heartbeat = time.time()
            return True
        return False
    
    def subscribe(self, callback: Callable[[str, ServiceInfo], None]):
        """Subscribe to service registration/deregistration events"""
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[str, ServiceInfo], None]):
        """Unsubscribe from service events"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def _notify_subscribers(self, event_type: str, service: ServiceInfo):
        """Notify all subscribers of service events"""
        for callback in self._subscribers:
            try:
                callback(event_type, service)
            except Exception as e:
                self.logger.error(f"Error in subscriber callback: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of unhealthy services"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_unhealthy_services()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_unhealthy_services(self):
        """Remove services that haven't sent heartbeats"""
        current_time = time.time()
        unhealthy_services = []
        
        for service_id, service in self._services.items():
            if current_time - service.last_heartbeat > self._service_timeout:
                unhealthy_services.append(service_id)
        
        for service_id in unhealthy_services:
            self.deregister_service(service_id)
        
        if unhealthy_services:
            self.logger.info(f"Cleaned up {len(unhealthy_services)} unhealthy services")


class ServiceDiscovery:
    """
    High-performance service discovery client
    Provides caching and load balancing for service lookups
    """
    
    def __init__(self, registry: ServiceRegistry, cache_ttl: int = 10):
        self.registry = registry
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple] = {}  # service_name -> (timestamp, services)
        self._round_robin_counters: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)
    
    async def discover(self, service_name: str, use_cache: bool = True) -> List[ServiceInfo]:
        """
        Discover services with caching support
        Returns cached results if available and valid
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache and service_name in self._cache:
            cache_time, cached_services = self._cache[service_name]
            if time.time() - cache_time < self.cache_ttl:
                discovery_time = (time.time() - start_time) * 1000
                self.logger.debug(f"Cache hit for '{service_name}' in {discovery_time:.2f}ms")
                return cached_services
        
        # Fetch from registry
        services = self.registry.discover_services(service_name, healthy_only=True)
        
        # Update cache
        if use_cache:
            self._cache[service_name] = (time.time(), services)
        
        discovery_time = (time.time() - start_time) * 1000
        self.logger.debug(f"Registry lookup for '{service_name}' in {discovery_time:.2f}ms")
        
        return services
    
    async def get_service(self, service_name: str, load_balance: bool = True) -> Optional[ServiceInfo]:
        """
        Get a single service instance with optional load balancing
        Uses round-robin by default
        """
        services = await self.discover(service_name)
        
        if not services:
            return None
        
        if not load_balance or len(services) == 1:
            return services[0]
        
        # Round-robin load balancing
        counter = self._round_robin_counters.get(service_name, 0)
        selected_service = services[counter % len(services)]
        self._round_robin_counters[service_name] = counter + 1
        
        return selected_service
    
    def clear_cache(self, service_name: str = None):
        """Clear cache for specific service or all services"""
        if service_name:
            self._cache.pop(service_name, None)
        else:
            self._cache.clear()
        
        self.logger.debug(f"Cleared cache for {service_name or 'all services'}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for cache_time, _ in self._cache.values():
            if current_time - cache_time < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl': self.cache_ttl
        }