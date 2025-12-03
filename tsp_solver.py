#!/usr/bin/env python3
"""
TSP Solver

This script solves Traveling Salesman Problem (TSP) instances using different algorithms.
It reads TSPLIB format files, finds a tour, and outputs the solution to a file.

Supported Algorithms:
    - BF: Brute Force (optimal, slow)
    - Approx: MST-based 2-approximation (fast, not optimal)
    - LS: Genetic Algorithm / Local Search (heuristic, requires seed)

Usage:
    python tsp_solver.py -inst <filename> -alg <method> -time <cutoff> [-seed <seed>]

Input:
    -inst: TSP instance filename (without .tsp extension, looks in DATA/ directory)
    -alg: Algorithm method (BF, Approx, LS)
    -time: Cutoff time in seconds
    -seed: Random seed (required for LS, optional for others)

Output:
    Creates a solution file based on method and parameters.
"""

import sys
import os
import argparse
from tsp_parser import parse_tsp_file
import tsp_brute_force
import tsp_approx
import tsp_genetic


def write_solution_file(instance_name, method, cutoff_time, seed, best_tour, best_distance):
    """
    Write solution to output file in the specified format.
    
    Args:
        instance_name: Name of the TSP instance
        method: Algorithm method (e.g., "BF", "Approx")
        cutoff_time: Cutoff time used (int or float)
        seed: Random seed (optional, None if not used)
        best_tour: List of vertex IDs in the tour
        best_distance: Total distance of the tour
    """
    instance_lower = instance_name.lower()
    
    # Generate filename based on method requirements
    if method == 'BF':
        # For BF, random seed can be omitted
        filename = f"{instance_lower}_{method}_{int(cutoff_time)}.sol"
    elif method == 'Approx':
        # For approximation algorithm, cutoff can be omitted
        if seed is not None:
            filename = f"{instance_lower}_{method}_{seed}.sol"
        else:
            filename = f"{instance_lower}_{method}.sol"
    elif method == 'LS':
        # For LS, both cutoff and seed are required
        if seed is None:
            raise ValueError("Seed is required for LS method")
        filename = f"{instance_lower}_{method}_{int(cutoff_time)}_{seed}.sol"
    else:
        # Default fallback
        filename = f"{instance_lower}_{method}_{int(cutoff_time)}.sol"
        if seed is not None:
            filename = f"{instance_lower}_{method}_{int(cutoff_time)}_{seed}.sol"
    
    with open(filename, 'w') as f:
        # Line 1: Best solution quality (floating point)
        f.write(f"{best_distance:.2f}\n")
        
        # Line 2: Comma-separated vertex IDs
        tour_str = ", ".join(str(vertex) for vertex in best_tour)
        f.write(f"{tour_str}\n")
    
    print(f"Solution written to: {filename}")


def main():
    """Main function to run the TSP solver."""
    parser = argparse.ArgumentParser(description='TSP Solver')
    parser.add_argument('-inst', required=True, help='TSP instance filename (without .tsp)')
    parser.add_argument('-alg', required=True, choices=['BF', 'Approx', 'LS'], help='Algorithm method')
    parser.add_argument('-time', type=float, required=True, help='Cutoff time in seconds')
    parser.add_argument('-seed', type=int, help='Random seed')
    
    args = parser.parse_args()
    
    # Validate method-specific requirements
    if args.alg == 'LS' and args.seed is None:
        print("Error: Seed parameter is required for LS (Local Search) method.")
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
        
        best_tour = None
        best_distance = 0.0
        
        # Route to appropriate algorithm
        if args.alg == 'BF':
            print(f"Running Brute Force algorithm (cutoff: {args.time}s)...")
            best_tour, best_distance = tsp_brute_force.solve_tsp(coordinates, args.time)
            
        elif args.alg == 'Approx':
            print(f"Running Approximation algorithm...")
            # Approx ignores cutoff time in this implementation
            best_tour, best_distance = tsp_approx.solve_tsp(coordinates, args.time)
            
        elif args.alg == 'LS':
            if args.seed is None:
                print("Error: Seed parameter is required for LS method.")
                sys.exit(1)
            print(f"Running Genetic Algorithm / Local Search (cutoff: {args.time}s, seed: {args.seed})...")
            best_tour, best_distance = tsp_genetic.solve_tsp(coordinates, args.time, args.seed)
            
        if best_tour is None:
            print("Error: No solution found.")
            sys.exit(1)
        
        print(f"Best tour distance: {best_distance:.2f}")
        # Print first few and last few cities if tour is long
        if len(best_tour) > 20:
            tour_preview = " -> ".join(str(v) for v in best_tour[:5]) + " ... " + " -> ".join(str(v) for v in best_tour[-5:])
        else:
            tour_preview = " -> ".join(str(v) for v in best_tour)
        print(f"Tour: {tour_preview} -> {best_tour[0]}")
        
        # Write solution file
        write_solution_file(args.inst, args.alg, args.time, args.seed, 
                          best_tour, best_distance)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # import traceback
        # traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
