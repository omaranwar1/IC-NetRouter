class Pin:
    def __init__(self, layer, x, y):
        self.layer = layer
        self.x = x
        self.y = y

class Net:
    def __init__(self, name, pins):
        self.name = name
        self.pins = pins  # List of Pin objects
        self.route = []   # Will store the final route 