"""Rate limiter implementation for the multi-step agent."""

import time
import logging
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting parameters."""
    requests_per_second: float
    bucket_capacity: int
    adaptive_throttling: bool = True


class RateLimiter:
    """Implements rate limiting using token bucket algorithm with adaptive throttling."""
    
    def __init__(self, config: RateLimitConfig) -> None:
        """Initialize the rate limiter with configuration.
        
        Args:
            config: RateLimitConfig with rate limiting parameters
        """
        _msg = "RateLimiter.__init__ starting"
        log.debug(_msg)
        
        self.config = config
        self.tokens: Dict[str, float] = {}
        self.last_refill: Dict[str, float] = {}
        self.usage_stats: Dict[str, Dict[str, int]] = {}
        
        _msg = "RateLimiter.__init__ returning"
        log.debug(_msg)
        
    def _refill_tokens(self, endpoint: str) -> None:
        """Refill tokens based on time elapsed since last refill.
        
        Args:
            endpoint: The endpoint identifier
        """
        _msg = f"RateLimiter._refill_tokens starting for endpoint: {endpoint}"
        log.debug(_msg)
        
        now = time.time()
        
        # If this is the first time using this endpoint, initialize it
        if endpoint not in self.last_refill:
            self.last_refill[endpoint] = now
            self.tokens[endpoint] = float(self.config.bucket_capacity)
            return
            
        time_elapsed = now - self.last_refill[endpoint]
        new_tokens = time_elapsed * self.config.requests_per_second
        self.tokens[endpoint] = min(
            float(self.config.bucket_capacity),
            self.tokens[endpoint] + new_tokens
        )
        self.last_refill[endpoint] = now
        
        _msg = f"RateLimiter._refill_tokens returning for endpoint: {endpoint}"
        log.debug(_msg)
        
    def _consume_token(self, endpoint: str) -> bool:
        """Consume a token if available.
        
        Args:
            endpoint: The endpoint identifier
            
        Returns:
            bool: True if token was consumed, False if rate limited
        """
        _msg = f"RateLimiter._consume_token starting for endpoint: {endpoint}"
        log.debug(_msg)
        
        # Initialize endpoint if it doesn't exist in usage_stats
        if endpoint not in self.usage_stats:
            self.usage_stats[endpoint] = {"requests": 0, "throttled": 0}
        
        # Initialize endpoint if it doesn't exist in tokens
        if endpoint not in self.tokens:
            self.tokens[endpoint] = float(self.config.bucket_capacity)
            self.last_refill[endpoint] = time.time()
        # If this is the first time using this endpoint, ensure it has full tokens
        elif endpoint not in self.last_refill:
            self.tokens[endpoint] = float(self.config.bucket_capacity)
            self.last_refill[endpoint] = time.time()
        
        self._refill_tokens(endpoint)
        
        if self.tokens[endpoint] >= 1.0:
            self.tokens[endpoint] -= 1.0
            self.usage_stats[endpoint]["requests"] += 1
            _msg = f"Token consumed for endpoint: {endpoint}"
            log.debug(_msg)
            _msg = "RateLimiter._consume_token returning True"
            log.debug(_msg)
            return True
        else:
            self.usage_stats[endpoint]["throttled"] += 1
            _msg = f"Rate limit exceeded for endpoint: {endpoint}"
            log.debug(_msg)
            _msg = "RateLimiter._consume_token returning False"
            log.debug(_msg)
            return False
            
    def queue_request(self, endpoint: str, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Queue a request and execute when rate limit allows.
        
        Args:
            endpoint: The endpoint identifier
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: The result of the function execution
        """
        _msg = f"RateLimiter.queue_request starting for endpoint: {endpoint}"
        log.debug(_msg)
        
        while not self._consume_token(endpoint):
            # Calculate sleep time based on when next token will be available
            sleep_time = 1.0 / self.config.requests_per_second
            _msg = f"Rate limit reached for {endpoint}, sleeping for {sleep_time:.2f}s"
            log.debug(_msg)
            time.sleep(sleep_time)
            
        _msg = f"RateLimiter.queue_request executing function for endpoint: {endpoint}"
        log.debug(_msg)
        result = func(*args, **kwargs)
        
        _msg = "RateLimiter.queue_request returning"
        log.debug(_msg)
        return result
        
    def get_usage_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics for endpoints.
        
        Args:
            endpoint: Specific endpoint to get stats for, or None for all
            
        Returns:
            Dict[str, Any]: Usage statistics
        """
        _msg = "RateLimiter.get_usage_stats starting"
        log.debug(_msg)
        
        if endpoint:
            # Return existing stats or default stats if endpoint doesn't exist
            result = self.usage_stats.get(endpoint, {"requests": 0, "throttled": 0})
            _msg = "RateLimiter.get_usage_stats returning specific endpoint stats"
            log.debug(_msg)
            return result
        result = dict(self.usage_stats)
        _msg = "RateLimiter.get_usage_stats returning all stats"
        log.debug(_msg)
        return result
        
    def reset_usage_stats(self) -> None:
        """Reset all usage statistics."""
        _msg = "RateLimiter.reset_usage_stats starting"
        log.debug(_msg)
        
        for stats in self.usage_stats.values():
            stats["requests"] = 0
            stats["throttled"] = 0
            
        _msg = "RateLimiter.reset_usage_stats returning"
        log.debug(_msg)
