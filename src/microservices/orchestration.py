"""
Service Orchestration and Health Monitoring for ElizaOS-OpenCog-GnuCash Microservices

Provides orchestration, health monitoring, and zero-downtime deployment
capabilities for cognitive financial services.
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from .service_discovery import ServiceRegistry, ServiceInfo, ServiceDiscovery
from .load_balancer import LoadBalancer, LoadBalancingConfig


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result structure"""
    service_id: str
    status: ServiceStatus
    response_time_ms: float
    timestamp: datetime
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class OrchestrationConfig:
    """Orchestration configuration"""
    health_check_interval: int = 30
    health_check_timeout: int = 5
    max_concurrent_health_checks: int = 10
    deployment_strategy: str = "rolling"  # rolling, blue_green, canary
    max_unavailable_percentage: int = 25
    readiness_probe_delay: int = 10
    liveness_probe_delay: int = 30


class HealthMonitor:
    """
    Advanced health monitoring system for microservices
    Provides real-time health checking and alerting
    """
    
    def __init__(self, service_discovery: ServiceDiscovery, config: OrchestrationConfig = None):
        self.service_discovery = service_discovery
        self.config = config or OrchestrationConfig()
        self._health_results: Dict[str, HealthCheckResult] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._subscribers: List[Callable[[HealthCheckResult], None]] = []
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start health monitoring"""
        if self._health_check_task is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.health_check_timeout)
            )
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self.logger.info("Health monitor started")
    
    async def stop(self):
        """Stop health monitoring"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        
        if self._session:
            await self._session.close()
            self._session = None
        
        self.logger.info("Health monitor stopped")
    
    async def check_service_health(self, service: ServiceInfo) -> HealthCheckResult:
        """
        Perform health check on a specific service
        Returns health check result with response time
        """
        start_time = time.time()
        
        try:
            if not self._session:
                raise Exception("Health monitor not started")
            
            async with self._session.get(service.health_url) as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    # Try to parse health details
                    try:
                        details = await response.json()
                    except:
                        details = {"status": "ok"}
                    
                    result = HealthCheckResult(
                        service_id=service.service_id,
                        status=ServiceStatus.HEALTHY,
                        response_time_ms=response_time_ms,
                        timestamp=datetime.now(),
                        details=details
                    )
                else:
                    result = HealthCheckResult(
                        service_id=service.service_id,
                        status=ServiceStatus.UNHEALTHY,
                        response_time_ms=response_time_ms,
                        timestamp=datetime.now(),
                        error_message=f"HTTP {response.status}"
                    )
            
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                service_id=service.service_id,
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(),
                error_message="Health check timeout"
            )
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                service_id=service.service_id,
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(),
                error_message=str(e)
            )
        
        # Store result and notify subscribers
        self._health_results[service.service_id] = result
        self._notify_subscribers(result)
        
        return result
    
    async def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """Check health of all registered services"""
        all_services = await self.service_discovery.discover("*")  # Get all services
        
        # Use semaphore to limit concurrent checks
        semaphore = asyncio.Semaphore(self.config.max_concurrent_health_checks)
        
        async def check_with_semaphore(service):
            async with semaphore:
                return await self.check_service_health(service)
        
        # Run health checks concurrently
        tasks = [check_with_semaphore(service) for service in all_services]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        health_results = {}
        for i, result in enumerate(results):
            if isinstance(result, HealthCheckResult):
                health_results[all_services[i].service_id] = result
            else:
                # Handle exceptions
                self.logger.error(f"Health check failed for {all_services[i].service_id}: {result}")
        
        return health_results
    
    def get_service_health(self, service_id: str) -> Optional[HealthCheckResult]:
        """Get latest health result for a service"""
        return self._health_results.get(service_id)
    
    def get_all_health_results(self) -> Dict[str, HealthCheckResult]:
        """Get all health results"""
        return dict(self._health_results)
    
    def subscribe(self, callback: Callable[[HealthCheckResult], None]):
        """Subscribe to health check events"""
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[HealthCheckResult], None]):
        """Unsubscribe from health check events"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def _notify_subscribers(self, result: HealthCheckResult):
        """Notify all subscribers of health check results"""
        for callback in self._subscribers:
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in health check subscriber: {e}")
    
    async def _health_check_loop(self):
        """Periodic health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self.check_all_services()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")


class ServiceOrchestrator:
    """
    Service orchestration engine for zero-downtime deployments
    Supports rolling updates, blue-green, and canary deployments
    """
    
    def __init__(self, service_registry: ServiceRegistry, health_monitor: HealthMonitor,
                 load_balancer: LoadBalancer, config: OrchestrationConfig = None):
        self.service_registry = service_registry
        self.health_monitor = health_monitor
        self.load_balancer = load_balancer
        self.config = config or OrchestrationConfig()
        self._deployment_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the orchestrator"""
        await self.health_monitor.start()
        self.logger.info("Service orchestrator started")
    
    async def stop(self):
        """Stop the orchestrator"""
        await self.health_monitor.stop()
        self.logger.info("Service orchestrator stopped")
    
    async def deploy_service(self, service_name: str, new_services: List[ServiceInfo],
                           strategy: str = None) -> Dict[str, Any]:
        """
        Deploy new service instances with zero downtime
        Supports rolling, blue-green, and canary strategies
        """
        deployment_id = f"deploy_{service_name}_{int(time.time())}"
        strategy = strategy or self.config.deployment_strategy
        
        self.logger.info(f"Starting {strategy} deployment {deployment_id} for {service_name}")
        
        deployment_result = {
            "deployment_id": deployment_id,
            "service_name": service_name,
            "strategy": strategy,
            "start_time": datetime.now(),
            "status": "in_progress",
            "new_services": len(new_services),
            "errors": []
        }
        
        try:
            if strategy == "rolling":
                result = await self._rolling_deployment(service_name, new_services)
            elif strategy == "blue_green":
                result = await self._blue_green_deployment(service_name, new_services)
            elif strategy == "canary":
                result = await self._canary_deployment(service_name, new_services)
            else:
                raise ValueError(f"Unknown deployment strategy: {strategy}")
            
            deployment_result.update(result)
            deployment_result["status"] = "completed"
            deployment_result["end_time"] = datetime.now()
            
        except Exception as e:
            deployment_result["status"] = "failed"
            deployment_result["error"] = str(e)
            deployment_result["end_time"] = datetime.now()
            self.logger.error(f"Deployment {deployment_id} failed: {e}")
        
        # Store deployment history
        self._deployment_history.append(deployment_result)
        
        return deployment_result
    
    async def _rolling_deployment(self, service_name: str, new_services: List[ServiceInfo]) -> Dict[str, Any]:
        """
        Rolling deployment strategy
        Gradually replaces old instances with new ones
        """
        # Get current services
        current_services = self.service_registry.discover_services(service_name)
        
        if not current_services:
            # No existing services, register all new ones
            for service in new_services:
                self.service_registry.register_service(service)
            return {"deployed_services": len(new_services), "replaced_services": 0}
        
        # Calculate how many services can be unavailable
        max_unavailable = max(1, len(current_services) * self.config.max_unavailable_percentage // 100)
        
        deployed_count = 0
        replaced_count = 0
        
        # Deploy new services in batches
        for i in range(0, len(new_services), max_unavailable):
            batch = new_services[i:i + max_unavailable]
            
            # Register new services
            for service in batch:
                self.service_registry.register_service(service)
                deployed_count += 1
            
            # Wait for readiness
            await asyncio.sleep(self.config.readiness_probe_delay)
            
            # Check health of new services
            for service in batch:
                health_result = await self.health_monitor.check_service_health(service)
                if health_result.status != ServiceStatus.HEALTHY:
                    raise Exception(f"New service {service.service_id} failed health check")
            
            # Remove old services if we have more than needed
            if len(current_services) > i:
                services_to_remove = current_services[i:i + len(batch)]
                for service in services_to_remove:
                    self.service_registry.deregister_service(service.service_id)
                    replaced_count += 1
        
        return {"deployed_services": deployed_count, "replaced_services": replaced_count}
    
    async def _blue_green_deployment(self, service_name: str, new_services: List[ServiceInfo]) -> Dict[str, Any]:
        """
        Blue-green deployment strategy
        Switches traffic from old to new services instantly
        """
        # Register all new services (green environment)
        for service in new_services:
            self.service_registry.register_service(service)
        
        # Wait for readiness
        await asyncio.sleep(self.config.readiness_probe_delay)
        
        # Health check all new services
        for service in new_services:
            health_result = await self.health_monitor.check_service_health(service)
            if health_result.status != ServiceStatus.HEALTHY:
                # Rollback: remove new services
                for rollback_service in new_services:
                    self.service_registry.deregister_service(rollback_service.service_id)
                raise Exception(f"New service {service.service_id} failed health check, rolled back")
        
        # Remove old services (blue environment)
        current_services = self.service_registry.discover_services(service_name)
        old_services = [s for s in current_services if s.service_id not in [ns.service_id for ns in new_services]]
        
        for service in old_services:
            self.service_registry.deregister_service(service.service_id)
        
        return {"deployed_services": len(new_services), "replaced_services": len(old_services)}
    
    async def _canary_deployment(self, service_name: str, new_services: List[ServiceInfo],
                                canary_percentage: int = 10) -> Dict[str, Any]:
        """
        Canary deployment strategy
        Gradually shifts traffic to new services
        """
        # Start with a small percentage of traffic to new services
        canary_count = max(1, len(new_services) * canary_percentage // 100)
        canary_services = new_services[:canary_count]
        
        # Deploy canary services
        for service in canary_services:
            self.service_registry.register_service(service)
        
        # Wait and monitor canary services
        await asyncio.sleep(self.config.readiness_probe_delay)
        
        # Check canary health
        for service in canary_services:
            health_result = await self.health_monitor.check_service_health(service)
            if health_result.status != ServiceStatus.HEALTHY:
                # Rollback canary
                for rollback_service in canary_services:
                    self.service_registry.deregister_service(rollback_service.service_id)
                raise Exception(f"Canary service {service.service_id} failed, rolled back")
        
        # If canary is successful, deploy remaining services
        remaining_services = new_services[canary_count:]
        if remaining_services:
            # Use rolling deployment for the rest
            result = await self._rolling_deployment(service_name, remaining_services)
            result["canary_services"] = len(canary_services)
            return result
        
        return {"deployed_services": len(canary_services), "canary_services": len(canary_services)}
    
    async def scale_service(self, service_name: str, target_instances: int) -> Dict[str, Any]:
        """
        Scale service to target number of instances
        Supports both scale up and scale down operations
        """
        current_services = self.service_registry.discover_services(service_name)
        current_count = len(current_services)
        
        if current_count == target_instances:
            return {"action": "no_change", "current_instances": current_count}
        
        if target_instances > current_count:
            # Scale up - add more instances
            needed = target_instances - current_count
            # In a real implementation, this would trigger container/pod creation
            # For now, we'll simulate with placeholder services
            new_services = []
            for i in range(needed):
                service_id = f"{service_name}_scaled_{int(time.time())}_{i}"
                service = ServiceInfo(
                    service_id=service_id,
                    service_name=service_name,
                    host="127.0.0.1",
                    port=8000 + i,  # Placeholder port
                    metadata={"scaled": True}
                )
                new_services.append(service)
            
            # Deploy new instances
            deployment_result = await self.deploy_service(service_name, new_services, "rolling")
            return {"action": "scale_up", "added_instances": needed, "deployment": deployment_result}
        
        else:
            # Scale down - remove instances
            to_remove = current_count - target_instances
            services_to_remove = current_services[:to_remove]
            
            for service in services_to_remove:
                self.service_registry.deregister_service(service.service_id)
            
            return {"action": "scale_down", "removed_instances": to_remove}
    
    def get_deployment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent deployment history"""
        return self._deployment_history[-limit:]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        all_services = self.service_registry.get_all_services(healthy_only=False)
        health_results = self.health_monitor.get_all_health_results()
        
        service_counts = {}
        for service in all_services:
            service_counts[service.service_name] = service_counts.get(service.service_name, 0) + 1
        
        healthy_count = sum(1 for result in health_results.values() 
                          if result.status == ServiceStatus.HEALTHY)
        
        return {
            "total_services": len(all_services),
            "healthy_services": healthy_count,
            "unhealthy_services": len(all_services) - healthy_count,
            "service_counts": service_counts,
            "last_deployment": self._deployment_history[-1] if self._deployment_history else None,
            "uptime": "running"  # Placeholder
        }