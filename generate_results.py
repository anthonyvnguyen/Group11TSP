#!/usr/bin/env python3
"""
Generate Results CSV for TSP Project

This script runs all three algorithms (BF, Approx, LS) on all datasets
and generates a results.csv file with performance metrics.

Usage:
    python generate_results.py

Requirements:
    - All TSP datasets in DATA/ folder
    - tsp_solver.py and algorithm modules available
"""

import os
import subprocess
import time
import csv
import statistics
from tsp_parser import parse_tsp_file
import tsp_brute_force
import tsp_approx
import tsp_genetic


def get_dataset_files(data_dir='DATA'):
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} directory not found")
        return []
    
    files = [f[:-4] for f in os.listdir(data_dir) if f.endswith('.tsp')]
    return sorted(files)


def run_brute_force(instance_name, coordinates, cutoff_time=600):
    print(f"  Running Brute Force (cutoff: {cutoff_time}s)...")
    start_time = time.time()
    
    best_tour, best_distance = tsp_brute_force.solve_tsp(coordinates, cutoff_time)
    
    elapsed_time = time.time() - start_time
    
    full_tour = 'Yes' if best_tour and len(best_tour) == len(coordinates) else 'No'
    
    return {
        'time': round(elapsed_time, 2),
        'quality': best_distance,
        'full_tour': full_tour
    }


def run_approx(instance_name, coordinates):
    print(f"  Running Approximation...")
    start_time = time.time()
    
    best_tour, best_distance = tsp_approx.solve_tsp(coordinates)
    
    elapsed_time = time.time() - start_time
    
    return {
        'time': round(elapsed_time, 2),
        'quality': best_distance
    }


def run_local_search(instance_name, coordinates, cutoff_time=600, num_runs=10):
    print(f"  Running Local Search {num_runs} times (cutoff: {cutoff_time}s)...")
    
    times = []
    qualities = []
    
    for seed in range(num_runs):
        print(f"    Run {seed+1}/{num_runs} (seed={seed})...", end=' ')
        start_time = time.time()
        
        best_tour, best_distance = tsp_genetic.solve_tsp(coordinates, cutoff_time, seed)
        
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
        qualities.append(best_distance)
        
        print(f"Quality: {best_distance:.2f}, Time: {elapsed_time:.2f}s")
    
    return {
        'avg_time': round(statistics.mean(times), 2),
        'avg_quality': round(statistics.mean(qualities), 2),
        'best_quality': min(qualities),
        'all_qualities': qualities
    }


def calculate_relative_error(quality, best_quality):
    if best_quality == 0:
        return 0.0
    rel_error = ((quality - best_quality) / best_quality)
    return round(rel_error, 5)


def generate_results_csv(datasets, bf_cutoff=600, ls_cutoff=600, ls_runs=10):
    results = []
    
    for dataset in datasets:
        print(f"\nProcessing {dataset}...")
        
        tsp_file = os.path.join('DATA', f"{dataset}.tsp")
        try:
            instance_name, dimension, coordinates = parse_tsp_file(tsp_file)
            print(f"  Loaded: {dimension} cities")
        except Exception as e:
            print(f"  Error loading {dataset}: {e}")
            continue
        
        row = {'Dataset': dataset}

        try:
            bf_results = run_brute_force(dataset, coordinates, bf_cutoff)
            row['BF_Time'] = bf_results['time']
            row['BF_Quality'] = bf_results['quality']
            row['BF_FullTour'] = bf_results['full_tour']
        except Exception as e:
            print(f"  Error in Brute Force: {e}")
            row['BF_Time'] = 'Error'
            row['BF_Quality'] = 'Error'
            row['BF_FullTour'] = 'No'

        try:
            approx_results = run_approx(dataset, coordinates)
            row['Approx_Time'] = approx_results['time']
            row['Approx_Quality'] = approx_results['quality']
        except Exception as e:
            print(f"  Error in Approximation: {e}")
            row['Approx_Time'] = 'Error'
            row['Approx_Quality'] = 'Error'
        
        try:
            ls_results = run_local_search(dataset, coordinates, ls_cutoff, ls_runs)
            row['LS_Time'] = ls_results['avg_time']
            row['LS_Quality'] = ls_results['avg_quality']
            best_quality = ls_results['best_quality']
        except Exception as e:
            print(f"  Error in Local Search: {e}")
            row['LS_Time'] = 'Error'
            row['LS_Quality'] = 'Error'
            best_quality = float('inf')
        
        if isinstance(row['Approx_Quality'], (int, float)) and best_quality != float('inf'):
            row['Approx_RelError'] = calculate_relative_error(row['Approx_Quality'], best_quality)
        else:
            row['Approx_RelError'] = 'N/A'
        
        if isinstance(row['LS_Quality'], (int, float)) and best_quality != float('inf'):
            row['LS_RelError'] = calculate_relative_error(row['LS_Quality'], best_quality)
        else:
            row['LS_RelError'] = 'N/A'
        
        results.append(row)
        print(f"  Completed {dataset}")
    
    csv_file = 'results.csv'
    fieldnames = [
        'Dataset',
        'BF_Time', 'BF_Quality', 'BF_FullTour',
        'Approx_Time', 'Approx_Quality', 'Approx_RelError',
        'LS_Time', 'LS_Quality', 'LS_RelError'
    ]
    
    formatted_fieldnames = [
        'Dataset',
        'Time(s)', 'Sol.Quality', 'Full Tour',
        'Time(s)', 'Sol.Quality', 'RelError',
        'Time(s)', 'Sol.Quality', 'RelError'
    ]
    
    with open(csv_file, 'w', newline='') as f:
        f.write(',Brute Force,,,Approx,,,Local Search,,\n')
        f.write(','.join(formatted_fieldnames) + '\n')
        
        for row in results:
            data_row = [
                row['Dataset'],
                row['BF_Time'], row['BF_Quality'], row['BF_FullTour'],
                row['Approx_Time'], row['Approx_Quality'], row['Approx_RelError'],
                row['LS_Time'], row['LS_Quality'], row['LS_RelError']
            ]
            f.write(','.join(str(x) for x in data_row) + '\n')
    
    print(f"\n{'='*60}")
    print(f"Results saved to {csv_file}")
    print(f"{'='*60}")


def main():
    print("TSP Results Generator")
    print("=" * 60)
    
    datasets = get_dataset_files('DATA')
    
    if not datasets:
        print("No datasets found in DATA/ directory")
        return
    
    print(f"Found {len(datasets)} datasets: {', '.join(datasets)}")
    
    bf_cutoff = 60
    ls_cutoff = 60
    ls_runs = 10
    
    print(f"\nConfiguration:")
    print(f"  Brute Force cutoff: {bf_cutoff}s")
    print(f"  Local Search cutoff: {ls_cutoff}s")
    print(f"  Local Search runs: {ls_runs}")
    
    response = input("\nProceed with generation? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return

    generate_results_csv(datasets, bf_cutoff, ls_cutoff, ls_runs)

if __name__ == '__main__':
    main()