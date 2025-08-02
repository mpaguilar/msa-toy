"""Cache manager for tool responses in the multi-step agent."""

import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from msa.config import load_app_config

log = logging.getLogger(__name__)


class CacheManager:
    """Manages caching operations for tool responses."""

    def __init__(self, cache_dir: str | None = None, default_ttl: int = 3600):
        """Initialize the cache manager.

        Args:
            cache_dir: Directory for persistent cache storage. If not provided, defaults to "msa/cache".
            default_ttl: Default time-to-live in seconds for cached entries. If not provided, defaults to 3600 seconds (1 hour).

        Returns:
            None

        Notes:
            1. Initializes the cache manager with the provided cache directory or defaults to "msa/cache".
            2. Creates the cache directory if it does not exist.
            3. Attempts to load application configuration from msa.config.load_app_config().
            4. If configuration is loaded, updates default_ttl with the value from the config under "cache.default_ttl".
            5. Logs initialization start and completion messages.

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
            key: Cache key used to generate the file path.

        Returns:
            Path object pointing to the file where the cache entry is stored.

        Notes:
            1. Takes the provided cache key and appends ".json" to form the file name.
            2. Constructs a Path object using the cache directory and the generated file name.
            3. Returns the constructed Path.

        """
        return self.cache_dir / f"{key}.json"

    def _is_expired(self, timestamp: float, ttl: int | None = None) -> bool:
        """Check if a cache entry is expired.

        Args:
            timestamp: The timestamp when the cache entry was created.
            ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

        Returns:
            True if the entry has expired, False otherwise.

        Notes:
            1. If ttl is None, uses the instance's default_ttl.
            2. Calculates the difference between the current time and the timestamp.
            3. Returns True if the difference exceeds the ttl, otherwise False.

        """
        if ttl is None:
            ttl = self.default_ttl
        return time.time() - timestamp > ttl

    def normalize_query(self, query: str) -> str:
        """Normalize a query string for consistent cache keys.

        Args:
            query: The query string to normalize.

        Returns:
            A normalized string suitable for use as a cache key, created by converting to lowercase, stripping whitespace, and hashing.

        Notes:
            1. Converts the input query to lowercase.
            2. Strips leading and trailing whitespace.
            3. Removes extra internal whitespace by splitting and rejoining with single spaces.
            4. Creates a hash of the normalized query using MD5.
            5. Returns the hexadecimal digest of the hash.

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

    def get(self, key: str, ttl: int | None = None) -> dict[str, Any] | None:
        """Retrieve an item from the cache.

        Args:
            key: Cache key used to locate the entry.
            ttl: Optional override for the time-to-live of this entry. If None, uses the default_ttl.

        Returns:
            The cached data (dict) if the entry exists and is not expired; otherwise, returns None.

        Notes:
            1. Constructs the file path for the cache entry using _get_cache_file_path.
            2. If the file does not exist, returns None.
            3. Tries to read the file and load the JSON content.
            4. Checks if the entry has expired using _is_expired.
            5. If expired, the file is deleted and None is returned.
            6. If not expired, the content from the cache entry is returned.
            7. If JSON decoding fails, the file is deleted and None is returned.

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
            with open(cache_file) as f:
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
        except json.JSONDecodeError as e:
            _msg = f"Error decoding JSON cache entry for key {key}: {e}"
            log.exception(_msg)
            try:
                cache_file.unlink()  # Remove corrupted entry
                _msg = f"Removed corrupted cache entry for key: {key}"
                log.debug(_msg)
            except Exception as unlink_error:
                _msg = f"Error removing corrupted cache entry for key {key}: {unlink_error}"
                log.exception(_msg)
            _msg = "CacheManager.get returning None"
            log.debug(_msg)
            return None
        except Exception as e:
            _msg = f"Error reading cache entry for key {key}: {e}"
            log.exception(_msg)
            _msg = "CacheManager.get returning None"
            log.debug(_msg)
            return None

    def set(self, key: str, value: dict[str, Any], ttl: int | None = None) -> None:
        """Store an item in the cache.

        Args:
            key: Cache key under which to store the data.
            value: Data to be cached, must be a dictionary.
            ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

        Returns:
            None

        Notes:
            1. If ttl is None, uses the instance's default_ttl.
            2. Constructs the file path using _get_cache_file_path.
            3. Creates a cache data dictionary containing the key, value, timestamp, and ttl.
            4. Converts any datetime objects in the value to ISO format strings for JSON serialization.
            5. Writes the cache data to the file in JSON format.
            6. If an error occurs during writing, logs the exception.

        """
        _msg = f"CacheManager.set starting with key: {key}"
        log.debug(_msg)

        if ttl is None:
            ttl = self.default_ttl

        cache_file = self._get_cache_file_path(key)

        # Convert datetime objects to ISO format strings for JSON serialization
        def convert_datetime(obj):
            if isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj

        cache_data = {
            "key": key,
            "content": convert_datetime(value),
            "timestamp": time.time(),
            "ttl": ttl,
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
            key: Cache key of the entry to remove.

        Returns:
            True if the entry was found and removed; otherwise, False.

        Notes:
            1. Constructs the file path using _get_cache_file_path.
            2. Checks if the file exists.
            3. If the file exists, attempts to delete it.
            4. If deletion succeeds, returns True.
            5. If the file does not exist or deletion fails, returns False.

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

    def warm_cache(
        self,
        key: str,
        value: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Pre-populate the cache with frequently accessed data.

        Args:
            key: Cache key under which to store the data.
            value: Data to be cached, must be a dictionary.
            ttl: Time-to-live in seconds for this entry. If None, uses the default_ttl.

        Returns:
            None

        Notes:
            1. Uses the set method to store the provided key-value pair in the cache.
            2. Logs the successful addition of the warm cache entry.

        """
        _msg = f"CacheManager.warm_cache starting with key: {key}"
        log.debug(_msg)

        self.set(key, value, ttl)
        _msg = f"Warm cache entry added for key: {key}"
        log.debug(_msg)

        _msg = "CacheManager.warm_cache returning"
        log.debug(_msg)
