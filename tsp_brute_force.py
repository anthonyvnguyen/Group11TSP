"""
TSP Brute Force Algorithm

This module implements the brute force algorithm for solving the Traveling Salesman Problem.
It checks all possible permutations of cities to find the optimal tour.
"""

import time
import math
from itertools import permutations
from tsp_utils import calculate_tour_distance


def solve_tsp(coordinates, cutoff_time):
    """
    Solve TSP using brute force by checking all permutations.
    
    Args:
        coordinates: Dictionary mapping vertex_id -> (x, y)
        cutoff_time: Maximum time in seconds to run
        
    Returns:
        tuple: (best_tour, best_distance)
    """
    start_time = time.time()
    vertices = sorted(coordinates.keys())
    
    if len(vertices) == 0:
        return [], 0.0
    if len(vertices) == 1:
        return vertices, 0.0
    
    # Fix starting vertex to reduce permutations (n-1)! instead of n!
    start_vertex = vertices[0]
    remaining_vertices = vertices[1:]
    
    best_tour = None
    best_distance = float('inf')
    
    total_permutations = math.factorial(len(remaining_vertices))
    checked = 0
    # Check time every 1000 iterations for efficiency, but always check on first iteration
    check_interval = 1000
    
    print(f"Total permutations to check: {total_permutations:,}")
    if total_permutations > 1000000:
        print("Warning: This will take a very long time. The algorithm will stop at the cutoff time.")
    
    # Generate all permutations of remaining vertices
    for perm in permutations(remaining_vertices):
        checked += 1
        
        # Check time periodically (not every iteration for performance)
        if checked == 1 or checked % check_interval == 0:
            elapsed = time.time() - start_time
            if elapsed > cutoff_time:
                print(f"\nCutoff time ({cutoff_time}s) reached. Checked {checked:,} / {total_permutations:,} permutations")
                break
        
        # Create tour: start_vertex + permutation + back to start
        tour = [start_vertex] + list(perm)
        distance = calculate_tour_distance(tour, coordinates)
        
        if distance < best_distance:
            best_distance = distance
            best_tour = tour
    
    if best_tour is None:
        # If we didn't find any solution, return a default tour
        best_tour = [start_vertex] + remaining_vertices
        best_distance = calculate_tour_distance(best_tour, coordinates)
    
    return best_tour, best_distance

