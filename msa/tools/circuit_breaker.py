"""Circuit breaker pattern implementation for tool reliability."""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

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

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None) -> None:
        """Initialize the circuit breaker.

        Args:
            name: The name of the circuit breaker for logging and identification.
            config: Configuration for circuit breaker behavior, including failure threshold,
                    timeout duration, and number of half-open attempts.

        Notes:
            1. Initializes the circuit breaker with the given name and configuration.
            2. Sets the initial state to CLOSED.
            3. Initializes failure count to zero and last failure time to None.
            4. Initializes half-open success count to zero.

        """
        _msg = f"CircuitBreaker.__init__ starting with name: {name}"
        log.debug(_msg)

        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.half_open_success_count = 0

        _msg = "CircuitBreaker.__init__ returning"
        log.debug(_msg)

    def execute_with_circuit_breaker(
        self,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute a function with circuit breaker protection.

        Args:
            func: The function to execute. Must be callable and can accept variable arguments.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.

        Returns:
            The result of the function execution if successful.

        Raises:
            Exception: If the circuit breaker is in OPEN state and reset conditions are not met,
                       or if the function raises an exception during execution.

        Notes:
            1. Determines the function name for logging purposes.
            2. Checks if the circuit breaker is in OPEN state.
            3. If OPEN, attempts to transition to HALF_OPEN if sufficient time has passed.
            4. If unable to transition (too soon), raises an exception.
            5. Executes the function within a try block.
            6. On success, calls _on_success to handle the success state.
            7. On failure, calls _on_failure to handle the failure state and re-raises the exception.

        """
        # Get function name safely for logging
        func_name = getattr(func, "__name__", str(func))
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
            True if the timeout has expired since the last failure, False otherwise.

        Notes:
            1. Returns False if there is no recorded last failure time.
            2. Calculates the elapsed time since the last failure.
            3. Compares elapsed time to the configured timeout.
            4. Returns True if elapsed time exceeds timeout.

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
        """Transition the circuit breaker to half-open state.

        Notes:
            1. Sets the state to HALF_OPEN.
            2. Resets the success counter for half-open attempts to zero.

        """
        _msg = "CircuitBreaker._transition_to_half_open starting"
        log.debug(_msg)

        self.state = CircuitState.HALF_OPEN
        self.half_open_success_count = 0

        _msg = "CircuitBreaker._transition_to_half_open returning"
        log.debug(_msg)

    def _on_success(self) -> None:
        """Handle successful execution.

        Notes:
            1. Checks if the current state is HALF_OPEN.
            2. If HALF_OPEN, increments the success counter.
            3. If the success counter reaches the half-open threshold, resets the circuit.
            4. Otherwise, resets the circuit regardless of state.

        """
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
        """Handle failed execution.

        Notes:
            1. Increments the failure count.
            2. Records the current time as the last failure time.
            3. If in HALF_OPEN state, trips the circuit.
            4. If the failure count reaches the threshold, trips the circuit.

        """
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
        """Trip the circuit breaker to open state.

        Notes:
            1. Sets the state to OPEN.
            2. Logs a warning message indicating the circuit has been tripped.

        """
        _msg = "CircuitBreaker._trip starting"
        log.debug(_msg)

        self.state = CircuitState.OPEN
        _msg = f"Circuit breaker {self.name} TRIPPED to OPEN"
        log.warning(_msg)

        _msg = "CircuitBreaker._trip returning"
        log.debug(_msg)

    def _reset(self) -> None:
        """Reset the circuit breaker to closed state.

        Notes:
            1. Sets the state to CLOSED.
            2. Resets the failure count to zero.
            3. Clears the last failure time.
            4. Resets the half-open success count to zero.
            5. Logs an informational message indicating the reset.

        """
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

    def get_state_info(self) -> dict[str, Any]:
        """Get current state information for monitoring.

        Returns:
            A dictionary containing the circuit breaker's name, current state, failure count,
            last failure time, and half-open success count.

        Notes:
            1. Constructs a dictionary with the current state information.
            2. Includes the name, state, failure count, last failure time, and half-open success count.
            3. Returns the constructed dictionary.

        """
        _msg = "CircuitBreaker.get_state_info starting"
        log.debug(_msg)

        result = {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "half_open_success_count": self.half_open_success_count,
        }

        _msg = "CircuitBreaker.get_state_info returning"
        log.debug(_msg)
        return result
