"""Unit tests for the cache manager."""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from msa.tools.cache import CacheManager


def test_cache_manager_initialization():
    """Test CacheManager initialization with default values."""
    _msg = "test_cache_manager_initialization starting"
    print(_msg)
    
    cache_manager = CacheManager()
    assert cache_manager.default_ttl == 3600
    assert cache_manager.cache_dir.exists()
    
    _msg = "test_cache_manager_initialization returning"
    print(_msg)


def test_cache_manager_initialization_with_custom_values():
    """Test CacheManager initialization with custom values."""
    _msg = "test_cache_manager_initialization_with_custom_values starting"
    print(_msg)
    
    cache_manager = CacheManager(cache_dir="/tmp/test_cache", default_ttl=1800)
    assert cache_manager.default_ttl == 1800
    assert str(cache_manager.cache_dir) == "/tmp/test_cache"
    
    _msg = "test_cache_manager_initialization_with_custom_values returning"
    print(_msg)


def test_normalize_query():
    """Test query normalization."""
    _msg = "test_normalize_query starting"
    print(_msg)
    
    cache_manager = CacheManager()
    
    # Test basic normalization
    key1 = cache_manager.normalize_query("What is the capital of France?")
    key2 = cache_manager.normalize_query("what is the capital of france?  ")
    assert key1 == key2  # Should be the same after normalization
    
    # Test different queries produce different keys
    key3 = cache_manager.normalize_query("What is the capital of Germany?")
    assert key1 != key3
    
    _msg = "test_normalize_query returning"
    print(_msg)


def test_is_expired():
    """Test expiration checking."""
    _msg = "test_is_expired starting"
    print(_msg)
    
    cache_manager = CacheManager()
    
    # Test not expired
    assert not cache_manager._is_expired(time.time(), 3600)
    
    # Test expired
    assert cache_manager._is_expired(time.time() - 3601, 3600)
    
    _msg = "test_is_expired returning"
    print(_msg)


@patch("pathlib.Path.exists")
@patch("builtins.open", new_callable=mock_open, read_data='{"timestamp": 0, "content": {"test": "data"}}')
def test_get_expired_entry(mock_file, mock_exists):
    """Test getting an expired cache entry."""
    _msg = "test_get_expired_entry starting"
    print(_msg)
    
    mock_exists.return_value = True
    cache_manager = CacheManager()
    
    result = cache_manager.get("test_key")
    assert result is None
    
    _msg = "test_get_expired_entry returning"
    print(_msg)


@patch("pathlib.Path.exists")
@patch("builtins.open", new_callable=mock_open, read_data='{"timestamp": 10000000000, "content": {"test": "data"}}')
def test_get_valid_entry(mock_file, mock_exists):
    """Test getting a valid cache entry."""
    _msg = "test_get_valid_entry starting"
    print(_msg)
    
    mock_exists.return_value = True
    cache_manager = CacheManager()
    
    result = cache_manager.get("test_key")
    assert result == {"test": "data"}
    
    _msg = "test_get_valid_entry returning"
    print(_msg)


@patch("pathlib.Path.exists")
def test_get_nonexistent_entry(mock_exists):
    """Test getting a nonexistent cache entry."""
    _msg = "test_get_nonexistent_entry starting"
    print(_msg)
    
    mock_exists.return_value = False
    cache_manager = CacheManager()
    
    result = cache_manager.get("test_key")
    assert result is None
    
    _msg = "test_get_nonexistent_entry returning"
    print(_msg)


@patch("builtins.open", new_callable=mock_open)
def test_set_entry(mock_file):
    """Test setting a cache entry."""
    _msg = "test_set_entry starting"
    print(_msg)
    
    cache_manager = CacheManager()
    test_data = {"result": "test data"}
    
    cache_manager.set("test_key", test_data)
    
    # Verify file was written
    mock_file.assert_called()
    
    _msg = "test_set_entry returning"
    print(_msg)


@patch("pathlib.Path.exists")
@patch("pathlib.Path.unlink")
def test_invalidate_existing_entry(mock_unlink, mock_exists):
    """Test invalidating an existing cache entry."""
    _msg = "test_invalidate_existing_entry starting"
    print(_msg)
    
    mock_exists.return_value = True
    cache_manager = CacheManager()
    
    result = cache_manager.invalidate("test_key")
    assert result is True
    mock_unlink.assert_called_once()
    
    _msg = "test_invalidate_existing_entry returning"
    print(_msg)


@patch("pathlib.Path.exists")
def test_invalidate_nonexistent_entry(mock_exists):
    """Test invalidating a nonexistent cache entry."""
    _msg = "test_invalidate_nonexistent_entry starting"
    print(_msg)
    
    mock_exists.return_value = False
    cache_manager = CacheManager()
    
    result = cache_manager.invalidate("test_key")
    assert result is False
    
    _msg = "test_invalidate_nonexistent_entry returning"
    print(_msg)


def test_warm_cache():
    """Test warming the cache."""
    _msg = "test_warm_cache starting"
    print(_msg)
    
    cache_manager = CacheManager()
    test_data = {"result": "warm data"}
    
    # This should just call set, so we'll verify it doesn't raise an exception
    cache_manager.warm_cache("warm_key", test_data)
    
    _msg = "test_warm_cache returning"
    print(_msg)
