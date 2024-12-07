class Pin:
    def __init__(self, layer, x, y):
        self.layer = layer
        self.x = x
        self.y = y


class Net:
    def __init__(self, name, pins):
        self.name = name
        self.pins = pins    # List of Pin objects
        self.route = []     # Will store the final route [(layer, x, y), ...]
        self.cost = float('inf')  # Total routing cost
        
        
    def clear_route(self):
        """Clear the current route"""
        self.route = []
        self.cost = float('inf')
