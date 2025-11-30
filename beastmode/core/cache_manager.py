"""
Inference Cache Manager - Intelligent caching for inference results
"""

import logging
from typing import Any, Optional, Dict
from dataclasses import dataclass
import time
from collections import OrderedDict
import sys

# Try to import numpy at module level for efficiency
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    size_bytes: int
    timestamp: float
    hit_count: int = 0
    last_access: float = 0.0


class InferenceCache:
    """
    LRU cache with size limits for inference results.
    
    Features:
    - Size-based eviction (in MB)
    - LRU eviction policy
    - Hit rate tracking
    - TTL support
    """
    
    def __init__(self, max_size_mb: int = 1024, ttl_seconds: Optional[int] = None):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_size_bytes = 0
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Check TTL
        if self.ttl_seconds:
            age = time.time() - entry.timestamp
            if age > self.ttl_seconds:
                # Expired
                self.remove(key)
                self.misses += 1
                return None
        
        # Update access info
        entry.hit_count += 1
        entry.last_access = time.time()
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        
        self.hits += 1
        return entry.value
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache"""
        # Calculate size
        size_bytes = self._estimate_size(value)
        
        # Check if value is too large for cache
        if size_bytes > self.max_size_bytes:
            logger.warning(f"Value too large for cache: {size_bytes} bytes")
            return
        
        # Remove existing entry if present
        if key in self.cache:
            self.remove(key)
        
        # Evict entries if needed
        while self.current_size_bytes + size_bytes > self.max_size_bytes:
            if not self.cache:
                break
            self._evict_lru()
        
        # Add new entry
        entry = CacheEntry(
            key=key,
            value=value,
            size_bytes=size_bytes,
            timestamp=time.time(),
            last_access=time.time()
        )
        
        self.cache[key] = entry
        self.current_size_bytes += size_bytes
        
        logger.debug(f"Cached entry {key}: {size_bytes} bytes")
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache"""
        if key in self.cache:
            entry = self.cache.pop(key)
            self.current_size_bytes -= entry.size_bytes
            return True
        return False
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Pop from beginning (least recently used)
        key, entry = self.cache.popitem(last=False)
        self.current_size_bytes -= entry.size_bytes
        self.evictions += 1
        
        logger.debug(f"Evicted LRU entry {key}: {entry.size_bytes} bytes")
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimate size of object in bytes"""
        # Use sys.getsizeof as rough estimate
        # For numpy arrays, use nbytes
        if NUMPY_AVAILABLE and isinstance(obj, np.ndarray):
            return obj.nbytes
        
        return sys.getsizeof(obj)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.current_size_bytes = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'size_mb': self.current_size_bytes / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'entries': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'utilization': self.current_size_bytes / self.max_size_bytes if self.max_size_bytes > 0 else 0.0
        }
