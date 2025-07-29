"""Unit tests for the circuit breaker pattern implementation."""

import time
import pytest
from unittest.mock import Mock, patch

from msa.tools.circuit_breaker import (
    CircuitBreaker, 
    CircuitBreakerConfig, 
    CircuitState
)


def test_circuit_breaker_initialization():
    """Test circuit breaker initialization with default config."""
    _msg = "test_circuit_breaker_initialization starting"
    print(_msg)
    
    cb = CircuitBreaker("test_breaker")
    
    assert cb.name == "test_breaker"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0
    assert cb.last_failure_time is None
    assert cb.half_open_success_count == 0
    assert isinstance(cb.config, CircuitBreakerConfig)
    assert cb.config.failure_threshold == 5
    assert cb.config.timeout_seconds == 60
    assert cb.config.half_open_attempts == 3
    
    _msg = "test_circuit_breaker_initialization returning"
    print(_msg)


def test_circuit_breaker_initialization_with_custom_config():
    """Test circuit breaker initialization with custom config."""
    _msg = "test_circuit_breaker_initialization_with_custom_config starting"
    print(_msg)
    
    config = CircuitBreakerConfig(
        failure_threshold=3,
        timeout_seconds=30,
        half_open_attempts=2
    )
    cb = CircuitBreaker("test_breaker", config)
    
    assert cb.name == "test_breaker"
    assert cb.config.failure_threshold == 3
    assert cb.config.timeout_seconds == 30
    assert cb.config.half_open_attempts == 2
    
    _msg = "test_circuit_breaker_initialization_with_custom_config returning"
    print(_msg)


def test_successful_execution():
    """Test successful function execution through circuit breaker."""
    _msg = "test_successful_execution starting"
    print(_msg)
    
    cb = CircuitBreaker("test_breaker")
    mock_func = Mock(return_value="success_result")
    
    result = cb.execute_with_circuit_breaker(mock_func, "arg1", kwarg1="value1")
    
    assert result == "success_result"
    mock_func.assert_called_once_with("arg1", kwarg1="value1")
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0
    
    _msg = "test_successful_execution returning"
    print(_msg)


def test_failed_execution():
    """Test failed function execution through circuit breaker."""
    _msg = "test_failed_execution starting"
    print(_msg)
    
    cb = CircuitBreaker("test_breaker")
    mock_func = Mock(side_effect=Exception("test failure"))
    
    with pytest.raises(Exception, match="test failure"):
        cb.execute_with_circuit_breaker(mock_func)
    
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 1
    assert cb.last_failure_time is not None
    
    _msg = "test_failed_execution returning"
    print(_msg)


def test_circuit_tripping():
    """Test circuit breaker tripping after failure threshold."""
    _msg = "test_circuit_tripping starting"
    print(_msg)
    
    config = CircuitBreakerConfig(failure_threshold=3)
    cb = CircuitBreaker("test_breaker", config)
    mock_func = Mock(side_effect=Exception("test failure"))
    
    # Fail threshold-1 times
    for i in range(2):
        with pytest.raises(Exception):
            cb.execute_with_circuit_breaker(mock_func)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == i + 1
    
    # Fail threshold times to trip circuit
    with pytest.raises(Exception):
        cb.execute_with_circuit_breaker(mock_func)
    
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 3
    
    _msg = "test_circuit_tripping returning"
    print(_msg)


def test_circuit_rejection_in_open_state():
    """Test that calls are rejected when circuit is open."""
    _msg = "test_circuit_rejection_in_open_state starting"
    print(_msg)
    
    cb = CircuitBreaker("test_breaker")
    cb.state = CircuitState.OPEN
    mock_func = Mock(return_value="success_result")
    
    with pytest.raises(Exception, match="Circuit breaker test_breaker is OPEN"):
        cb.execute_with_circuit_breaker(mock_func)
    
    mock_func.assert_not_called()
    
    _msg = "test_circuit_rejection_in_open_state returning"
    print(_msg)


@patch('time.time')
def test_circuit_reset_after_timeout(mock_time):
    """Test circuit reset after timeout period."""
    _msg = "test_circuit_reset_after_timeout starting"
    print(_msg)
    
    config = CircuitBreakerConfig(timeout_seconds=60)
    cb = CircuitBreaker("test_breaker", config)
    cb.state = CircuitState.OPEN
    cb.last_failure_time = 1000.0  # Set a fixed time
    
    # Mock time to simulate timeout expiration
    mock_time.return_value = 1061.0  # 61 seconds later
    
    mock_func = Mock(return_value="success_result")
    
    # Should transition to half-open and then execute
    result = cb.execute_with_circuit_breaker(mock_func)
    
    assert result == "success_result"
    assert cb.state == CircuitState.HALF_OPEN
    mock_func.assert_called_once()
    
    _msg = "test_circuit_reset_after_timeout returning"
    print(_msg)


def test_half_open_success():
    """Test successful executions in half-open state."""
    _msg = "test_half_open_success starting"
    print(_msg)
    
    config = CircuitBreakerConfig(half_open_attempts=2)
    cb = CircuitBreaker("test_breaker", config)
    cb.state = CircuitState.HALF_OPEN
    cb.half_open_success_count = 0
    mock_func = Mock(return_value="success_result")
    
    # First success in half-open
    result = cb.execute_with_circuit_breaker(mock_func)
    assert result == "success_result"
    assert cb.state == CircuitState.HALF_OPEN
    assert cb.half_open_success_count == 1
    
    # Second success resets circuit
    result = cb.execute_with_circuit_breaker(mock_func)
    assert result == "success_result"
    assert cb.state == CircuitState.CLOSED
    assert cb.half_open_success_count == 0
    assert cb.failure_count == 0
    
    _msg = "test_half_open_success returning"
    print(_msg)


def test_half_open_failure():
    """Test failure in half-open state trips circuit again."""
    _msg = "test_half_open_failure starting"
    print(_msg)
    
    cb = CircuitBreaker("test_breaker")
    cb.state = CircuitState.HALF_OPEN
    cb.half_open_success_count = 1
    mock_func = Mock(side_effect=Exception("test failure"))
    
    with pytest.raises(Exception):
        cb.execute_with_circuit_breaker(mock_func)
    
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 1
    
    _msg = "test_half_open_failure returning"
    print(_msg)


def test_should_attempt_reset():
    """Test timeout checking logic."""
    _msg = "test_should_attempt_reset starting"
    print(_msg)
    
    config = CircuitBreakerConfig(timeout_seconds=60)
    cb = CircuitBreaker("test_breaker", config)
    
    # No failure time set
    assert cb._should_attempt_reset() is False
    
    # Time not expired
    cb.last_failure_time = time.time() - 30
    assert cb._should_attempt_reset() is False
    
    # Time expired
    cb.last_failure_time = time.time() - 61
    assert cb._should_attempt_reset() is True
    
    _msg = "test_should_attempt_reset returning"
    print(_msg)


def test_get_state_info():
    """Test state information retrieval."""
    _msg = "test_get_state_info starting"
    print(_msg)
    
    cb = CircuitBreaker("test_breaker")
    cb.state = CircuitState.OPEN
    cb.failure_count = 2
    cb.last_failure_time = 1234567890.0
    cb.half_open_success_count = 1
    
    info = cb.get_state_info()
    
    assert info["name"] == "test_breaker"
    assert info["state"] == "open"
    assert info["failure_count"] == 2
    assert info["last_failure_time"] == 1234567890.0
    assert info["half_open_success_count"] == 1
    
    _msg = "test_get_state_info returning"
    print(_msg)
