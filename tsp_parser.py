"""
TSP File Parser

This module provides functionality to parse TSPLIB format files and extract
coordinate information for Traveling Salesman Problem instances.

The parser reads standard TSPLIB format files and extracts:
- Instance name
- Dimension (number of cities)
- Node coordinates (vertex IDs and their x, y coordinates)
"""


def parse_tsp_file(filename):
    """
    Parse a TSPLIB format file and extract coordinates.
    
    Args:
        filename: Path to the .tsp file
        
    Returns:
        tuple: (instance_name, dimension, coordinates_dict)
        coordinates_dict maps vertex_id -> (x, y)
        
    Raises:
        ValueError: If the file format is invalid or required information is missing
    """
    coordinates = {}
    instance_name = None
    dimension = None
    
    with open(filename, 'r') as f:
        in_coord_section = False
        
        for line in f:
            line = line.strip()
            
            if not line or line == 'EOF':
                if in_coord_section:
                    break
                continue
            
            if line.startswith('NAME:'):
                instance_name = line.split(':', 1)[1].strip()
            elif line.startswith('DIMENSION:'):
                dimension = int(line.split(':', 1)[1].strip())
            elif line == 'NODE_COORD_SECTION':
                in_coord_section = True
                continue
            
            if in_coord_section:
                parts = line.split()
                if len(parts) >= 3:
                    vertex_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    coordinates[vertex_id] = (x, y)
    
    if instance_name is None or dimension is None or not coordinates:
        raise ValueError(f"Invalid TSP file format: {filename}")
    
    return instance_name, dimension, coordinates

