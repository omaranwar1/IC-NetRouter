import numpy as np
from collections import defaultdict

class Grid:
    def __init__(self, width, height, bend_penalty, via_penalty):
        self.width = width
        self.height = height
        self.bend_penalty = bend_penalty
        self.via_penalty = via_penalty
        
        # Create two layers (M0 and M1)
        self.layer_m0 = np.zeros((height, width), dtype=int)
        self.layer_m1 = np.zeros((height, width), dtype=int)
        
        # Track used cells for each net
        self.used_cells = defaultdict(set)
        
    def add_obstacle(self, layer, x, y):
        """Add obstacle to specified layer"""
        if layer == 0:
            self.layer_m0[y, x] = 1
        else:
            self.layer_m1[y, x] = 1
        print(f"Obstacle added at Layer={layer}, X={x}, Y={y}")
            
    def is_valid_move(self, layer, x, y, net_name=None):
        """Check if a position is valid for routing"""
        # Check bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            print(f"Invalid move: Out of bounds at X={x}, Y={y}")
            return False
            
        # Check obstacles
        if layer == 0 and self.layer_m0[y, x] == 1:
            print(f"Invalid move: Obstacle found at Layer={layer}, X={x}, Y={y}")
            return False
        if layer == 1 and self.layer_m1[y, x] == 1:
            print(f"Invalid move: Obstacle found at Layer={layer}, X={x}, Y={y}")
            return False
            
        # Check if cell is used by other nets
        pos = (layer, x, y)
        for other_net, cells in self.used_cells.items():
            if other_net != net_name:
                if pos in cells:
                    print(f"Invalid move: Cell already used by net {other_net} at Layer={layer}, X={x}, Y={y}")
                    return False
                
        print(f"Valid move at Layer={layer}, X={x}, Y={y}")
        return True
        
    def get_neighbors(self, pos, prev_pos, net_name):
        """Get valid neighboring positions with costs"""
        layer, x, y = pos
        neighbors = []
        
        # Determine previous direction
        prev_direction = None
        if prev_pos:
            dx = x - prev_pos[1]
            dy = y - prev_pos[2]
            prev_direction = 'horizontal' if dx != 0 else 'vertical'
        
        # Same layer movements
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_move(layer, new_x, new_y, net_name):
                # Calculate cost based on preferred directions
                is_horizontal = dx != 0
                cost = 1
                
                # Add bend penalty if changing direction
                if prev_direction:
                    current_direction = 'horizontal' if dx != 0 else 'vertical'
                    if current_direction != prev_direction:
                        cost += self.bend_penalty
                
                # Add penalty for non-preferred direction
                if (layer == 0 and not is_horizontal) or (layer == 1 and is_horizontal):
                    cost += self.bend_penalty
                
                neighbors.append((layer, new_x, new_y, cost))
                print(f"Neighbor found: Layer={layer}, X={new_x}, Y={new_y}, Cost={cost}")
        
        # Via movements (layer changes)
        other_layer = 1 - layer
        if self.is_valid_move(other_layer, x, y, net_name):
            neighbors.append((other_layer, x, y, self.via_penalty))
            print(f"Adding via from Layer={layer} to Layer={other_layer} at X={x}, Y={y}, Cost={self.via_penalty}")
        
        return neighbors
    
    def mark_path(self, path, net_name):
        """Mark cells as used by a net"""
        for pos in path:
            self.used_cells[net_name].add(pos)
            
    def clear_path(self, net_name):
        """Clear the path of a specific net"""
        if net_name in self.used_cells:
            del self.used_cells[net_name]

# import numpy as np
# from collections import defaultdict

# class Grid:
#     def __init__(self, width, height, bend_penalty, via_penalty):
#         self.width = width
#         self.height = height
#         self.bend_penalty = bend_penalty
#         self.via_penalty = via_penalty
        
#         # Create two layers (M0 and M1)
#         self.layer_m0 = np.zeros((height, width), dtype=int)
#         self.layer_m1 = np.zeros((height, width), dtype=int)
        
#         # Track used cells for each net
#         self.used_cells = defaultdict(set)
        
#     def add_obstacle(self, layer, x, y):
#         """Add obstacle to specified layer"""
#         if layer == 0:
#             self.layer_m0[y, x] = 1
#         else:
#             self.layer_m1[y, x] = 1
            
#     def is_valid_move(self, layer, x, y, net_name=None):
#         """Check if a position is valid for routing"""
#         # Check bounds
#         if x < 0 or x >= self.width or y < 0 or y >= self.height:
#             return False
            
#         # Check obstacles
#         if layer == 0 and self.layer_m0[y, x] == 1:
#             return False
#         if layer == 1 and self.layer_m1[y, x] == 1:
#             return False
            
#         # Check if cell is used by other nets
#         pos = (layer, x, y)
#         for other_net, cells in self.used_cells.items():
#             if other_net != net_name:
#               if pos in cells:
#                 return False
                
#         return True
        
#     def get_neighbors(self, pos, prev_pos, net_name):
#         """Get valid neighboring positions with costs"""
#         layer, x, y = pos
#         neighbors = []
        
#         # Determine previous direction
#         prev_direction = None
#         if prev_pos:
#             dx = x - prev_pos[1]
#             dy = y - prev_pos[2]
#             prev_direction = 'horizontal' if dx != 0 else 'vertical'
        
#         # Same layer movements
#         moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
#         for dx, dy in moves:
#             new_x, new_y = x + dx, y + dy
#             if self.is_valid_move(layer, new_x, new_y, net_name):
#                 # Calculate cost based on preferred directions
#                 is_horizontal = dx != 0
#                 cost = 1
                
#                 # Add bend penalty if changing direction
#                 if prev_direction:
#                     current_direction = 'horizontal' if dx != 0 else 'vertical'
#                     if current_direction != prev_direction:
#                         cost += self.bend_penalty
                
#                 # Add penalty for non-preferred direction
#                 if (layer == 0 and not is_horizontal) or (layer == 1 and is_horizontal):
#                     cost += self.bend_penalty
                
#                 neighbors.append((layer, new_x, new_y, cost))
        
#         # Via movements (layer changes)
#         other_layer = 1 - layer
#         if self.is_valid_move(other_layer, x, y, net_name):
#             neighbors.append((other_layer, x, y, self.via_penalty))
        
#         return neighbors
    
