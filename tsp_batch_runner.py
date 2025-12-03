#!/usr/bin/env python3
"""
TSP Batch Runner

Automates running all TSP algorithms on all instances and generates output files.
"""

import subprocess
import os

INSTANCES = [
    'Atlanta',
    'Berlin',
    'Boston',
    'Champaign',
    'Cincinnati',
    'Denver',
    'NYC',
    'Philadelphia',
    'Roanoke',
    'SanFrancisco',
    'Toronto',
    'UKansasState', 
    'UMissouri'
]

CUTOFF_TIME_BF = 60
CUTOFF_TIME_LS = 60
SEEDS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
OUTPUT_DIR = 'output'


def run_algorithm(instance, algorithm, cutoff_time, seed=None):
    cmd = [
        'python', 'tsp_solver.py',
        '-inst', instance,
        '-alg', algorithm,
        '-time', str(cutoff_time)
    ]
    
    if seed is not None:
        cmd.extend(['-seed', str(seed)])
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=cutoff_time + 30, cwd='.')
        
        if result.returncode == 0:
            instance_lower = instance.lower()
            if algorithm == 'BF':
                filename = f"{instance_lower}_{algorithm}_{int(cutoff_time)}.sol"
            elif algorithm == 'Approx':
                if seed is not None:
                    filename = f"{instance_lower}_{algorithm}_{seed}.sol"
                else:
                    filename = f"{instance_lower}_{algorithm}.sol"
            elif algorithm == 'LS':
                filename = f"{instance_lower}_{algorithm}_{int(cutoff_time)}_{seed}.sol"
            
            if os.path.exists(filename):
                os.rename(filename, os.path.join(OUTPUT_DIR, filename))
                print(f"[SUCCESS] {instance} - {algorithm}" + (f" (seed {seed})" if seed else ""))
            return True
        else:
            print(f"[FAILED] {instance} - {algorithm}" + (f" (seed {seed})" if seed else ""))
            print(f"  Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {instance} - {algorithm}" + (f" (seed {seed})" if seed else ""))
        return False
    except Exception as e:
        print(f"[EXCEPTION] {instance} - {algorithm}: {str(e)}")
        return False


def main():
    if not os.path.exists('tsp_solver.py'):
        print("Error: tsp_solver.py not found")
        return
    
    if not os.path.exists('DATA'):
        print("Error: DATA/ directory not found")
        return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}/")
    print("="*60)
    
    for instance in INSTANCES:
        tsp_file = os.path.join('DATA', f"{instance}.tsp")
        if not os.path.exists(tsp_file):
            print(f"Warning: {tsp_file} not found, skipping...")
            continue
        
        print(f"\nInstance: {instance}")
        print("-"*60)
        
        run_algorithm(instance, 'BF', CUTOFF_TIME_BF)
        run_algorithm(instance, 'Approx', 1, 0)
        
        for seed in SEEDS:
            run_algorithm(instance, 'LS', CUTOFF_TIME_LS, seed)
    
    print("\n" + "="*60)
    print("All runs complete. Output files in output/")
    print("="*60)


if __name__ == '__main__':
    main()