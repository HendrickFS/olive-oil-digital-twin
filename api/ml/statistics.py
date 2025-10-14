"""
Statistical Analysis Functions
"""

def calculate_stats(values):
    """
    Calculate basic statistics for sensor data
    
    Args:
        values: List of numeric values
    
    Returns:
        Dictionary with min, max, average, etc.
    """
    if not values:
        return {}
    
    stats = {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "average": sum(values) / len(values)
    }
    
    # TODO: Add more statistical calculations
    # - Standard deviation
    # - Percentiles
    # - Trend analysis
    
    return stats