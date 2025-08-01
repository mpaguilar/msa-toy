"""
Unit tests for performance metrics collection.
"""
import pytest
import time
import json
import os
from unittest.mock import patch, mock_open

from msa.monitoring.metrics import PerformanceMetrics, timing_decorator, global_metrics


class TestPerformanceMetrics:
    """Test performance metrics collection functionality."""

    def test_initialization(self):
        """Test that PerformanceMetrics initializes correctly."""
        metrics = PerformanceMetrics()
        
        # Check that metrics structure is initialized
        assert "operation_timings" in metrics.metrics
        assert "api_calls" in metrics.metrics
        assert "controller_iterations" in metrics.metrics
        assert "memory_operations" in metrics.metrics
        assert "tool_executions" in metrics.metrics
        assert metrics.start_times == {}

    def test_timer_operations(self):
        """Test starting and stopping timers."""
        metrics = PerformanceMetrics()
        
        # Start timer
        metrics.start_timer("test_operation")
        assert "test_operation" in metrics.start_times
        
        # Stop timer
        duration = metrics.stop_timer("test_operation")
        assert duration >= 0
        assert "test_operation" not in metrics.start_times
        
        # Check that timing was recorded
        assert "test_operation" in metrics.metrics["operation_timings"]
        assert len(metrics.metrics["operation_timings"]["test_operation"]) == 1

    def test_stop_timer_without_start(self):
        """Test stopping a timer that was never started."""
        metrics = PerformanceMetrics()
        
        # Stop timer that was never started
        duration = metrics.stop_timer("nonexistent_operation")
        assert duration == 0.0

    def test_record_api_call(self):
        """Test recording API call metrics."""
        metrics = PerformanceMetrics()
        
        # Record an API call
        metrics.record_api_call("test_endpoint", 0.5, 0.01)
        
        # Check metrics were recorded
        assert "test_endpoint" in metrics.metrics["api_calls"]
        api_metrics = metrics.metrics["api_calls"]["test_endpoint"]
        assert api_metrics["count"] == 1
        assert api_metrics["total_duration"] == 0.5
        assert api_metrics["total_cost"] == 0.01
        assert api_metrics["average_duration"] == 0.5
        assert api_metrics["average_cost"] == 0.01
        
        # Record another call to test aggregation
        metrics.record_api_call("test_endpoint", 1.0, 0.02)
        
        api_metrics = metrics.metrics["api_calls"]["test_endpoint"]
        assert api_metrics["count"] == 2
        assert api_metrics["total_duration"] == 1.5
        assert api_metrics["total_cost"] == 0.03
        assert api_metrics["average_duration"] == 0.75
        assert api_metrics["average_cost"] == 0.015

    def test_record_controller_iteration(self):
        """Test recording controller iteration metrics."""
        metrics = PerformanceMetrics()
        
        # Record a controller iteration
        metrics.record_controller_iteration(1, 0.1, 0.2, 0.3)
        
        # Check metrics were recorded
        assert "1" in metrics.metrics["controller_iterations"]
        iteration_metrics = metrics.metrics["controller_iterations"]["1"]
        assert iteration_metrics["thoughts_duration"] == 0.1
        assert iteration_metrics["action_duration"] == 0.2
        assert iteration_metrics["completion_duration"] == 0.3
        # Use pytest.approx for floating point comparison
        assert iteration_metrics["total_duration"] == pytest.approx(0.6)

    def test_record_memory_operation(self):
        """Test recording memory operation metrics."""
        metrics = PerformanceMetrics()
        
        # Record memory operations
        metrics.record_memory_operation("add_observation", 0.05)
        metrics.record_memory_operation("add_observation", 0.03)
        
        # Check metrics were recorded
        assert "add_observation" in metrics.metrics["memory_operations"]
        durations = metrics.metrics["memory_operations"]["add_observation"]
        assert len(durations) == 2
        assert 0.05 in durations
        assert 0.03 in durations

    def test_record_tool_execution(self):
        """Test recording tool execution metrics."""
        metrics = PerformanceMetrics()
        
        # Record successful tool execution
        metrics.record_tool_execution("web_search", 0.5, True)
        
        # Check metrics were recorded
        assert "web_search" in metrics.metrics["tool_executions"]
        tool_metrics = metrics.metrics["tool_executions"]["web_search"]
        assert tool_metrics["count"] == 1
        assert tool_metrics["success_count"] == 1
        assert tool_metrics["total_duration"] == 0.5
        assert tool_metrics["average_duration"] == 0.5
        assert tool_metrics["success_rate"] == 1.0
        
        # Record failed tool execution
        metrics.record_tool_execution("web_search", 0.3, False)
        
        tool_metrics = metrics.metrics["tool_executions"]["web_search"]
        assert tool_metrics["count"] == 2
        assert tool_metrics["success_count"] == 1
        assert tool_metrics["total_duration"] == 0.8
        assert tool_metrics["average_duration"] == 0.4
        assert tool_metrics["success_rate"] == 0.5

    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        metrics = PerformanceMetrics()
        
        # Add some test data
        metrics.start_timer("test_op")
        time.sleep(0.01)  # Small delay to ensure non-zero duration
        metrics.stop_timer("test_op")
        
        metrics.record_api_call("test_api", 0.2, 0.01)
        metrics.record_memory_operation("test_memory", 0.05)
        metrics.record_tool_execution("test_tool", 0.3, True)
        
        # Get summary
        summary = metrics.get_metrics_summary()
        
        # Check summary structure
        assert "operation_timings" in summary
        assert "api_calls" in summary
        assert "controller_iterations" in summary
        assert "memory_operations" in summary
        assert "tool_executions" in summary
        
        # Check operation timings summary
        assert "test_op" in summary["operation_timings"]
        op_summary = summary["operation_timings"]["test_op"]
        assert op_summary["count"] == 1
        assert op_summary["total_time"] > 0
        assert op_summary["average_time"] > 0

    def test_reset_metrics(self):
        """Test resetting all metrics."""
        metrics = PerformanceMetrics()
        
        # Add some test data
        metrics.start_timer("test_op")
        metrics.stop_timer("test_op")
        metrics.record_api_call("test_api", 0.2, 0.01)
        
        # Verify data exists
        assert len(metrics.metrics["operation_timings"]["test_op"]) > 0
        assert "test_api" in metrics.metrics["api_calls"]
        
        # Reset metrics
        metrics.reset_metrics()
        
        # Verify metrics are reset
        assert metrics.metrics["operation_timings"] == {}
        assert metrics.metrics["api_calls"] == {}
        assert metrics.metrics["controller_iterations"] == {}
        assert metrics.metrics["memory_operations"] == {}
        assert metrics.metrics["tool_executions"] == {}
        assert metrics.start_times == {}

    @patch("builtins.open", new_callable=mock_open)
    def test_save_metrics(self, mock_file):
        """Test saving metrics to file."""
        metrics = PerformanceMetrics()
        
        # Add some test data
        metrics.record_api_call("test_api", 0.2, 0.01)
        
        # Save metrics
        test_file = "test_metrics.json"
        metrics.save_metrics(test_file)
        
        # Verify file was written
        mock_file.assert_called_once_with(test_file, 'w')


class TestTimingDecorator:
    """Test timing decorator functionality."""

    def test_timing_decorator_without_metric_name(self):
        """Test timing decorator without explicit metric name."""
        metrics = PerformanceMetrics()
        
        # Create a decorated function
        @timing_decorator()
        def test_function():
            time.sleep(0.01)  # Small delay
            return "result"
        
        # Attach metrics instance to wrapper for testing
        test_function.metrics_instance = metrics
        
        # Call the function
        result = test_function()
        
        # Check result and metrics
        assert result == "result"
        assert "test_function" in metrics.metrics["operation_timings"]
        assert len(metrics.metrics["operation_timings"]["test_function"]) == 1

    def test_timing_decorator_with_metric_name(self):
        """Test timing decorator with explicit metric name."""
        metrics = PerformanceMetrics()
        
        # Create a decorated function with custom metric name
        @timing_decorator("custom_metric")
        def test_function():
            time.sleep(0.01)  # Small delay
            return "result"
        
        # Attach metrics instance to wrapper for testing
        test_function.metrics_instance = metrics
        
        # Call the function
        result = test_function()
        
        # Check result and metrics
        assert result == "result"
        assert "custom_metric" in metrics.metrics["operation_timings"]
        assert len(metrics.metrics["operation_timings"]["custom_metric"]) == 1

    def test_timing_decorator_with_exception(self):
        """Test timing decorator when function raises exception."""
        metrics = PerformanceMetrics()
        
        # Create a decorated function that raises exception
        @timing_decorator("exception_metric")
        def test_function():
            raise ValueError("Test exception")
        
        # Attach metrics instance to wrapper for testing
        test_function.metrics_instance = metrics
        
        # Call the function and expect exception
        with pytest.raises(ValueError):
            test_function()
        
        # Check that timing was still recorded
        assert "exception_metric" in metrics.metrics["operation_timings"]
        assert len(metrics.metrics["operation_timings"]["exception_metric"]) == 1


def test_global_metrics_instance():
    """Test that global metrics instance is created."""
    assert isinstance(global_metrics, PerformanceMetrics)


if __name__ == "__main__":
    pytest.main([__file__])
