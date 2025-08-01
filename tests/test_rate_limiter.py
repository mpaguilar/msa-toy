"""Unit tests for the rate limiter implementation."""

import time

from msa.tools.rate_limiter import RateLimiter, RateLimitConfig


def test_rate_limiter_initialization():
    """Test RateLimiter initialization."""
    _msg = "test_rate_limiter_initialization starting"
    print(_msg)

    config = RateLimitConfig(requests_per_second=1.0, bucket_capacity=5)
    limiter = RateLimiter(config)

    assert limiter.config == config
    assert limiter.tokens == {}
    assert limiter.last_refill == {}

    _msg = "test_rate_limiter_initialization returning"
    print(_msg)


def test_token_consumption():
    """Test token consumption functionality."""
    _msg = "test_token_consumption starting"
    print(_msg)

    config = RateLimitConfig(requests_per_second=1.0, bucket_capacity=5)
    limiter = RateLimiter(config)

    # Should be able to consume tokens initially
    result = limiter._consume_token("test_endpoint")
    assert result is True

    # Check usage stats
    stats = limiter.get_usage_stats("test_endpoint")
    assert stats["requests"] == 1
    assert stats["throttled"] == 0

    _msg = "test_token_consumption returning"
    print(_msg)


def test_rate_limiting():
    """Test rate limiting when no tokens available."""
    _msg = "test_rate_limiting starting"
    print(_msg)

    config = RateLimitConfig(
        requests_per_second=0.0,
        bucket_capacity=1,
    )  # No refill rate
    limiter = RateLimiter(config)

    # Consume the only available token
    result1 = limiter._consume_token("test_endpoint")
    assert result1 is True

    # Next request should be rate limited (no refill with 0.0 rate)
    result2 = limiter._consume_token("test_endpoint")
    assert result2 is False

    # Check usage stats
    stats = limiter.get_usage_stats("test_endpoint")
    assert stats["requests"] == 1
    assert stats["throttled"] == 1

    _msg = "test_rate_limiting returning"
    print(_msg)


def test_token_refill():
    """Test token refilling over time."""
    _msg = "test_token_refill starting"
    print(_msg)

    config = RateLimitConfig(requests_per_second=10.0, bucket_capacity=1)
    limiter = RateLimiter(config)

    # Consume the only available token
    limiter._consume_token("test_endpoint")

    # Wait for token to refill
    time.sleep(0.2)  # Should refill ~2 tokens

    # Should be able to consume again
    result = limiter._consume_token("test_endpoint")
    assert result is True

    _msg = "test_token_refill returning"
    print(_msg)


def test_queue_request():
    """Test queued request execution."""
    _msg = "test_queue_request starting"
    print(_msg)

    config = RateLimitConfig(requests_per_second=10.0, bucket_capacity=1)
    limiter = RateLimiter(config)

    # Simple test function
    def test_func(x: int, y: int) -> int:
        return x + y

    # Queue a request
    result = limiter.queue_request("test_endpoint", test_func, 2, 3)
    assert result == 5

    _msg = "test_queue_request returning"
    print(_msg)


def test_usage_stats():
    """Test usage statistics tracking."""
    _msg = "test_usage_stats starting"
    print(_msg)

    config = RateLimitConfig(requests_per_second=1.0, bucket_capacity=5)
    limiter = RateLimiter(config)

    # Make some requests
    result1 = limiter._consume_token("endpoint1")
    result2 = limiter._consume_token("endpoint1")
    result3 = limiter._consume_token("endpoint2")

    assert result1 is True  # First request should succeed
    assert (
        result2 is True
    )  # Second request should also succeed with higher bucket capacity
    assert result3 is True  # Third request should succeed

    # Check specific endpoint stats
    stats1 = limiter.get_usage_stats("endpoint1")
    assert stats1["requests"] == 2
    assert stats1["throttled"] == 0

    # Check all stats
    all_stats = limiter.get_usage_stats()
    assert "endpoint1" in all_stats
    assert "endpoint2" in all_stats

    _msg = "test_usage_stats returning"
    print(_msg)


def test_reset_usage_stats():
    """Test resetting usage statistics."""
    _msg = "test_reset_usage_stats starting"
    print(_msg)

    config = RateLimitConfig(requests_per_second=1.0, bucket_capacity=1)
    limiter = RateLimiter(config)

    # Make some requests
    limiter._consume_token("test_endpoint")
    limiter._consume_token("test_endpoint")

    # Reset stats
    limiter.reset_usage_stats()

    # Check stats are reset
    stats = limiter.get_usage_stats("test_endpoint")
    assert stats["requests"] == 0
    assert stats["throttled"] == 0

    _msg = "test_reset_usage_stats returning"
    print(_msg)
