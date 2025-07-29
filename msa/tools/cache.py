"""Cache manager for tool responses in the multi-step agent."""

import logging
import hashlib
import json
import time
from typing import Any, Dict, Optional
from pathlib import Path

from msa.config import load_app_config

log = logging.getLogger(__name__)


class CacheManager:
    """Manages caching operations for tool responses."""

    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 3600):
        """Initialize the cache manager.

        Args:
            cache_dir: Directory for persistent cache storage
            default_ttl: Default time-to-live in seconds
        """
        _msg = "CacheManager.__init__ starting"
        log.debug(_msg)
        
        self.default_ttl = default_ttl
        self.cache_dir = Path(cache_dir) if cache_dir else Path("msa/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cache configuration
        try:
            config = load_app_config()
            cache_config = config.get("cache", {})
            self.default_ttl = cache_config.get("default_ttl", default_ttl)
        except Exception as e:
            _msg = f"Could not load cache configuration: {e}"
            log.warning(_msg)

        _msg = "CacheManager.__init__ returning"
        log.debug(_msg)

    def _get_cache_file_path(self, key: str) -> Path:
        """Get the file path for a cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Path to the cache file
        """
        return self.cache_dir / f"{key}.json"

    def _is_expired(self, timestamp: float, ttl: Optional[int] = None) -> bool:
        """Check if a cache entry is expired.
        
        Args:
            timestamp: Creation timestamp
            ttl: Time-to-live in seconds, uses default if None
            
        Returns:
            True if expired, False otherwise
        """
        if ttl is None:
            ttl = self.default_ttl
        return time.time() - timestamp > ttl

    def normalize_query(self, query: str) -> str:
        """Normalize a query string for consistent cache keys.
        
        Args:
            query: The query string to normalize
            
        Returns:
            Normalized query string suitable for use as a cache key
        """
        _msg = f"CacheManager.normalize_query starting with query: {query}"
        log.debug(_msg)
        
        # Convert to lowercase and strip whitespace
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        
        # Create a hash of the normalized query for consistent key length
        query_hash = hashlib.md5(normalized.encode()).hexdigest()
        
        _msg = f"CacheManager.normalize_query returning: {query_hash}"
        log.debug(_msg)
        return query_hash

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Retrieve an item from the cache.
        
        Args:
            key: Cache key
            ttl: Time-to-live override for this entry
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        _msg = f"CacheManager.get starting with key: {key}"
        log.debug(_msg)
        
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            _msg = f"Cache miss for key: {key}"
            log.debug(_msg)
            _msg = "CacheManager.get returning None"
            log.debug(_msg)
            return None
            
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                
            if self._is_expired(data["timestamp"], ttl):
                _msg = f"Cache entry expired for key: {key}"
                log.debug(_msg)
                cache_file.unlink()  # Remove expired entry
                _msg = "CacheManager.get returning None"
                log.debug(_msg)
                return None
                
            _msg = f"Cache hit for key: {key}"
            log.debug(_msg)
            _msg = "CacheManager.get returning cached data"
            log.debug(_msg)
            return data["content"]
        except Exception as e:
            _msg = f"Error reading cache entry for key {key}: {e}"
            log.exception(_msg)
            _msg = "CacheManager.get returning None"
            log.debug(_msg)
            return None

    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Store an item in the cache.
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time-to-live in seconds, uses default if None
        """
        _msg = f"CacheManager.set starting with key: {key}"
        log.debug(_msg)
        
        if ttl is None:
            ttl = self.default_ttl
            
        cache_file = self._get_cache_file_path(key)
        
        cache_data = {
            "key": key,
            "content": value,
            "timestamp": time.time(),
            "ttl": ttl
        }
        
        try:
            with open(cache_file, "w") as f:
                json.dump(cache_data, f)
            _msg = f"Stored cache entry for key: {key}"
            log.debug(_msg)
        except Exception as e:
            _msg = f"Error storing cache entry for key {key}: {e}"
            log.exception(_msg)

        _msg = "CacheManager.set returning"
        log.debug(_msg)

    def invalidate(self, key: str) -> bool:
        """Remove an item from the cache.
        
        Args:
            key: Cache key to remove
            
        Returns:
            True if item was removed, False if not found
        """
        _msg = f"CacheManager.invalidate starting with key: {key}"
        log.debug(_msg)
        
        cache_file = self._get_cache_file_path(key)
        
        if cache_file.exists():
            try:
                cache_file.unlink()
                _msg = f"Invalidated cache entry for key: {key}"
                log.debug(_msg)
                _msg = "CacheManager.invalidate returning True"
                log.debug(_msg)
                return True
            except Exception as e:
                _msg = f"Error invalidating cache entry for key {key}: {e}"
                log.exception(_msg)
                _msg = "CacheManager.invalidate returning False"
                log.debug(_msg)
                return False
        else:
            _msg = f"Cache entry not found for invalidation: {key}"
            log.debug(_msg)
            _msg = "CacheManager.invalidate returning False"
            log.debug(_msg)
            return False

    def warm_cache(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Pre-populate the cache with frequently accessed data.
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time-to-live in seconds, uses default if None
        """
        _msg = f"CacheManager.warm_cache starting with key: {key}"
        log.debug(_msg)
        
        self.set(key, value, ttl)
        _msg = f"Warm cache entry added for key: {key}"
        log.debug(_msg)
        
        _msg = "CacheManager.warm_cache returning"
        log.debug(_msg)
