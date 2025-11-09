"""
Load Balancer and Proxy Configuration for ElizaOS-OpenCog-GnuCash Microservices

Provides load balancing capabilities with Envoy and Traefik integration
for distributed cognitive financial services.
"""

import asyncio
import json
import yaml
import random
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from .service_discovery import ServiceInfo, ServiceDiscovery


@dataclass
class LoadBalancingConfig:
    """Load balancing configuration"""
    strategy: str = "round_robin"  # round_robin, weighted_round_robin, least_connections, random
    health_check_interval: int = 10
    timeout_seconds: int = 5
    max_retries: int = 3
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5


class LoadBalancer:
    """
    High-performance load balancer with multiple strategies
    Supports circuit breaking and health monitoring
    """
    
    def __init__(self, service_discovery: ServiceDiscovery, config: LoadBalancingConfig = None):
        self.service_discovery = service_discovery
        self.config = config or LoadBalancingConfig()
        self._counters: Dict[str, int] = {}
        self._weights: Dict[str, Dict[str, int]] = {}  # service_name -> {service_id: weight}
        self._circuit_breakers: Dict[str, Dict[str, int]] = {}  # service_id -> failure_count
        self.logger = logging.getLogger(__name__)
    
    async def get_service(self, service_name: str, exclude_services: List[str] = None) -> Optional[ServiceInfo]:
        """
        Get a service instance using the configured load balancing strategy
        """
        start_time = time.time()
        
        services = await self.service_discovery.discover(service_name)
        if not services:
            return None
        
        # Filter out excluded services and circuit breaker triggered services
        available_services = []
        for service in services:
            if exclude_services and service.service_id in exclude_services:
                continue
            
            if self._is_circuit_breaker_open(service.service_id):
                continue
            
            available_services.append(service)
        
        if not available_services:
            return None
        
        # Apply load balancing strategy
        selected_service = None
        
        if self.config.strategy == "round_robin":
            selected_service = self._round_robin_select(service_name, available_services)
        elif self.config.strategy == "weighted_round_robin":
            selected_service = self._weighted_round_robin_select(service_name, available_services)
        elif self.config.strategy == "random":
            selected_service = self._random_select(available_services)
        elif self.config.strategy == "least_connections":
            selected_service = self._least_connections_select(available_services)
        else:
            # Default to round robin
            selected_service = self._round_robin_select(service_name, available_services)
        
        selection_time = (time.time() - start_time) * 1000
        self.logger.debug(f"Load balancer selected service in {selection_time:.2f}ms using {self.config.strategy}")
        
        return selected_service
    
    def _round_robin_select(self, service_name: str, services: List[ServiceInfo]) -> ServiceInfo:
        """Round robin selection"""
        counter = self._counters.get(service_name, 0)
        selected = services[counter % len(services)]
        self._counters[service_name] = counter + 1
        return selected
    
    def _weighted_round_robin_select(self, service_name: str, services: List[ServiceInfo]) -> ServiceInfo:
        """Weighted round robin selection"""
        weights = self._weights.get(service_name, {})
        
        # If no weights configured, use equal weights
        if not weights:
            return self._round_robin_select(service_name, services)
        
        # Build weighted list
        weighted_services = []
        for service in services:
            weight = weights.get(service.service_id, 1)
            weighted_services.extend([service] * weight)
        
        if not weighted_services:
            return services[0]
        
        counter = self._counters.get(f"{service_name}_weighted", 0)
        selected = weighted_services[counter % len(weighted_services)]
        self._counters[f"{service_name}_weighted"] = counter + 1
        return selected
    
    def _random_select(self, services: List[ServiceInfo]) -> ServiceInfo:
        """Random selection"""
        return random.choice(services)
    
    def _least_connections_select(self, services: List[ServiceInfo]) -> ServiceInfo:
        """Least connections selection (simplified - uses random for now)"""
        # In a real implementation, this would track active connections
        # For now, we'll use random selection as a placeholder
        return self._random_select(services)
    
    def set_weights(self, service_name: str, weights: Dict[str, int]):
        """Set weights for weighted round robin"""
        self._weights[service_name] = weights
    
    def record_success(self, service_id: str):
        """Record successful request for circuit breaker"""
        if service_id in self._circuit_breakers:
            # Reset failure count on success
            self._circuit_breakers[service_id] = 0
    
    def record_failure(self, service_id: str):
        """Record failed request for circuit breaker"""
        if self.config.circuit_breaker_enabled:
            current_failures = self._circuit_breakers.get(service_id, 0)
            self._circuit_breakers[service_id] = current_failures + 1
            
            if self._circuit_breakers[service_id] >= self.config.circuit_breaker_threshold:
                self.logger.warning(f"Circuit breaker opened for service {service_id}")
    
    def _is_circuit_breaker_open(self, service_id: str) -> bool:
        """Check if circuit breaker is open for a service"""
        if not self.config.circuit_breaker_enabled:
            return False
        
        failures = self._circuit_breakers.get(service_id, 0)
        return failures >= self.config.circuit_breaker_threshold
    
    def reset_circuit_breaker(self, service_id: str):
        """Manually reset circuit breaker for a service"""
        self._circuit_breakers[service_id] = 0
        self.logger.info(f"Circuit breaker reset for service {service_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            'strategy': self.config.strategy,
            'counters': dict(self._counters),
            'weights': dict(self._weights),
            'circuit_breakers': dict(self._circuit_breakers),
            'config': asdict(self.config)
        }


class ConfigGenerator(ABC):
    """Abstract base class for proxy configuration generators"""
    
    @abstractmethod
    def generate_config(self, services: Dict[str, List[ServiceInfo]], 
                       lb_config: LoadBalancingConfig) -> str:
        """Generate proxy configuration"""
        pass


class EnvoyConfigGenerator(ConfigGenerator):
    """
    Envoy proxy configuration generator
    Generates dynamic Envoy configuration for service mesh
    """
    
    def __init__(self, admin_port: int = 9901, listener_port: int = 10000):
        self.admin_port = admin_port
        self.listener_port = listener_port
        self.logger = logging.getLogger(__name__)
    
    def generate_config(self, services: Dict[str, List[ServiceInfo]], 
                       lb_config: LoadBalancingConfig) -> str:
        """Generate Envoy configuration YAML"""
        
        # Map load balancing strategies
        envoy_lb_policy = {
            "round_robin": "ROUND_ROBIN",
            "weighted_round_robin": "ROUND_ROBIN",  # Weights handled in endpoints
            "random": "RANDOM",
            "least_connections": "LEAST_REQUEST"
        }.get(lb_config.strategy, "ROUND_ROBIN")
        
        config = {
            "admin": {
                "access_log_path": "/dev/null",
                "address": {
                    "socket_address": {
                        "address": "127.0.0.1",
                        "port_value": self.admin_port
                    }
                }
            },
            "static_resources": {
                "listeners": self._generate_listeners(services),
                "clusters": self._generate_clusters(services, envoy_lb_policy, lb_config)
            }
        }
        
        return yaml.dump(config, default_flow_style=False)
    
    def _generate_listeners(self, services: Dict[str, List[ServiceInfo]]) -> List[Dict]:
        """Generate Envoy listeners"""
        listeners = []
        
        port = self.listener_port
        for service_name in services.keys():
            listener = {
                "name": f"listener_{service_name}",
                "address": {
                    "socket_address": {
                        "address": "127.0.0.1",
                        "port_value": port
                    }
                },
                "filter_chains": [{
                    "filters": [{
                        "name": "envoy.filters.network.http_connection_manager",
                        "typed_config": {
                            "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                            "stat_prefix": f"ingress_{service_name}",
                            "codec_type": "AUTO",
                            "route_config": {
                                "name": f"local_route_{service_name}",
                                "virtual_hosts": [{
                                    "name": f"local_service_{service_name}",
                                    "domains": ["*"],
                                    "routes": [{
                                        "match": {"prefix": "/"},
                                        "route": {"cluster": f"cluster_{service_name}"}
                                    }]
                                }]
                            },
                            "http_filters": [{"name": "envoy.filters.http.router"}]
                        }
                    }]
                }]
            }
            listeners.append(listener)
            port += 1
        
        return listeners
    
    def _generate_clusters(self, services: Dict[str, List[ServiceInfo]], 
                          lb_policy: str, lb_config: LoadBalancingConfig) -> List[Dict]:
        """Generate Envoy clusters"""
        clusters = []
        
        for service_name, service_list in services.items():
            cluster = {
                "name": f"cluster_{service_name}",
                "connect_timeout": f"{lb_config.timeout_seconds}s",
                "type": "STATIC",
                "lb_policy": lb_policy,
                "load_assignment": {
                    "cluster_name": f"cluster_{service_name}",
                    "endpoints": [{
                        "lb_endpoints": []
                    }]
                }
            }
            
            # Add health checking
            if lb_config.health_check_interval > 0:
                cluster["health_checks"] = [{
                    "timeout": f"{lb_config.timeout_seconds}s",
                    "interval": f"{lb_config.health_check_interval}s",
                    "unhealthy_threshold": 3,
                    "healthy_threshold": 2,
                    "http_health_check": {
                        "path": "/health"
                    }
                }]
            
            # Add endpoints
            for service in service_list:
                endpoint = {
                    "endpoint": {
                        "address": {
                            "socket_address": {
                                "address": service.host,
                                "port_value": service.port
                            }
                        }
                    }
                }
                cluster["load_assignment"]["endpoints"][0]["lb_endpoints"].append(endpoint)
            
            clusters.append(cluster)
        
        return clusters


class TraefikConfigGenerator(ConfigGenerator):
    """
    Traefik proxy configuration generator
    Generates dynamic Traefik configuration for service mesh
    """
    
    def __init__(self, entry_point: str = "web", api_port: int = 8080):
        self.entry_point = entry_point
        self.api_port = api_port
        self.logger = logging.getLogger(__name__)
    
    def generate_config(self, services: Dict[str, List[ServiceInfo]], 
                       lb_config: LoadBalancingConfig) -> str:
        """Generate Traefik configuration YAML"""
        
        # Static configuration
        static_config = {
            "api": {
                "dashboard": True,
                "insecure": True
            },
            "entryPoints": {
                self.entry_point: {
                    "address": f":{self.api_port}"
                }
            },
            "providers": {
                "file": {
                    "filename": "/etc/traefik/dynamic.yml",
                    "watch": True
                }
            }
        }
        
        # Dynamic configuration
        dynamic_config = {
            "http": {
                "routers": {},
                "services": {}
            }
        }
        
        # Generate routes and services
        for service_name, service_list in services.items():
            # Router
            router_name = f"router-{service_name}"
            dynamic_config["http"]["routers"][router_name] = {
                "rule": f"PathPrefix(`/{service_name}`)",
                "service": f"service-{service_name}",
                "entryPoints": [self.entry_point]
            }
            
            # Service with load balancing
            service_config = {
                "loadBalancer": {
                    "servers": [],
                    "healthCheck": {
                        "path": "/health",
                        "interval": f"{lb_config.health_check_interval}s",
                        "timeout": f"{lb_config.timeout_seconds}s"
                    }
                }
            }
            
            # Add servers
            for service in service_list:
                server = {"url": service.url}
                service_config["loadBalancer"]["servers"].append(server)
            
            dynamic_config["http"]["services"][f"service-{service_name}"] = service_config
        
        # Combine configurations
        full_config = {
            "static": static_config,
            "dynamic": dynamic_config
        }
        
        return yaml.dump(full_config, default_flow_style=False)
    
    def generate_dynamic_config_only(self, services: Dict[str, List[ServiceInfo]], 
                                   lb_config: LoadBalancingConfig) -> str:
        """Generate only the dynamic configuration part"""
        config = {
            "http": {
                "routers": {},
                "services": {}
            }
        }
        
        for service_name, service_list in services.items():
            # Router
            router_name = f"router-{service_name}"
            config["http"]["routers"][router_name] = {
                "rule": f"PathPrefix(`/{service_name}`)",
                "service": f"service-{service_name}",
                "entryPoints": ["web"]
            }
            
            # Service
            service_config = {
                "loadBalancer": {
                    "servers": [{"url": service.url} for service in service_list],
                    "healthCheck": {
                        "path": "/health",
                        "interval": f"{lb_config.health_check_interval}s"
                    }
                }
            }
            
            config["http"]["services"][f"service-{service_name}"] = service_config
        
        return yaml.dump(config, default_flow_style=False)