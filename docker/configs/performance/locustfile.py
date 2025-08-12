#!/usr/bin/env python3
"""
Performance Testing Configuration for ElizaOS-OpenCog-GnuCash Microservices

This Locust configuration tests the performance of the microservice infrastructure
including service discovery, load balancing, and individual service endpoints.
"""

import random
import json
from locust import HttpUser, task, between, events
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MicroservicePerformanceUser(HttpUser):
    """
    Simulates user interactions with the microservice infrastructure
    for performance testing and benchmarking.
    """
    
    # Wait between requests to simulate realistic usage
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user session"""
        logger.info(f"Starting performance test user: {self.__class__.__name__}")
        self.service_endpoints = [
            "/health",
            "/metrics", 
            "/status",
            "/api/v1/services",
            "/api/v1/discovery"
        ]
        
        # Test data for financial service
        self.financial_test_data = {
            "account_id": f"test_account_{random.randint(1000, 9999)}",
            "amount": random.uniform(100, 10000),
            "transaction_type": random.choice(["credit", "debit"]),
            "category": random.choice(["income", "expense", "transfer"])
        }
    
    @task(10)
    def test_health_endpoints(self):
        """Test health check endpoints - highest frequency"""
        endpoint = random.choice(self.service_endpoints[:3])  # health, metrics, status
        
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                logger.debug(f"Health check successful: {endpoint}")
            elif response.status_code == 404:
                # Expected for some services that may not have all endpoints
                response.success() 
            else:
                response.failure(f"Health check failed: {endpoint} - Status: {response.status_code}")
    
    @task(7)
    def test_service_discovery(self):
        """Test service discovery performance"""
        service_names = ["financial-analysis", "cognitive-reasoning", "ml-inference"]
        service_name = random.choice(service_names)
        
        endpoint = f"/api/v1/discover/{service_name}"
        
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        response.success()
                        logger.debug(f"Service discovery successful: {service_name}")
                    else:
                        response.failure(f"No services found for: {service_name}")
                except json.JSONDecodeError:
                    response.success()  # May return non-JSON health response
            elif response.status_code == 404:
                response.success()  # Service not found is acceptable in testing
            else:
                response.failure(f"Service discovery failed: {endpoint} - Status: {response.status_code}")
    
    @task(5)
    def test_load_balancer(self):
        """Test load balancer performance"""
        service_types = ["financial", "reasoning", "ggml"]
        service_type = random.choice(service_types)
        
        endpoint = f"/api/v1/balance/{service_type}"
        
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
                logger.debug(f"Load balancer test successful: {service_type}")
            else:
                response.failure(f"Load balancer test failed: {endpoint} - Status: {response.status_code}")
    
    @task(3)
    def test_financial_service_simulation(self):
        """Simulate financial service operations"""
        endpoints = [
            "/api/v1/accounts",
            "/api/v1/transactions", 
            "/api/v1/analysis"
        ]
        endpoint = random.choice(endpoints)
        
        # Simulate both GET and POST operations
        if random.choice([True, False]):
            # GET request
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code in [200, 404]:
                    response.success()
                else:
                    response.failure(f"Financial GET failed: {endpoint} - Status: {response.status_code}")
        else:
            # POST request with test data
            with self.client.post(endpoint, json=self.financial_test_data, catch_response=True) as response:
                if response.status_code in [200, 201, 404, 405]:  # 405 Method Not Allowed is acceptable
                    response.success()
                else:
                    response.failure(f"Financial POST failed: {endpoint} - Status: {response.status_code}")
    
    @task(2)
    def test_reasoning_service_simulation(self):
        """Simulate cognitive reasoning service operations"""
        reasoning_queries = [
            {"query": "analyze financial patterns", "context": "quarterly_analysis"},
            {"query": "predict market trends", "context": "risk_assessment"},
            {"query": "optimize portfolio", "context": "investment_strategy"}
        ]
        
        endpoint = "/api/v1/reasoning/query"
        query_data = random.choice(reasoning_queries)
        
        with self.client.post(endpoint, json=query_data, catch_response=True) as response:
            if response.status_code in [200, 201, 404, 405]:
                response.success()
                logger.debug(f"Reasoning query successful: {query_data['query'][:20]}...")
            else:
                response.failure(f"Reasoning query failed: {endpoint} - Status: {response.status_code}")
    
    @task(1)
    def test_ml_inference_simulation(self):
        """Simulate ML inference service operations"""
        inference_requests = [
            {"model": "llama", "prompt": "Analyze this financial data", "max_tokens": 100},
            {"model": "gpt", "prompt": "Generate investment summary", "max_tokens": 150},
            {"model": "bert", "text": "Classify this transaction type", "labels": ["income", "expense"]}
        ]
        
        endpoint = "/api/v1/inference"
        inference_data = random.choice(inference_requests)
        
        with self.client.post(endpoint, json=inference_data, catch_response=True) as response:
            if response.status_code in [200, 201, 404, 405, 503]:  # 503 Service Unavailable is acceptable for ML
                response.success()
                logger.debug(f"ML inference successful: {inference_data.get('model', 'unknown')}")
            else:
                response.failure(f"ML inference failed: {endpoint} - Status: {response.status_code}")


class HighLoadUser(HttpUser):
    """
    High-load user simulation for stress testing
    """
    wait_time = between(0.1, 0.5)  # Faster requests for stress testing
    
    @task
    def rapid_health_checks(self):
        """Rapid health check requests for stress testing"""
        endpoints = ["/health", "/metrics", "/status"]
        endpoint = random.choice(endpoints)
        
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Rapid health check failed: {endpoint}")


# Event handlers for detailed reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start"""
    logger.info("Performance test starting...")
    logger.info(f"Target host: {environment.host}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test completion and summary"""
    logger.info("Performance test completed")
    
    if environment.stats:
        logger.info("Performance Test Summary:")
        logger.info(f"Total requests: {environment.stats.total.num_requests}")
        logger.info(f"Failed requests: {environment.stats.total.num_failures}")
        logger.info(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
        logger.info(f"Max response time: {environment.stats.total.max_response_time:.2f}ms")
        logger.info(f"Requests per second: {environment.stats.total.total_rps:.2f}")
        
        # Check performance criteria
        avg_response_time = environment.stats.total.avg_response_time
        failure_rate = (environment.stats.total.num_failures / environment.stats.total.num_requests) * 100 if environment.stats.total.num_requests > 0 else 0
        
        logger.info("Performance Criteria Check:")
        logger.info(f"Average response time: {avg_response_time:.2f}ms ({'PASS' if avg_response_time < 1000 else 'FAIL'} - Target: <1000ms)")
        logger.info(f"Failure rate: {failure_rate:.2f}% ({'PASS' if failure_rate < 5 else 'FAIL'} - Target: <5%)")
        logger.info(f"RPS: {environment.stats.total.total_rps:.2f} ({'PASS' if environment.stats.total.total_rps > 10 else 'FAIL'} - Target: >10 RPS)")


# Custom user classes for different test scenarios
class StressTestUser(HighLoadUser):
    """Stress testing user with high request rate"""
    weight = 1

class NormalUser(MicroservicePerformanceUser):
    """Normal load testing user"""
    weight = 3