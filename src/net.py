class Pin:
    def __init__(self, layer, x, y):
        self.layer = layer
        self.x = x
        self.y = y
        
    def _str_(self):
        return f"({self.layer},{self.x},{self.y})"
        
    def _repr_(self):
        return self._str_()

class Net:
    def __init__(self, name, pins):
        self.name = name
        self.pins = pins    # List of Pin objects
        self.route = []     # Will store the final route [(layer, x, y), ...]
        self.cost = float('inf')  # Total routing cost
        
    def __str__(self):
        return f"{self.name}: {len(self.pins)} pins, cost={self.cost}"
        
    def clear_route(self):
        """Clear the current route"""
        self.route = []
        self.cost = float('inf')