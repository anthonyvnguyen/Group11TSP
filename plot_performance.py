"""
Generate plot of performance of various algorithms from results.csv file

Usage:
    python plot_performance.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def load_results(csv_file='results.csv'):
    df = pd.read_csv(csv_file, skiprows=1)
    df.columns = ['Dataset', 'BF_Time', 'BF_Quality', 'BF_FullTour',
                  'Approx_Time', 'Approx_Quality', 'Approx_RelError', 'Approx_FullTour',
                  'LS_Time', 'LS_Quality', 'LS_RelError', 'LS_FullTour']
    return df


def normalize_quality(row):
    qualities = []
    
    try:
        bf_quality = float(row['BF_Quality'])
        qualities.append(bf_quality)
    except (ValueError, TypeError):
        bf_quality = None
    
    try:
        approx_quality = float(row['Approx_Quality'])
        qualities.append(approx_quality)
    except (ValueError, TypeError):
        approx_quality = None
    
    try:
        ls_quality = float(row['LS_Quality'])
        qualities.append(ls_quality)
    except (ValueError, TypeError):
        ls_quality = None
    
    valid_qualities = [q for q in qualities if q is not None]
    if not valid_qualities:
        return None, None, None, None
    
    best_quality = min(valid_qualities)
    
    normalized_bf = bf_quality / best_quality if bf_quality is not None else None
    normalized_approx = approx_quality / best_quality if approx_quality is not None else None
    normalized_ls = ls_quality / best_quality if ls_quality is not None else None
    
    return normalized_bf, normalized_approx, normalized_ls, best_quality


def create_bar_chart(df, output_file='performance_chart.png'):
    normalized_data = []
    
    for _, row in df.iterrows():
        norm_bf, norm_approx, norm_ls, best_quality = normalize_quality(row)
        
        if best_quality is not None:
            normalized_data.append({
                'Dataset': row['Dataset'],
                'BF': norm_bf,
                'Approx': norm_approx,
                'LS': norm_ls
            })
    
    norm_df = pd.DataFrame(normalized_data)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    datasets = norm_df['Dataset']
    x = np.arange(len(datasets))
    width = 0.25
    
    bars1 = ax.bar(x - width, norm_df['BF'], width, label='Brute Force', 
                   color='#e74c3c', alpha=0.8)
    bars2 = ax.bar(x, norm_df['Approx'], width, label='MST Approximation', 
                   color='#3498db', alpha=0.8)
    bars3 = ax.bar(x + width, norm_df['LS'], width, label='Genetic (Local Search)', 
                   color='#2ecc71', alpha=0.8)
    
    ax.set_xlabel('Dataset Instance', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Solution Quality (Best = 1.0)', fontsize=12, fontweight='bold')
    ax.set_title('Algorithm Performance Comparison Across TSP Instances', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, rotation=45, ha='right')
    
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1, alpha=0.7, 
               label='Optimal (Best)')
    
    ax.legend(loc='upper left', fontsize=10)
    
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    y_min = 0
    y_max = max(norm_df[['BF', 'Approx', 'LS']].max().max() * 1.1, 1.5)
    ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()


def main():
    df = load_results('results.csv')
    create_bar_chart(df, 'performance_chart.png')


if __name__ == '__main__':
    main()