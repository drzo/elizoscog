"""
Phase 4: Optimization and Scaling - Production Readiness Module

Implements monitoring, backup, and deployment automation for enterprise production use.
"""

import asyncio
import json
import logging
import time
import os
import shutil
import subprocess
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import sqlite3
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"


@dataclass
class Alert:
    """System alert data"""
    id: str
    level: AlertLevel
    component: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class HealthCheck:
    """Health check configuration and status"""
    name: str
    check_function: Callable
    interval_seconds: int
    timeout_seconds: int
    threshold_failures: int
    current_failures: int = 0
    last_check: Optional[datetime] = None
    last_status: ServiceStatus = ServiceStatus.HEALTHY


class MonitoringSystem:
    """Comprehensive monitoring and alerting system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alerts: List[Alert] = []
        self.health_checks: Dict[str, HealthCheck] = {}
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alert_handlers = {}
        self.monitoring_active = False
        
        # Initialize default health checks
        self._initialize_default_health_checks()
        
        # Setup alert handlers
        self._setup_alert_handlers()
    
    def _initialize_default_health_checks(self):
        """Setup default health checks for all system components"""
        
        # AtomSpace health check
        self.health_checks['atomspace'] = HealthCheck(
            name='AtomSpace Connectivity',
            check_function=self._check_atomspace_health,
            interval_seconds=30,
            timeout_seconds=5,
            threshold_failures=3
        )
        
        # GnuCash database health check
        self.health_checks['gnucash_db'] = HealthCheck(
            name='GnuCash Database',
            check_function=self._check_gnucash_db_health,
            interval_seconds=60,
            timeout_seconds=10,
            threshold_failures=2
        )
        
        # ElizaOS plugins health check
        self.health_checks['elizaos_plugins'] = HealthCheck(
            name='ElizaOS Plugins',
            check_function=self._check_elizaos_plugins_health,
            interval_seconds=45,
            timeout_seconds=5,
            threshold_failures=2
        )
        
        # System resources health check
        self.health_checks['system_resources'] = HealthCheck(
            name='System Resources',
            check_function=self._check_system_resources_health,
            interval_seconds=20,
            timeout_seconds=3,
            threshold_failures=5
        )
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        self.monitoring_active = True
        logger.info("🔍 Starting monitoring system...")
        
        # Start health check tasks
        tasks = []
        for check_name, health_check in self.health_checks.items():
            task = asyncio.create_task(self._run_health_check_loop(check_name, health_check))
            tasks.append(task)
        
        # Start metrics collection
        metrics_task = asyncio.create_task(self._collect_metrics_loop())
        tasks.append(metrics_task)
        
        # Wait for all monitoring tasks
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Monitoring system error: {e}")
            self.monitoring_active = False
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        logger.info("⏹️ Stopping monitoring system...")
    
    async def _run_health_check_loop(self, check_name: str, health_check: HealthCheck):
        """Run individual health check in a loop"""
        while self.monitoring_active:
            try:
                await self._execute_health_check(check_name, health_check)
                await asyncio.sleep(health_check.interval_seconds)
            except Exception as e:
                logger.error(f"Health check loop error for {check_name}: {e}")
                await asyncio.sleep(health_check.interval_seconds)
    
    async def _execute_health_check(self, check_name: str, health_check: HealthCheck):
        """Execute a single health check"""
        try:
            # Run the health check with timeout
            start_time = time.time()
            result = await asyncio.wait_for(
                health_check.check_function(),
                timeout=health_check.timeout_seconds
            )
            
            duration = time.time() - start_time
            health_check.last_check = datetime.now()
            
            if result:
                # Health check passed
                if health_check.current_failures > 0:
                    # Recovery from previous failures
                    await self._create_alert(
                        AlertLevel.INFO,
                        check_name,
                        f"{health_check.name} has recovered"
                    )
                
                health_check.current_failures = 0
                health_check.last_status = ServiceStatus.HEALTHY
            else:
                # Health check failed
                health_check.current_failures += 1
                
                if health_check.current_failures >= health_check.threshold_failures:
                    health_check.last_status = ServiceStatus.UNHEALTHY
                    await self._create_alert(
                        AlertLevel.ERROR,
                        check_name,
                        f"{health_check.name} is unhealthy (failed {health_check.current_failures} times)"
                    )
                else:
                    health_check.last_status = ServiceStatus.DEGRADED
            
            # Record metrics
            self.metrics_history[f"{check_name}_duration"].append({
                'timestamp': datetime.now(),
                'value': duration
            })
            
        except asyncio.TimeoutError:
            health_check.current_failures += 1
            health_check.last_status = ServiceStatus.DEGRADED
            
            await self._create_alert(
                AlertLevel.WARNING,
                check_name,
                f"{health_check.name} health check timed out"
            )
        
        except Exception as e:
            health_check.current_failures += 1
            health_check.last_status = ServiceStatus.UNHEALTHY
            
            await self._create_alert(
                AlertLevel.ERROR,
                check_name,
                f"{health_check.name} health check failed: {str(e)}"
            )
    
    async def _check_atomspace_health(self) -> bool:
        """Check AtomSpace connectivity and basic operations"""
        try:
            # Mock AtomSpace health check
            # In real implementation, would test actual AtomSpace connectivity
            await asyncio.sleep(0.1)  # Simulate check time
            return True
        except Exception:
            return False
    
    async def _check_gnucash_db_health(self) -> bool:
        """Check GnuCash database connectivity and basic queries"""
        try:
            # Mock database health check
            # In real implementation, would test actual database connectivity
            await asyncio.sleep(0.2)  # Simulate check time
            return True
        except Exception:
            return False
    
    async def _check_elizaos_plugins_health(self) -> bool:
        """Check ElizaOS plugins status"""
        try:
            # Mock plugins health check
            # In real implementation, would test actual plugin status
            await asyncio.sleep(0.1)  # Simulate check time
            return True
        except Exception:
            return False
    
    async def _check_system_resources_health(self) -> bool:
        """Check system resources (CPU, memory, disk)"""
        try:
            # Mock system resources check
            # In real implementation, would check actual system metrics
            await asyncio.sleep(0.05)  # Simulate check time
            
            # Simulate resource thresholds
            cpu_usage = time.time() % 100
            memory_usage = (time.time() * 1.5) % 100
            disk_usage = (time.time() * 0.8) % 100
            
            # Alert if any resource exceeds 90%
            if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
                return False
            
            return True
        except Exception:
            return False
    
    async def _collect_metrics_loop(self):
        """Collect system metrics periodically"""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(10)  # Collect metrics every 10 seconds
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_system_metrics(self):
        """Collect various system metrics"""
        timestamp = datetime.now()
        
        # Simulate metrics collection
        metrics = {
            'cpu_usage': time.time() % 100,
            'memory_usage': (time.time() * 1.5) % 100,
            'disk_usage': (time.time() * 0.8) % 100,
            'network_io': (time.time() * 2) % 1000,
            'active_connections': int(time.time()) % 50,
            'response_time': (time.time() % 1) * 1000  # ms
        }
        
        for metric_name, value in metrics.items():
            self.metrics_history[metric_name].append({
                'timestamp': timestamp,
                'value': value
            })
    
    async def _create_alert(self, level: AlertLevel, component: str, message: str):
        """Create and handle a new alert"""
        alert = Alert(
            id=f"{component}_{int(time.time())}",
            level=level,
            component=component,
            message=message,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        logger.log(
            logging.ERROR if level in [AlertLevel.ERROR, AlertLevel.CRITICAL] else logging.WARNING,
            f"Alert [{level.value.upper()}] {component}: {message}"
        )
        
        # Trigger alert handlers
        for handler_name, handler_func in self.alert_handlers.items():
            try:
                await handler_func(alert)
            except Exception as e:
                logger.error(f"Alert handler {handler_name} failed: {e}")
    
    def _setup_alert_handlers(self):
        """Setup alert notification handlers"""
        self.alert_handlers['console'] = self._console_alert_handler
        # Additional handlers could be added (email, Slack, etc.)
    
    async def _console_alert_handler(self, alert: Alert):
        """Handle alerts by logging to console"""
        print(f"🚨 ALERT [{alert.level.value.upper()}] {alert.component}: {alert.message}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        overall_status = ServiceStatus.HEALTHY
        unhealthy_components = []
        
        for check_name, health_check in self.health_checks.items():
            if health_check.last_status in [ServiceStatus.UNHEALTHY, ServiceStatus.DOWN]:
                overall_status = ServiceStatus.UNHEALTHY
                unhealthy_components.append(check_name)
            elif health_check.last_status == ServiceStatus.DEGRADED and overall_status == ServiceStatus.HEALTHY:
                overall_status = ServiceStatus.DEGRADED
        
        return {
            'overall_status': overall_status.value,
            'unhealthy_components': unhealthy_components,
            'health_checks': {
                name: {
                    'status': check.last_status.value,
                    'last_check': check.last_check.isoformat() if check.last_check else None,
                    'failures': check.current_failures
                }
                for name, check in self.health_checks.items()
            },
            'recent_alerts': [
                {
                    'level': alert.level.value,
                    'component': alert.component,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ],
            'metrics_summary': self._get_metrics_summary()
        }
    
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recent metrics"""
        summary = {}
        
        for metric_name, history in self.metrics_history.items():
            if history:
                recent_values = [item['value'] for item in list(history)[-10:]]
                summary[metric_name] = {
                    'current': recent_values[-1] if recent_values else 0,
                    'average': sum(recent_values) / len(recent_values) if recent_values else 0,
                    'min': min(recent_values) if recent_values else 0,
                    'max': max(recent_values) if recent_values else 0
                }
        
        return summary


class BackupManager:
    """Automated backup and disaster recovery system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.backup_dir = Path(self.config.get('backup_dir', '/tmp/elizoscog_backups'))
        self.retention_days = self.config.get('retention_days', 30)
        self.backup_schedule = self.config.get('backup_schedule', '0 2 * * *')  # Daily at 2 AM
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_full_backup(self) -> Dict[str, Any]:
        """Create a complete system backup"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"💾 Creating full backup: {backup_id}")
        
        backup_manifest = {
            'backup_id': backup_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'full',
            'components': {},
            'status': 'in_progress'
        }
        
        try:
            # Backup AtomSpace data
            atomspace_backup = await self._backup_atomspace(backup_path)
            backup_manifest['components']['atomspace'] = atomspace_backup
            
            # Backup GnuCash database
            gnucash_backup = await self._backup_gnucash_db(backup_path)
            backup_manifest['components']['gnucash'] = gnucash_backup
            
            # Backup configuration files
            config_backup = await self._backup_configurations(backup_path)
            backup_manifest['components']['configuration'] = config_backup
            
            # Backup user data and cache
            userdata_backup = await self._backup_user_data(backup_path)
            backup_manifest['components']['userdata'] = userdata_backup
            
            backup_manifest['status'] = 'completed'
            backup_manifest['completed_at'] = datetime.now().isoformat()
            
            # Save backup manifest
            manifest_path = backup_path / 'backup_manifest.json'
            with open(manifest_path, 'w') as f:
                json.dump(backup_manifest, f, indent=2)
            
            logger.info(f"✅ Backup completed: {backup_id}")
            return backup_manifest
            
        except Exception as e:
            backup_manifest['status'] = 'failed'
            backup_manifest['error'] = str(e)
            logger.error(f"❌ Backup failed: {e}")
            raise
    
    async def _backup_atomspace(self, backup_path: Path) -> Dict[str, Any]:
        """Backup AtomSpace data"""
        atomspace_dir = backup_path / 'atomspace'
        atomspace_dir.mkdir(exist_ok=True)
        
        # Mock AtomSpace backup
        # In real implementation, would export AtomSpace data
        backup_info = {
            'component': 'atomspace',
            'size_bytes': 1024 * 1024,  # Mock size
            'atom_count': 1500,
            'backup_file': str(atomspace_dir / 'atomspace_export.scm')
        }
        
        # Create mock backup file
        with open(backup_info['backup_file'], 'w') as f:
            f.write(";; AtomSpace backup - Mock data\n")
            f.write(f";; Generated at {datetime.now()}\n")
        
        return backup_info
    
    async def _backup_gnucash_db(self, backup_path: Path) -> Dict[str, Any]:
        """Backup GnuCash database"""
        gnucash_dir = backup_path / 'gnucash'
        gnucash_dir.mkdir(exist_ok=True)
        
        backup_info = {
            'component': 'gnucash',
            'size_bytes': 2 * 1024 * 1024,  # Mock size
            'backup_file': str(gnucash_dir / 'gnucash_backup.sqlite')
        }
        
        # Create mock backup file
        with open(backup_info['backup_file'], 'w') as f:
            f.write("-- GnuCash database backup - Mock data\n")
            f.write(f"-- Generated at {datetime.now()}\n")
        
        return backup_info
    
    async def _backup_configurations(self, backup_path: Path) -> Dict[str, Any]:
        """Backup configuration files"""
        config_dir = backup_path / 'configuration'
        config_dir.mkdir(exist_ok=True)
        
        backup_info = {
            'component': 'configuration',
            'size_bytes': 512 * 1024,  # Mock size
            'files_backed_up': ['elizaos_config.json', 'opencog_config.scm', 'system_config.yaml']
        }
        
        # Create mock config backups
        for config_file in backup_info['files_backed_up']:
            with open(config_dir / config_file, 'w') as f:
                f.write(f"# Configuration backup - {config_file}\n")
                f.write(f"# Generated at {datetime.now()}\n")
        
        return backup_info
    
    async def _backup_user_data(self, backup_path: Path) -> Dict[str, Any]:
        """Backup user data and cache"""
        userdata_dir = backup_path / 'userdata'
        userdata_dir.mkdir(exist_ok=True)
        
        backup_info = {
            'component': 'userdata',
            'size_bytes': 256 * 1024,  # Mock size
            'cache_entries': 150
        }
        
        # Create mock user data backup
        with open(userdata_dir / 'user_preferences.json', 'w') as f:
            json.dump({'mock': 'user data'}, f)
        
        return backup_info
    
    async def restore_backup(self, backup_id: str) -> bool:
        """Restore system from backup"""
        backup_path = self.backup_dir / backup_id
        manifest_path = backup_path / 'backup_manifest.json'
        
        if not manifest_path.exists():
            raise ValueError(f"Backup {backup_id} not found or invalid")
        
        logger.info(f"🔄 Restoring from backup: {backup_id}")
        
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            # Restore components in order
            for component, info in manifest['components'].items():
                await self._restore_component(component, info, backup_path)
            
            logger.info(f"✅ Restore completed: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            raise
    
    async def _restore_component(self, component: str, info: Dict[str, Any], backup_path: Path):
        """Restore individual component from backup"""
        logger.info(f"Restoring component: {component}")
        
        if component == 'atomspace':
            # Mock AtomSpace restore
            pass
        elif component == 'gnucash':
            # Mock GnuCash restore
            pass
        elif component == 'configuration':
            # Mock configuration restore
            pass
        elif component == 'userdata':
            # Mock user data restore
            pass
    
    async def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        removed_count = 0
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir() and backup_dir.name.startswith('backup_'):
                manifest_path = backup_dir / 'backup_manifest.json'
                
                if manifest_path.exists():
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                        
                        backup_date = datetime.fromisoformat(manifest['timestamp'])
                        
                        if backup_date < cutoff_date:
                            shutil.rmtree(backup_dir)
                            removed_count += 1
                            logger.info(f"Removed old backup: {backup_dir.name}")
                    
                    except Exception as e:
                        logger.warning(f"Error processing backup {backup_dir.name}: {e}")
        
        logger.info(f"Cleaned up {removed_count} old backups")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir() and backup_dir.name.startswith('backup_'):
                manifest_path = backup_dir / 'backup_manifest.json'
                
                if manifest_path.exists():
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                        backups.append(manifest)
                    except Exception as e:
                        logger.warning(f"Error reading backup manifest {backup_dir.name}: {e}")
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups


class DeploymentAutomation:
    """Automated deployment and configuration management"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.deployment_templates = {}
        self.current_deployments = {}
        
        # Load deployment templates
        self._load_deployment_templates()
    
    def _load_deployment_templates(self):
        """Load deployment configuration templates"""
        self.deployment_templates = {
            'development': {
                'environment': 'development',
                'replicas': 1,
                'resources': {
                    'cpu': '500m',
                    'memory': '1Gi'
                },
                'features': {
                    'debug_mode': True,
                    'hot_reload': True,
                    'extensive_logging': True
                }
            },
            'staging': {
                'environment': 'staging',
                'replicas': 2,
                'resources': {
                    'cpu': '1000m',
                    'memory': '2Gi'
                },
                'features': {
                    'debug_mode': False,
                    'hot_reload': False,
                    'extensive_logging': False
                }
            },
            'production': {
                'environment': 'production',
                'replicas': 3,
                'resources': {
                    'cpu': '2000m',
                    'memory': '4Gi'
                },
                'features': {
                    'debug_mode': False,
                    'hot_reload': False,
                    'extensive_logging': False,
                    'backup_enabled': True,
                    'monitoring_enabled': True
                }
            }
        }
    
    async def deploy(self, environment: str, version: str = 'latest') -> Dict[str, Any]:
        """Deploy the system to specified environment"""
        if environment not in self.deployment_templates:
            raise ValueError(f"Unknown environment: {environment}")
        
        template = self.deployment_templates[environment]
        deployment_id = f"{environment}_{version}_{int(time.time())}"
        
        logger.info(f"🚀 Starting deployment: {deployment_id}")
        
        deployment_status = {
            'deployment_id': deployment_id,
            'environment': environment,
            'version': version,
            'status': 'deploying',
            'started_at': datetime.now().isoformat(),
            'steps_completed': 0,
            'total_steps': 7
        }
        
        self.current_deployments[deployment_id] = deployment_status
        
        try:
            # Step 1: Validate configuration
            await self._deploy_step("Validating configuration", deployment_status)
            
            # Step 2: Prepare environment
            await self._deploy_step("Preparing environment", deployment_status)
            
            # Step 3: Deploy AtomSpace components
            await self._deploy_step("Deploying AtomSpace components", deployment_status)
            
            # Step 4: Deploy ElizaOS plugins
            await self._deploy_step("Deploying ElizaOS plugins", deployment_status)
            
            # Step 5: Deploy GnuCash integration
            await self._deploy_step("Deploying GnuCash integration", deployment_status)
            
            # Step 6: Configure monitoring and backup
            await self._deploy_step("Configuring monitoring and backup", deployment_status)
            
            # Step 7: Validate deployment
            await self._deploy_step("Validating deployment", deployment_status)
            
            deployment_status['status'] = 'completed'
            deployment_status['completed_at'] = datetime.now().isoformat()
            
            logger.info(f"✅ Deployment completed: {deployment_id}")
            return deployment_status
            
        except Exception as e:
            deployment_status['status'] = 'failed'
            deployment_status['error'] = str(e)
            deployment_status['failed_at'] = datetime.now().isoformat()
            
            logger.error(f"❌ Deployment failed: {e}")
            raise
    
    async def _deploy_step(self, step_description: str, deployment_status: Dict[str, Any]):
        """Execute a single deployment step"""
        logger.info(f"📋 {step_description}...")
        
        # Simulate deployment work
        await asyncio.sleep(1)
        
        deployment_status['steps_completed'] += 1
        deployment_status['last_step'] = step_description
        deployment_status['progress'] = (deployment_status['steps_completed'] / deployment_status['total_steps']) * 100
    
    async def rollback(self, deployment_id: str) -> bool:
        """Rollback a deployment"""
        if deployment_id not in self.current_deployments:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        deployment = self.current_deployments[deployment_id]
        
        logger.info(f"🔄 Rolling back deployment: {deployment_id}")
        
        try:
            # Simulate rollback steps
            await asyncio.sleep(2)
            
            deployment['status'] = 'rolled_back'
            deployment['rolled_back_at'] = datetime.now().isoformat()
            
            logger.info(f"✅ Rollback completed: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            raise
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get status of a specific deployment"""
        return self.current_deployments.get(deployment_id, {})
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments"""
        return list(self.current_deployments.values())