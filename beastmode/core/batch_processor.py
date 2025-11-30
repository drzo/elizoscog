"""
Dynamic Batch Processor - Handles dynamic batching for optimal throughput
"""

import asyncio
import logging
from typing import List, Any, Optional
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """Batch processing configuration"""
    max_batch_size: int = 32
    max_wait_ms: int = 10  # Maximum wait time to accumulate requests
    min_batch_size: int = 1
    timeout_ms: int = 5000


class DynamicBatchProcessor:
    """
    Dynamic batch processor that intelligently groups requests
    to maximize throughput while minimizing latency.
    """
    
    def __init__(self, max_batch_size: int = 32, max_wait_ms: int = 10):
        self.config = BatchConfig(
            max_batch_size=max_batch_size,
            max_wait_ms=max_wait_ms
        )
        self.pending_requests: List[Any] = []
        self.lock = asyncio.Lock()
        
    async def add_request(self, request: Any) -> None:
        """Add request to batch"""
        async with self.lock:
            self.pending_requests.append(request)
    
    async def get_batch(self, timeout_s: float = 0.01) -> List[Any]:
        """
        Get a batch of requests, waiting up to timeout_s for more requests.
        
        Returns:
            List of requests ready for batch processing
        """
        start_time = time.time()
        batch = []
        
        while len(batch) < self.config.max_batch_size:
            async with self.lock:
                if self.pending_requests:
                    # Take requests up to max batch size
                    remaining = self.config.max_batch_size - len(batch)
                    batch.extend(self.pending_requests[:remaining])
                    self.pending_requests = self.pending_requests[remaining:]
            
            # Check if we should wait for more requests
            if len(batch) >= self.config.max_batch_size:
                break
            
            elapsed = time.time() - start_time
            if elapsed >= timeout_s:
                break
            
            # Small wait to accumulate more requests
            await asyncio.sleep(0.001)  # 1ms
        
        if batch:
            logger.debug(f"Created batch of size {len(batch)}")
        
        return batch
    
    async def clear_pending(self) -> List[Any]:
        """Clear and return all pending requests"""
        async with self.lock:
            requests = self.pending_requests.copy()
            self.pending_requests.clear()
            return requests
    
    def pending_count(self) -> int:
        """Get count of pending requests"""
        return len(self.pending_requests)
