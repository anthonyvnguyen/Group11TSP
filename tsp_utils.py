"""
TSP Utilities

This module contains helper functions for calculating distances and tour lengths
for the Traveling Salesman Problem.
"""

import math


def euclidean_distance(coord1, coord2):
    """
    Calculate Euclidean distance between two 2D coordinates.
    
    Args:
        coord1: Tuple (x1, y1)
        coord2: Tuple (x2, y2)
        
    Returns:
        float: Euclidean distance
    """
    x1, y1 = coord1
    x2, y2 = coord2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return round(distance)


def calculate_tour_distance(tour, coordinates):
    """
    Calculate total distance of a TSP tour.
    
    Args:
        tour: List of vertex IDs in order
        coordinates: Dictionary mapping vertex_id -> (x, y)
        
    Returns:
        float: Total tour distance
    """
    if len(tour) < 2:
        return 0.0
    
    total_distance = 0.0
    
    # Distance between consecutive cities
    for i in range(len(tour) - 1):
        total_distance += euclidean_distance(
            coordinates[tour[i]],
            coordinates[tour[i + 1]]
        )
    
    # Distance from last city back to first
    total_distance += euclidean_distance(
        coordinates[tour[-1]],
        coordinates[tour[0]]
    )
    
    return total_distance

