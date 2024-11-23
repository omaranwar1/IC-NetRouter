import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, ConnectionPatch
import re

def parse_output_file(filename):
    nets = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                net_name, coords = line.strip().split(' ', 1)
                coords = re.findall(r'\((\d+),(\d+),(\d+)\)', coords)
                path = [(int(layer), int(x), int(y)) for layer, x, y in coords]
                nets[net_name] = path
    return nets

def parse_input_file(filename):
    """Parse input file to get nets and their original pins"""
    nets_pins = {}
    with open(filename, 'r') as f:
        # Skip first line (grid info)
        f.readline()
        for line in f:
            if line.startswith('net'):
                name = line.split()[0]
                pins = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
                nets_pins[name] = [(int(layer), int(x), int(y)) for layer, x, y in pins]
    return nets_pins

def find_actual_vias_and_connections(route):
    """Find actual vias and additional connections needed"""
    vias = set()
    additional_connections = []
    points_by_coord = {}
    
    # Group points by their x,y coordinates
    for layer, x, y in route:
        coord = (x, y)
        if coord not in points_by_coord:
            points_by_coord[coord] = set()
        points_by_coord[coord].add(layer)
        
    # If a coordinate has points on both layers, it's a via
    for (x, y), layers in points_by_coord.items():
        if len(layers) > 1:  # Points exist on both layers
            vias.add((x, y))
    
    # Find additional connections needed (only for non-consecutive adjacent points)
    for i in range(len(route)):
        for j in range(i + 2, len(route)):  # Start checking from 2 positions ahead
            curr = route[i]
            next_pos = route[j]
            
            # Check if points are adjacent but not consecutive
            if curr[0] == next_pos[0]:  # Same layer
                dx = abs(curr[1] - next_pos[1])
                dy = abs(curr[2] - next_pos[2])
                if dx + dy == 1:  # Adjacent points
                    # Check if there's no direct connection already
                    if j != i + 1:  # Not consecutive points
                        # Check if these points are connected through vias
                        curr_coord = (curr[1], curr[2])
                        next_coord = (next_pos[1], next_pos[2])
                        
                        # Only add connection if points aren't connected through vias
                        if not (curr_coord in vias and next_coord in vias):
                            additional_connections.append((curr, next_pos))
    
    return vias, additional_connections

def visualize_routing(output_file, input_file):
    # Read grid dimensions and obstacles from input file
    with open(input_file, 'r') as f:
        width, height, bend_penalty, via_penalty = map(int, f.readline().strip().split(','))
        obstacles = []
        for line in f:
            if line.startswith('OBS'):
                obs = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)[0]
                obstacles.append(tuple(map(int, obs)))

    # Parse both input and output files
    nets_routes = parse_output_file(output_file)
    nets_pins = parse_input_file(input_file)

    # Create figure with two subplots (one for each layer)
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.3])
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1])
    ax_info = fig.add_subplot(gs[2])
    
    fig.suptitle('Routing Visualization', fontsize=16, y=0.95)
    
    # Set up both layers
    ax0.set_title(f'Layer M0 (Preferred Horizontal)\nGrid Size: {width}x{height}', pad=20)
    ax1.set_title(f'Layer M1 (Preferred Vertical)\nGrid Size: {width}x{height}', pad=20)
    
    # Add coordinate labels
    for ax in (ax0, ax1):
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add coordinate labels
        ax.set_xticks(range(width))
        ax.set_yticks(range(height))
        
        # Add coordinate numbers in each cell only if grid is smaller than 18x18
        if width <= 18 and height <= 18:
            for i in range(width):
                for j in range(height):
                    ax.text(i, j, f'({i},{j})', ha='center', va='center', 
                           fontsize=6, alpha=0.3)  # Reduced font size and opacity
        
        ax.set_xlim(-0.5, width - 0.5)
        ax.set_ylim(-0.5, height - 0.5)
        ax.set_aspect('equal')

    # Plot obstacles
    for layer, x, y in obstacles:
        ax = ax0 if layer == 0 else ax1
        obstacle = Rectangle((x-0.5, y-0.5), 1, 1, color='red', alpha=0.3)
        ax.add_patch(obstacle)
        ax.text(x, y, 'OBS', ha='center', va='center', color='red', fontweight='bold')

    # Colors for different nets
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Information panel setup
    ax_info.axis('off')
    info_text = [
        "Routing Information",
        "----------------",
        f"Grid Size: {width}x{height}",
        f"Bend Penalty: {bend_penalty}",
        f"Via Penalty: {via_penalty}",
        "\nNets:",
    ]
    
    # Plot nets
    for i, (net_name, route) in enumerate(nets_routes.items()):
        color = colors[i % len(colors)]
        original_pins = nets_pins[net_name]
        
        # First identify actual vias and additional connections
        actual_vias, additional_connections = find_actual_vias_and_connections(route)
        print(f"Found vias for {net_name}: {actual_vias}")
        print(f"Additional connections needed: {additional_connections}")
        
        # Calculate path cost
        path_cost = 0
        via_count = len(actual_vias)
        path_cost += via_count * via_penalty  # Add via penalties for actual vias
        
        # Calculate movement and bend costs
        for j in range(len(route) - 1):
            curr_pos = route[j]
            next_pos = route[j + 1]
            
            if curr_pos[0] == next_pos[0]:  # Same layer
                path_cost += 1  # Basic move cost
                # Add bend penalty if direction violates layer preference
                is_horizontal = (next_pos[1] - curr_pos[1]) != 0
                if (curr_pos[0] == 0 and not is_horizontal) or (curr_pos[0] == 1 and is_horizontal):
                    path_cost += bend_penalty
        
        # Add costs for additional connections
        for conn in additional_connections:
            path_cost += 1  # Basic move cost
            # Check if bend penalty applies
            is_horizontal = (conn[1][1] - conn[0][1]) != 0
            if (conn[0][0] == 0 and not is_horizontal) or (conn[0][0] == 1 and is_horizontal):
                path_cost += bend_penalty
        
        # Add net information to info panel
        info_text.append(f"\n{net_name}:")
        info_text.append(f"Pins:")
        for idx, pin in enumerate(original_pins):
            info_text.append(f"  P{idx+1}: ({pin[0]},{pin[1]},{pin[2]})")
        info_text.append(f"Path length: {len(route)}")
        info_text.append(f"Path cost: {path_cost}")

        # Draw the routing path
        for j in range(len(route) - 1):
            curr_pos = route[j]
            next_pos = route[j + 1]
            
            # Same layer connection
            if curr_pos[0] == next_pos[0]:
                ax = ax0 if curr_pos[0] == 0 else ax1
                ax.plot([curr_pos[1], next_pos[1]], 
                       [curr_pos[2], next_pos[2]], 
                       color=color, linewidth=2, 
                       label=net_name if j == 0 else "")
                
                # Direction arrows
                if curr_pos != next_pos:
                    mid_x = (curr_pos[1] + next_pos[1]) / 2
                    mid_y = (curr_pos[2] + next_pos[2]) / 2
                    dx = next_pos[1] - curr_pos[1]
                    dy = next_pos[2] - curr_pos[2]
                    ax.arrow(mid_x - dx/3, mid_y - dy/3, dx/6, dy/6, 
                            head_width=0.15, head_length=0.15, 
                            fc=color, ec=color, 
                            alpha=0.8,
                            width=0.05)
            
            # Via connection - check both current and next positions
            else:  # Layer change
                curr_coord = (curr_pos[1], curr_pos[2])
                next_coord = (next_pos[1], next_pos[2])
                
                # Draw via if either current or next position is a via point
                if curr_coord in actual_vias or next_coord in actual_vias:
                    via_coord = curr_coord if curr_coord in actual_vias else next_coord
                    
                    # Draw via markers on both layers
                    ax0.scatter(via_coord[0], via_coord[1], color=color, marker='s', s=80,
                              alpha=0.5 if curr_pos[0] == 1 else 1)
                    ax1.scatter(via_coord[0], via_coord[1], color=color, marker='s', s=80,
                              alpha=0.5 if curr_pos[0] == 0 else 1)
                    
                    # Add via label on the layer where the via starts
                    ax = ax0 if curr_pos[0] == 0 else ax1
                    ax.text(via_coord[0], via_coord[1], 'Via', fontsize=7,
                           ha='right', va='bottom', fontweight='bold',
                           alpha=1.0)

        # Draw additional connections with ConnectionPatch
        for conn in additional_connections:
            ax = ax0 if conn[0][0] == 0 else ax1
            conn_patch = ConnectionPatch(
                (conn[0][1], conn[0][2]), 
                (conn[1][1], conn[1][2]),
                coordsA='data', coordsB='data',
                axesA=ax, axesB=ax,
                color=color, linewidth=2,
                alpha=0.7  # Removed linestyle=':' for solid line
            )
            ax.add_artist(conn_patch)

        # Plot original pins (smaller markers)
        for idx, pin in enumerate(original_pins):
            layer, x, y = pin
            ax = ax0 if layer == 0 else ax1
            
            # Different markers for different pin types
            if idx == 0:  # Start pin
                marker = 'o'
                size = 80
            elif idx == len(original_pins) - 1:  # End pin
                marker = 'x'
                size = 80
            else:  # Intermediate pin
                marker = 'D'
                size = 60
            
            # Plot pin with appropriate marker
            ax.scatter(x, y, color=color, marker=marker, s=size,
                      label=net_name if idx == 0 else "", zorder=5)
            
            # Add pin number annotation
            ax.text(x, y+0.15, f'P{idx+1}', color=color,
                    ha='center', va='bottom', fontsize=7,
                    fontweight='bold', alpha=1.0)

    # Add single legend for each subplot
    handles0, labels0 = ax0.get_legend_handles_labels()
    handles1, labels1 = ax1.get_legend_handles_labels()
    
    # Remove duplicates while preserving order
    seen = set()
    handles0_unique = []
    labels0_unique = []
    for h, l in zip(handles0, labels0):
        if l not in seen:
            seen.add(l)
            handles0_unique.append(h)
            labels0_unique.append(l)
            
    seen = set()
    handles1_unique = []
    labels1_unique = []
    for h, l in zip(handles1, labels1):
        if l not in seen:
            seen.add(l)
            handles1_unique.append(h)
            labels1_unique.append(l)

    ax0.legend(handles0_unique, labels0_unique, bbox_to_anchor=(0.5, -0.1), loc='upper center', ncol=2)
    ax1.legend(handles1_unique, labels1_unique, bbox_to_anchor=(0.5, -0.1), loc='upper center', ncol=2)
    
    # Add information panel text
    ax_info.text(0, 0.95, '\n'.join(info_text), 
                verticalalignment='top', 
                horizontalalignment='left',
                fontfamily='monospace')
    
    # Add legend for symbols
    symbol_info = [
        "\nSymbol Legend:",
        "○ : Start Pin",
        "× : End Pin",
        "◇ : Intermediate Pin",
        "□ : Via",
        "→ : Direction",
        "▮ : Obstacle",
        "\nCost Information:",
        f"Basic move: 1",
        f"Bend penalty: {bend_penalty}",
        f"Via penalty: {via_penalty}"
    ]
    ax_info.text(0, 0.3, '\n'.join(symbol_info), 
                verticalalignment='top', 
                horizontalalignment='left',
                fontfamily='monospace')
    
    plt.tight_layout()
    plt.show()

