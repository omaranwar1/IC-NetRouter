import numpy as np
from collections import defaultdict

class Grid:
    def __init__(self, width, height, bend_penalty, via_penalty, router):
        self.width = width
        self.height = height
        self.bend_penalty = bend_penalty
        self.via_penalty = via_penalty
        self.router = router
        
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
            return False
            
        # Check obstacles
        if layer == 0 and self.layer_m0[y, x] == 1:
            return False
        if layer == 1 and self.layer_m1[y, x] == 1:
            return False
            
        pos = (layer, x, y)
        
        # Check if position is a pin location of another net
        for other_net in self.router.nets:  # We'll need to pass router reference to Grid
            if other_net.name != net_name:
                for pin in other_net.pins:
                    if (layer, x, y) == (pin.layer, pin.x, pin.y):
                        return False
        
        # Check if cell is used by other nets
        for other_net, cells in self.used_cells.items():
            if other_net != net_name:
                if pos in cells:
                    return False
            
        return True
        
    def get_neighbors(self, pos, prev_pos, net_name):
        """Get valid neighboring positions with costs"""
        layer, x, y = pos
        neighbors = []
        
        # Prioritize preferred directions based on layer
        if layer == 0:  # M0 prefers horizontal
            moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Horizontal first
        else:  # M1 prefers vertical
            moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Vertical first
        
        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_move(layer, new_x, new_y, net_name):
                is_horizontal = dx != 0
                cost = 1
                
                # Only add penalty for non-preferred direction movements
                # Remove the direction change penalty completely
                if ((layer == 0 and not is_horizontal) or 
                    (layer == 1 and is_horizontal)):
                    cost += self.bend_penalty
                
                neighbors.append((layer, new_x, new_y, cost))
        
        # Via movements (layer changes)
        other_layer = 1 - layer
        if self.is_valid_move(other_layer, x, y, net_name):
            neighbors.append((other_layer, x, y, self.via_penalty))
        
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
        
#         # Prioritize preferred directions based on layer
#         if layer == 0:  # M0 prefers horizontal
#             moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Horizontal first
#         else:  # M1 prefers vertical
#             moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Vertical first
#         
#         for dx, dy in moves:
#             new_x, new_y = x + dx, y + dy
#             if self.is_valid_move(layer, new_x, new_y, net_name):
#                 is_horizontal = dx != 0
#                 cost = 1
#                 
#                 # Only add penalty for non-preferred direction movements
#                 # Remove the direction change penalty completely
#                 if ((layer == 0 and not is_horizontal) or 
#                     (layer == 1 and is_horizontal)):
#                     cost += self.bend_penalty
#                 
#                 neighbors.append((layer, new_x, new_y, cost))
#         
#         # Via movements (layer changes)
#         other_layer = 1 - layer
#         if self.is_valid_move(other_layer, x, y, net_name):
#             neighbors.append((other_layer, x, y, self.via_penalty))
#         
#         return neighbors

