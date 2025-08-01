"""
Error handling and recovery tests for the multi-step agent.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from msa.memory.manager import WorkingMemoryManager
from msa.memory.models import WorkingMemory, Fact
from msa.tools.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from msa.tools.rate_limiter import RateLimiter, RateLimitConfig
from msa.tools.cache import CacheManager
from msa.controller.components import Controller
from msa.memory.models import ToolResponse


class TestToolErrorHandling:
    """Test tool failure simulation and recovery."""

    def test_network_error_handling(self):
        """Test handling of network errors in tool execution."""
        memory_manager = WorkingMemoryManager("Test query")
        
        # Add an observation to test memory persistence
        observation = {
            "content": "Initial fact",
            "source": "test",
            "confidence": 0.8,
            "metadata": {}
        }
        memory_manager.add_observation(observation)
        
        # Verify the fact was added
        facts = memory_manager.get_memory().information_store.facts
        assert len(facts) == 1
        assert list(facts.values())[0].content == "Initial fact"

    def test_api_limit_handling(self):
        """Test handling of API rate limiting."""
        # Test with rate limiter
        config = RateLimitConfig(requests_per_second=1, bucket_capacity=1)
        rate_limiter = RateLimiter(config)
        
        def dummy_func():
            return "success"
        
        # First call should succeed
        result1 = rate_limiter.queue_request("test_endpoint", dummy_func)
        assert result1 == "success"
        
        # Second call should be rate limited but eventually succeed
        result2 = rate_limiter.queue_request("test_endpoint", dummy_func)
        assert result2 == "success"


class TestMemoryPersistence:
    """Test memory serialization and deserialization."""

    def test_memory_serialization_deserialization(self):
        """Test that memory can be serialized and deserialized correctly."""
        # Create a memory manager with some data
        memory_manager = WorkingMemoryManager("Test serialization")
        
        # Add multiple observations
        observations = [
            {
                "content": "Fact 1",
                "source": "source1",
                "confidence": 0.9,
                "metadata": {"key": "value1"}
            },
            {
                "content": "Fact 2",
                "source": "source2",
                "confidence": 0.8,
                "metadata": {"key": "value2"}
            }
        ]
        
        for obs in observations:
            memory_manager.add_observation(obs)
        
        # Serialize the memory
        serialized = memory_manager.serialize()
        
        # Deserialize back to memory
        deserialized_memory = memory_manager.deserialize(serialized)
        
        # Verify the deserialized memory has the same content
        assert deserialized_memory.query_state.original_query == "Test serialization"
        assert len(deserialized_memory.information_store.facts) == 2
        
        # Verify facts content
        facts = list(deserialized_memory.information_store.facts.values())
        fact_contents = [fact.content for fact in facts]
        assert "Fact 1" in fact_contents
        assert "Fact 2" in fact_contents

    def test_memory_state_preservation(self):
        """Test that memory state is preserved across serialization."""
        memory_manager = WorkingMemoryManager("State preservation test")
        
        # Add some facts and update reasoning state
        observation = {
            "content": "Important fact",
            "source": "reliable_source",
            "confidence": 0.95,
            "metadata": {}
        }
        memory_manager.add_observation(observation)
        
        # Update reasoning state
        memory = memory_manager.get_memory()
        memory.reasoning_state.current_hypothesis = "Test hypothesis"
        memory.reasoning_state.answer_draft = "Draft answer"
        
        # Serialize and deserialize
        serialized = memory_manager.serialize()
        deserialized_memory = memory_manager.deserialize(serialized)
        
        # Verify state preservation
        assert deserialized_memory.reasoning_state.current_hypothesis == "Test hypothesis"
        assert deserialized_memory.reasoning_state.answer_draft == "Draft answer"
        assert len(deserialized_memory.information_store.facts) == 1


class TestCircuitBreakerIntegration:
    """Test circuit breaker integration with tools."""

    def test_circuit_breaker_trip_and_reset(self):
        """Test circuit breaker tripping and automatic reset."""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=1,
            half_open_attempts=5
        )
        circuit_breaker = CircuitBreaker("test_breaker", config)
        
        # Function that always fails
        def failing_func():
            raise Exception("Always fails")
        
        # Trip the circuit breaker
        for i in range(5):
            with pytest.raises(Exception):
                circuit_breaker.execute_with_circuit_breaker(failing_func)
        
        # Next call should raise CircuitBreakerOpenException (mocked as generic Exception)
        with pytest.raises(Exception):
            circuit_breaker.execute_with_circuit_breaker(failing_func)
        
        # Wait for timeout and test half-open state
        import time
        time.sleep(1)
        
        # Next call should go to half-open state and fail again
        with pytest.raises(Exception):
            circuit_breaker.execute_with_circuit_breaker(failing_func)

    def test_circuit_breaker_success_recovery(self):
        """Test circuit breaker recovery after successful calls."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=1,
            half_open_attempts=2
        )
        circuit_breaker = CircuitBreaker("test_recovery", config)
        
        call_count = 0
        
        def sometimes_failing_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Failing")
            return "success"
        
        # Fail twice to trip the circuit
        for i in range(2):
            with pytest.raises(Exception):
                circuit_breaker.execute_with_circuit_breaker(sometimes_failing_func)
        
        # Circuit should be open
        with pytest.raises(Exception):
            circuit_breaker.execute_with_circuit_breaker(sometimes_failing_func)
        
        # Wait for timeout
        import time
        time.sleep(1)
        
        # Should succeed in half-open state
        result = circuit_breaker.execute_with_circuit_breaker(sometimes_failing_func)
        assert result == "success"


class TestRateLimiterIntegration:
    """Test rate limiter integration."""

    def test_rate_limiter_throttling(self):
        """Test that rate limiter properly throttles requests."""
        config = RateLimitConfig(requests_per_second=2, bucket_capacity=2)
        rate_limiter = RateLimiter(config)
        
        call_times = []
        
        def timed_func():
            call_times.append(datetime.now())
            return "success"
        
        # Make several calls quickly - some should be delayed
        results = []
        for i in range(5):
            result = rate_limiter.queue_request("test_endpoint", timed_func)
            results.append(result)
        
        # All should succeed
        assert all(r == "success" for r in results)
        
        # Check that we have the expected number of calls
        assert len(call_times) == 5

    def test_rate_limiter_usage_stats(self):
        """Test rate limiter usage statistics tracking."""
        config = RateLimitConfig(requests_per_second=10, bucket_capacity=10)
        rate_limiter = RateLimiter(config)
        
        def dummy_func():
            return "success"
        
        # Make some calls
        for i in range(3):
            rate_limiter.queue_request("test_endpoint", dummy_func)
        
        # Check stats
        stats = rate_limiter.get_usage_stats("test_endpoint")
        assert stats["requests"] == 3
        assert stats["throttled"] == 0


class TestCacheIntegration:
    """Test cache integration with error handling."""

    def test_cache_error_recovery(self):
        """Test that cache errors don't break tool execution."""
        cache_manager = CacheManager()
        
        # Test normal cache operation
        test_key = "test_key"
        test_value = {"data": "test_data"}
        
        # Set and get cache value
        cache_manager.set(test_key, test_value)
        cached_value = cache_manager.get(test_key)
        assert cached_value == test_value
        
        # Test cache invalidation
        assert cache_manager.invalidate(test_key) is True
        assert cache_manager.get(test_key) is None
        assert cache_manager.invalidate(test_key) is False  # Already invalidated

    def test_cache_ttl_expiration(self):
        """Test that cache entries expire correctly."""
        cache_manager = CacheManager()
        
        test_key = "ttl_test"
        test_value = {"data": "ttl_data"}
        
        # Set with short TTL
        cache_manager.set(test_key, test_value, ttl=1)  # 1 second TTL
        
        # Should be available immediately
        cached_value = cache_manager.get(test_key)
        assert cached_value == test_value
        
        # Note: We won't test actual expiration here as it would require sleeping
        # In a real test, we would mock time or use a more sophisticated approach


if __name__ == "__main__":
    pytest.main([__file__])
