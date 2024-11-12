from .grid import Grid
from .net import Net, Pin

class MazeRouter:
    def __init__(self, input_file):
        self.grid = None
        self.nets = []
        self.parse_input(input_file)
    
    def parse_input(self, input_file):
        """Parse the input file and initialize grid and nets"""
        with open(input_file, 'r') as f:
            # Parse first line
            width, height, bend_penalty, via_penalty = map(int, f.readline().strip().split(','))
            self.grid = Grid(width, height, bend_penalty, via_penalty)
            
            # Parse remaining lines
            for line in f:
                line = line.strip()
                if line.startswith('OBS'):
                    # Parse obstacle
                    parts = line[4:-1].split(',')
                    layer, x, y = map(int, parts)
                    self.grid.add_obstacle(layer, x, y)
                elif line.startswith('net'):
                    # Parse net
                    name = line.split()[0]
                    pins = []
                    parts = line.split('(')[1:]
                    for part in parts:
                        layer, x, y = map(int, part.strip(') ').split(','))
                        pins.append(Pin(layer, x, y))
                    self.nets.append(Net(name, pins))