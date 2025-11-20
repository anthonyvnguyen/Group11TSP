#!/usr/bin/env python3
"""
TSP Solver - Brute Force Implementation

This script solves Traveling Salesman Problem (TSP) instances using brute force algorithm.
It reads TSPLIB format files, finds the optimal tour by checking all permutations,
and outputs the solution to a file in the specified format.

Usage:
    python tsp_solver.py -inst <filename> -alg BF -time <cutoff> [-seed <seed>]

Input:
    -inst: TSP instance filename (without .tsp extension, looks in DATA/ directory)
    -alg: Algorithm method (BF for brute force)
    -time: Cutoff time in seconds
    -seed: Random seed (optional for BF, ignored)

Output:
    Creates a solution file: <instance> <method> <cutoff>.sol
    Format:
        Line 1: Best solution quality (total distance)
        Line 2: Comma-separated vertex IDs of the tour
"""

import sys
import os
import argparse
import math
import time
from itertools import permutations
from tsp_parser import parse_tsp_file


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
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


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


def brute_force_tsp(coordinates, cutoff_time):
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
    # Check time every 10000 iterations for efficiency, but always check on first iteration
    check_interval = 10000
    
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


def write_solution_file(instance_name, method, cutoff_time, seed, best_tour, best_distance):
    """
    Write solution to output file in the specified format.
    
    Args:
        instance_name: Name of the TSP instance
        method: Algorithm method (e.g., "BF")
        cutoff_time: Cutoff time used
        seed: Random seed (optional, None if not used)
        best_tour: List of vertex IDs in the tour
        best_distance: Total distance of the tour
    """
    # Generate filename: <instance> <method> <cutoff> [<seed>].sol
    instance_lower = instance_name.lower()
    
    if seed is not None:
        filename = f"{instance_lower} {method} {cutoff_time} {seed}.sol"
    else:
        filename = f"{instance_lower} {method} {cutoff_time}.sol"
    
    with open(filename, 'w') as f:
        # Line 1: Best solution quality (floating point)
        f.write(f"{best_distance:.2f}\n")
        
        # Line 2: Comma-separated vertex IDs
        tour_str = ", ".join(str(vertex) for vertex in best_tour)
        f.write(f"{tour_str}\n")
    
    print(f"Solution written to: {filename}")


def main():
    """Main function to run the TSP solver."""
    parser = argparse.ArgumentParser(description='TSP Solver - Brute Force')
    parser.add_argument('-inst', required=True, help='TSP instance filename (without .tsp)')
    parser.add_argument('-alg', required=True, help='Algorithm method (BF, Approx, LS)')
    parser.add_argument('-time', type=float, required=True, help='Cutoff time in seconds')
    parser.add_argument('-seed', type=int, help='Random seed (optional for BF)')
    
    args = parser.parse_args()
    
    # Validate method
    if args.alg != 'BF':
        print(f"Error: Only BF (brute force) method is currently implemented.")
        sys.exit(1)
    
    # Validate cutoff time
    if args.time <= 0:
        print(f"Error: Cutoff time must be positive.")
        sys.exit(1)
    
    # Construct file path
    tsp_file = os.path.join('DATA', f"{args.inst}.tsp")
    
    if not os.path.exists(tsp_file):
        print(f"Error: TSP file not found: {tsp_file}")
        sys.exit(1)
    
    try:
        # Parse TSP file
        instance_name, dimension, coordinates = parse_tsp_file(tsp_file)
        print(f"Loaded instance: {instance_name} ({dimension} cities)")
        
        # Solve using brute force
        print(f"Running brute force algorithm (cutoff: {args.time}s)...")
        best_tour, best_distance = brute_force_tsp(coordinates, args.time)
        
        if best_tour is None:
            print("Error: No solution found.")
            sys.exit(1)
        
        print(f"Best tour distance: {best_distance:.2f}")
        print(f"Tour: {' -> '.join(str(v) for v in best_tour)} -> {best_tour[0]}")
        
        # Write solution file
        write_solution_file(instance_name, args.alg, int(args.time), args.seed, 
                          best_tour, best_distance)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

