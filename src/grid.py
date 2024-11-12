import numpy as np

class Grid:
    def __init__(self, width, height, bend_penalty, via_penalty):
        self.width = width
        self.height = height
        self.bend_penalty = bend_penalty
        self.via_penalty = via_penalty
        
        # Create two layers (M0 and M1)
        self.layer_m0 = np.zeros((height, width), dtype=int)  
        self.layer_m1 = np.zeros((height, width), dtype=int)  
        
    def add_obstacle(self, layer, x, y):
        if layer == 0:
            self.layer_m0[y, x] = 1
        else:
            self.layer_m1[y, x] = 1 