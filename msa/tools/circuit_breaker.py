"""Circuit breaker pattern implementation for tool reliability."""

import logging
import time
from enum import Enum
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass

log = logging.getLogger(__name__)


class CircuitState(Enum):
    """Enumeration of circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_attempts: int = 3


class CircuitBreaker:
    """Implements the circuit breaker pattern for tool reliability."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None) -> None:
        """Initialize the circuit breaker.
        
        Args:
            name: Name of the circuit breaker for logging
            config: Configuration for circuit breaker behavior
        """
        _msg = f"CircuitBreaker.__init__ starting with name: {name}"
        log.debug(_msg)
        
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_success_count = 0
        
        _msg = "CircuitBreaker.__init__ returning"
        log.debug(_msg)
        
    def execute_with_circuit_breaker(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function execution
            
        Raises:
            Exception: If the circuit is open or the function fails
        """
        # Get function name safely for logging
        func_name = getattr(func, '__name__', str(func))
        _msg = f"CircuitBreaker.execute_with_circuit_breaker starting for function: {func_name}"
        log.debug(_msg)
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                _msg = f"Circuit breaker {self.name} is OPEN, rejecting call"
                log.warning(_msg)
                raise Exception(f"Circuit breaker {self.name} is OPEN")
                
        try:
            result = func(*args, **kwargs)
            self._on_success()
            _msg = f"CircuitBreaker.execute_with_circuit_breaker succeeded for function: {func_name}"
            log.debug(_msg)
            return result
        except Exception as e:
            self._on_failure()
            _msg = f"CircuitBreaker.execute_with_circuit_breaker failed for function: {func_name}: {str(e)}"
            log.warning(_msg)
            raise
            
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset.
        
        Returns:
            True if timeout has expired, False otherwise
        """
        _msg = "CircuitBreaker._should_attempt_reset starting"
        log.debug(_msg)
        
        if self.last_failure_time is None:
            _msg = "CircuitBreaker._should_attempt_reset returning False (no last failure time)"
            log.debug(_msg)
            return False
            
        result = time.time() - self.last_failure_time >= self.config.timeout_seconds
        _msg = f"CircuitBreaker._should_attempt_reset returning: {result}"
        log.debug(_msg)
        return result
        
    def _transition_to_half_open(self) -> None:
        """Transition the circuit breaker to half-open state."""
        _msg = "CircuitBreaker._transition_to_half_open starting"
        log.debug(_msg)
        
        self.state = CircuitState.HALF_OPEN
        self.half_open_success_count = 0
        
        _msg = "CircuitBreaker._transition_to_half_open returning"
        log.debug(_msg)
        
    def _on_success(self) -> None:
        """Handle successful execution."""
        _msg = "CircuitBreaker._on_success starting"
        log.debug(_msg)
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_success_count += 1
            if self.half_open_success_count >= self.config.half_open_attempts:
                self._reset()
        else:
            self._reset()
            
        _msg = "CircuitBreaker._on_success returning"
        log.debug(_msg)
            
    def _on_failure(self) -> None:
        """Handle failed execution."""
        _msg = "CircuitBreaker._on_failure starting"
        log.debug(_msg)
        
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self._trip()
        elif self.failure_count >= self.config.failure_threshold:
            self._trip()
            
        _msg = "CircuitBreaker._on_failure returning"
        log.debug(_msg)
            
    def _trip(self) -> None:
        """Trip the circuit breaker to open state."""
        _msg = "CircuitBreaker._trip starting"
        log.debug(_msg)
        
        self.state = CircuitState.OPEN
        _msg = f"Circuit breaker {self.name} TRIPPED to OPEN"
        log.warning(_msg)
        
        _msg = "CircuitBreaker._trip returning"
        log.debug(_msg)
        
    def _reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        _msg = "CircuitBreaker._reset starting"
        log.debug(_msg)
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_success_count = 0
        _msg = f"Circuit breaker {self.name} RESET to CLOSED"
        log.info(_msg)
        
        _msg = "CircuitBreaker._reset returning"
        log.debug(_msg)
        
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information for monitoring.
        
        Returns:
            Dictionary with state information
        """
        _msg = "CircuitBreaker.get_state_info starting"
        log.debug(_msg)
        
        result = {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "half_open_success_count": self.half_open_success_count
        }
        
        _msg = "CircuitBreaker.get_state_info returning"
        log.debug(_msg)
        return result
