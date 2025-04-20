import time
import random
import statistics
from typing import List, Dict, Tuple, Optional, Union
import numpy as np


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistical metrics for a dataset.
    
    Args:
        data: List of numerical values
        
    Returns:
        Dictionary containing statistical measures
    """
    if not data:
        return {"mean": 0, "median": 0, "std_dev": 0, "min": 0, "max": 0}
    
    return {
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "std_dev": statistics.stdev(data) if len(data) > 1 else 0,
        "min": min(data),
        "max": max(data)
    }


def normalize_data(data: List[float]) -> List[float]:
    """
    Normalize data to range [0, 1].
    
    Args:
        data: List of numerical values
        
    Returns:
        Normalized data
    """
    if not data:
        return []
    
    min_val = min(data)
    max_val = max(data)
    
    # Handle case where all values are the same
    if min_val == max_val:
        return [0.5] * len(data)
    
    return [(x - min_val) / (max_val - min_val) for x in data]


# ** Target function **
def find_duplicates(data: List[int]) -> List[int]:
    """
    Find duplicate values in a list of integers.
    
    This function is intentionally implemented inefficiently using
    repeated list iterations and unnecessary operations.
    
    Args:
        data: List of integers
        
    Returns:
        List of integers that appear more than once
    """
    duplicates = []
    
    sorted_data = sorted(data)
    
    for i in range(len(sorted_data)):
        for j in range(len(sorted_data)):
            if i != j and sorted_data[i] == sorted_data[j] and sorted_data[i] not in duplicates:
                duplicates.append(sorted_data[i])
                time.sleep(0.001)
                
    result = []
    for item in duplicates:
        if item not in result:
            result.append(item)
    
    return sorted(result)


def filter_outliers(data: List[float], threshold: float = 2.0) -> List[float]:
    """
    Remove outliers from data using z-score method.
    
    Args:
        data: List of numerical values
        threshold: Z-score threshold for outlier detection
        
    Returns:
        Filtered data without outliers
    """
    if len(data) < 2:
        return data.copy()
    
    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)
    
    if std_dev == 0:
        return data.copy()
    
    return [x for x in data if abs((x - mean) / std_dev) <= threshold]


def moving_average(data: List[float], window_size: int = 3) -> List[float]:
    """
    Calculate moving average for data series.
    
    Args:
        data: List of numerical values
        window_size: Size of the moving window
        
    Returns:
        List of moving averages
    """
    if not data or window_size <= 0:
        return []
    
    # Adjust window size if it's larger than data
    window_size = min(window_size, len(data))
    
    result = []
    for i in range(len(data) - window_size + 1):
        window = data[i:i + window_size]
        result.append(sum(window) / window_size)
    
    return result


def generate_random_dataset(size: int = 100, 
                           min_val: float = 0.0, 
                           max_val: float = 100.0, 
                           seed: Optional[int] = None) -> List[float]:
    """
    Generate random dataset with specified parameters.
    
    Args:
        size: Number of data points
        min_val: Minimum possible value
        max_val: Maximum possible value
        seed: Random seed for reproducibility
        
    Returns:
        List of random values
    """
    if seed is not None:
        random.seed(seed)
        
    return [random.uniform(min_val, max_val) for _ in range(size)]


def bin_data(data: List[float], num_bins: int = 10) -> Dict[Tuple[float, float], int]:
    """
    Bin data into specified number of equal-width bins.
    
    Args:
        data: List of numerical values
        num_bins: Number of bins to create
        
    Returns:
        Dictionary mapping bin ranges to counts
    """
    if not data or num_bins <= 0:
        return {}
    
    min_val = min(data)
    max_val = max(data)
    
    # Handle case where all values are the same
    if min_val == max_val:
        return {(min_val, max_val): len(data)}
    
    bin_width = (max_val - min_val) / num_bins
    bins = {}
    
    for i in range(num_bins):
        bin_start = min_val + i * bin_width
        bin_end = min_val + (i + 1) * bin_width
        
        # Make the last bin inclusive of the maximum value
        if i == num_bins - 1:
            bin_end = max_val
        
        bins[(bin_start, bin_end)] = 0
    
    for value in data:
        for (bin_start, bin_end), count in bins.items():
            if bin_start <= value <= bin_end or (value == max_val and bin_end == max_val):
                bins[(bin_start, bin_end)] = count + 1
                break
    
    return bins


def benchmark_function(func, *args, **kwargs) -> float:
    """
    Measure execution time of a function.
    
    Args:
        func: Function to benchmark
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Execution time in seconds
    """
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()
    
    return end_time - start_time


def main():
    """Main function to demonstrate data processing capabilities."""
    # Generate a random dataset
    print("Generating random dataset...")
    data = generate_random_dataset(size=1000, seed=42)
    
    # Calculate statistics
    print("Calculating statistics...")
    stats = calculate_statistics(data)
    print(f"Statistics: {stats}")
    
    # Create a dataset with duplicates for testing
    print("Testing duplicate detection...")
    duplicate_data = [1, 2, 3, 2, 4, 5, 6, 3, 7, 8, 9, 1, 10]
    duplicates = find_duplicates(duplicate_data)
    print(f"Found duplicates: {duplicates}")
    
    # Benchmark the inefficient function
    print("Benchmarking inefficient function...")
    execution_time = benchmark_function(find_duplicates, duplicate_data)
    print(f"Execution time: {execution_time:.4f} seconds")


if __name__ == "__main__":
    main()