"""
Performance metrics collection for the multi-step agent.
"""
import time
import logging
from typing import Dict, Any, Callable
from functools import wraps
import json
from pathlib import Path

log = logging.getLogger(__name__)


class PerformanceMetrics:
    """Collects and manages performance metrics for the agent."""

    def __init__(self):
        """Initialize performance metrics collector.

        Notes:
            1. Initialize an empty dictionary for storing metrics.
            2. Initialize an empty dictionary for tracking start times of operations.
            3. Log the initialization.
        """
        _msg = "PerformanceMetrics initializing"
        log.debug(_msg)
        
        self.metrics = {
            "operation_timings": {},
            "api_calls": {},
            "controller_iterations": {},
            "memory_operations": {},
            "tool_executions": {}
        }
        self.start_times = {}
        
        _msg = "PerformanceMetrics initialized"
        log.debug(_msg)

    def start_timer(self, operation_name: str) -> None:
        """Start timing an operation.

        Args:
            operation_name: The name of the operation to time.

        Returns:
            None

        Notes:
            1. Store the current time in the start_times dictionary using operation_name as the key.
            2. Log the start of the timer.
        """
        _msg = f"PerformanceMetrics.start_timer starting for {operation_name}"
        log.debug(_msg)
        
        self.start_times[operation_name] = time.time()
        
        _msg = f"PerformanceMetrics.start_timer returning for {operation_name}"
        log.debug(_msg)

    def stop_timer(self, operation_name: str) -> float:
        """Stop timing an operation and record the duration.

        Args:
            operation_name: The name of the operation to stop timing.

        Returns:
            The duration of the operation in seconds. Returns 0.0 if no start time is found.

        Notes:
            1. Check if the operation_name exists in start_times.
            2. If it exists, calculate the duration by subtracting the start time from the current time.
            3. Append the duration to the list of timings for operation_name.
            4. Remove the operation_name from start_times.
            5. Log the duration and return it.
            6. If operation_name is not found, log a warning and return 0.0.
        """
        _msg = f"PerformanceMetrics.stop_timer starting for {operation_name}"
        log.debug(_msg)
        
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            if operation_name not in self.metrics["operation_timings"]:
                self.metrics["operation_timings"][operation_name] = []
            self.metrics["operation_timings"][operation_name].append(duration)
            
            # Remove the start time
            del self.start_times[operation_name]
            
            _msg = f"PerformanceMetrics.stop_timer returning {duration}s for {operation_name}"
            log.debug(_msg)
            return duration
        else:
            _msg = f"PerformanceMetrics.stop_timer: No start time found for {operation_name}"
            log.warning(_msg)
            return 0.0

    def record_api_call(self, endpoint: str, duration: float, cost: float = 0.0) -> None:
        """Record an API call with timing and cost.

        Args:
            endpoint: The API endpoint that was called.
            duration: The duration of the API call in seconds.
            cost: The cost of the API call in USD (default: 0.0).

        Returns:
            None

        Notes:
            1. If the endpoint is not in the api_calls dictionary, initialize its metrics.
            2. Increment the count of API calls for the endpoint.
            3. Add the duration and cost to the total for the endpoint.
            4. Calculate and store the average duration and cost.
        """
        _msg = f"PerformanceMetrics.record_api_call starting for {endpoint}"
        log.debug(_msg)
        
        if endpoint not in self.metrics["api_calls"]:
            self.metrics["api_calls"][endpoint] = {
                "count": 0,
                "total_duration": 0.0,
                "total_cost": 0.0,
                "average_duration": 0.0,
                "average_cost": 0.0
            }
        
        api_metrics = self.metrics["api_calls"][endpoint]
        api_metrics["count"] += 1
        api_metrics["total_duration"] += duration
        api_metrics["total_cost"] += cost
        api_metrics["average_duration"] = api_metrics["total_duration"] / api_metrics["count"]
        api_metrics["average_cost"] = api_metrics["total_cost"] / api_metrics["count"]
        
        _msg = f"PerformanceMetrics.record_api_call returning for {endpoint}"
        log.debug(_msg)

    def record_controller_iteration(self, iteration: int, thoughts_duration: float, 
                                  action_duration: float, completion_duration: float) -> None:
        """Record metrics for a controller iteration.

        Args:
            iteration: The iteration number.
            thoughts_duration: Time taken for the thinking phase.
            action_duration: Time taken for the action phase.
            completion_duration: Time taken for the completion phase.

        Returns:
            None

        Notes:
            1. Create a dictionary to store the metrics for the given iteration.
            2. Include the durations for each phase and the total duration.
            3. Store the dictionary in the controller_iterations dictionary using the iteration number as the key.
        """
        _msg = f"PerformanceMetrics.record_controller_iteration starting for iteration {iteration}"
        log.debug(_msg)
        
        self.metrics["controller_iterations"][str(iteration)] = {
            "thoughts_duration": thoughts_duration,
            "action_duration": action_duration,
            "completion_duration": completion_duration,
            "total_duration": thoughts_duration + action_duration + completion_duration
        }
        
        _msg = f"PerformanceMetrics.record_controller_iteration returning for iteration {iteration}"
        log.debug(_msg)

    def record_memory_operation(self, operation: str, duration: float) -> None:
        """Record a memory operation with timing.

        Args:
            operation: The name of the memory operation (e.g., "add_observation", "serialize").
            duration: The duration of the operation in seconds.

        Returns:
            None

        Notes:
            1. If the operation is not in the memory_operations dictionary, initialize an empty list.
            2. Append the duration to the list of timings for the operation.
        """
        _msg = f"PerformanceMetrics.record_memory_operation starting for {operation}"
        log.debug(_msg)
        
        if operation not in self.metrics["memory_operations"]:
            self.metrics["memory_operations"][operation] = []
        self.metrics["memory_operations"][operation].append(duration)
        
        _msg = f"PerformanceMetrics.record_memory_operation returning for {operation}"
        log.debug(_msg)

    def record_tool_execution(self, tool_name: str, duration: float, success: bool = True) -> None:
        """Record a tool execution with timing and success status.

        Args:
            tool_name: The name of the tool executed.
            duration: The duration of the tool execution in seconds.
            success: Whether the tool execution was successful (default: True).

        Returns:
            None

        Notes:
            1. If the tool_name is not in the tool_executions dictionary, initialize its metrics.
            2. Increment the count of tool executions for the tool.
            3. If the execution was successful, increment the success count.
            4. Add the duration to the total duration for the tool.
            5. Calculate and store the average duration and success rate.
        """
        _msg = f"PerformanceMetrics.record_tool_execution starting for {tool_name}"
        log.debug(_msg)
        
        if tool_name not in self.metrics["tool_executions"]:
            self.metrics["tool_executions"][tool_name] = {
                "count": 0,
                "success_count": 0,
                "total_duration": 0.0,
                "average_duration": 0.0,
                "success_rate": 0.0
            }
        
        tool_metrics = self.metrics["tool_executions"][tool_name]
        tool_metrics["count"] += 1
        if success:
            tool_metrics["success_count"] += 1
        tool_metrics["total_duration"] += duration
        tool_metrics["average_duration"] = tool_metrics["total_duration"] / tool_metrics["count"]
        tool_metrics["success_rate"] = tool_metrics["success_count"] / tool_metrics["count"]
        
        _msg = f"PerformanceMetrics.record_tool_execution returning for {tool_name}"
        log.debug(_msg)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics.

        Returns:
            A dictionary containing summary statistics for all metrics, including:
            - operation_timings: Counts, totals, averages, mins, and maxes for each operation.
            - api_calls: Count, total and average duration and cost for each endpoint.
            - controller_iterations: Durations for each phase of each iteration.
            - memory_operations: Lists of durations for each operation.
            - tool_executions: Counts, success rates, and average durations for each tool.

        Notes:
            1. Initialize an empty dictionary for the summary.
            2. Summarize operation timings by calculating counts, totals, averages, mins, and maxes.
            3. Include other metrics directly from the metrics dictionary.
        """
        _msg = "PerformanceMetrics.get_metrics_summary starting"
        log.debug(_msg)
        
        summary = {}
        
        # Summarize operation timings
        summary["operation_timings"] = {}
        for operation, timings in self.metrics["operation_timings"].items():
            if timings:
                summary["operation_timings"][operation] = {
                    "count": len(timings),
                    "total_time": sum(timings),
                    "average_time": sum(timings) / len(timings),
                    "min_time": min(timings),
                    "max_time": max(timings)
                }
        
        # Include other metrics
        summary["api_calls"] = self.metrics["api_calls"]
        summary["controller_iterations"] = self.metrics["controller_iterations"]
        summary["memory_operations"] = self.metrics["memory_operations"]
        summary["tool_executions"] = self.metrics["tool_executions"]
        
        _msg = "PerformanceMetrics.get_metrics_summary returning"
        log.debug(_msg)
        return summary

    def reset_metrics(self) -> None:
        """Reset all collected metrics.

        Returns:
            None

        Notes:
            1. Reinitialize the metrics dictionary to empty.
            2. Reinitialize the start_times dictionary to empty.
        """
        _msg = "PerformanceMetrics.reset_metrics starting"
        log.debug(_msg)
        
        self.metrics = {
            "operation_timings": {},
            "api_calls": {},
            "controller_iterations": {},
            "memory_operations": {},
            "tool_executions": {}
        }
        self.start_times = {}
        
        _msg = "PerformanceMetrics.reset_metrics returning"
        log.debug(_msg)

    def save_metrics(self, filepath: str) -> None:
        """Save metrics to a JSON file.

        Args:
            filepath: The path to save the metrics file.

        Returns:
            None

        Notes:
            1. Create a copy of the metrics dictionary to avoid serialization issues.
            2. Write the metrics dictionary to the file in JSON format with indentation.
        """
        _msg = f"PerformanceMetrics.save_metrics starting to {filepath}"
        log.debug(_msg)
        
        # Convert any non-serializable objects
        metrics_to_save = {}
        for category, data in self.metrics.items():
            metrics_to_save[category] = {}
            for key, value in data.items():
                # Handle any special objects that need conversion
                metrics_to_save[category][key] = value
        
        with open(filepath, 'w') as f:
            json.dump(metrics_to_save, f, indent=2)
        
        _msg = f"PerformanceMetrics.save_metrics completed to {filepath}"
        log.debug(_msg)


def timing_decorator(metric_name: str = None):
    """Decorator to time function execution and record metrics.

    Args:
        metric_name: Name to use for the metric (defaults to function name).

    Returns:
        Decorated function that records timing metrics.

    Notes:
        1. Extract the metrics instance from the first argument if it's a method.
        2. Determine the operation name based on the provided metric_name or function name.
        3. Start the timer for the operation.
        4. Record the start time.
        5. Execute the function and capture the result.
        6. Calculate the duration and stop the timer.
        7. Return the result of the function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the metrics instance from the first argument if it's a method
            metrics_instance = None
            if args and hasattr(args[0], 'metrics') and isinstance(args[0].metrics, PerformanceMetrics):
                metrics_instance = args[0].metrics
            elif hasattr(wrapper, 'metrics_instance'):
                metrics_instance = wrapper.metrics_instance
            
            operation_name = metric_name or func.__name__
            
            if metrics_instance:
                metrics_instance.start_timer(operation_name)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                if metrics_instance:
                    metrics_instance.stop_timer(operation_name)
        return wrapper
    return decorator


# Global metrics instance
global_metrics = PerformanceMetrics()
