from .grid import Grid
from .net import Net, Pin
import heapq
import random

class MazeRouter:
    def _init_(self, input_file):
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
    
    def route_all_nets(self, max_attempts=3):
        """Route all nets with rip-up and retry"""
        for attempt in range(max_attempts):
            success = True
            # Randomize net order for each attempt
            random.shuffle(self.nets)
            
            for net in self.nets:
                if not net.route:  # Only route if not already routed
                    if not self.route_net(net):
                        success = False
                        # Clear failed net and try again
                        self.grid.clear_path(net.name)
                        net.clear_route()
                        
            if success:
                return True
                
        return False
    
    def route_net(self, net):
        """Route a multi-pin net"""
        if len(net.pins) < 2:
            return True
        
        complete_path = []
        total_cost = 0
        
        # Route between consecutive pins
        for i in range(len(net.pins) - 1):
            source = net.pins[i]
            target = net.pins[i + 1]
            
            path, cost = self.route_two_pins(source, target, net.name)
            if not path:
                return False
                
            total_cost += cost
            
            # Add path to complete route
            if complete_path and path:
                complete_path.extend(path[1:])
            else:
                complete_path.extend(path)
        
        net.route = complete_path
        net.cost = total_cost
        self.grid.mark_path(complete_path, net.name)
        return True
    
    def route_two_pins(self, source, target, net_name):
        """Route between two pins using A* algorithm"""
        start = (source.layer, source.x, source.y)
        goal = (target.layer, target.x, target.y)
        
        open_set = [(self.manhattan_distance(start, goal), start)]
        heapq.heapify(open_set)
        
        came_from = {start: None}
        g_score = {start: 0}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                return path, g_score[current]
            
            prev_pos = came_from[current]
            for next_pos, cost in self.grid.get_neighbors(current, prev_pos, net_name):
                tentative_g = g_score[current] + cost
                
                if next_pos not in g_score or tentative_g < g_score[next_pos]:
                    came_from[next_pos] = current
                    g_score[next_pos] = tentative_g
                    f_score = tentative_g + self.manhattan_distance(next_pos, goal)
                    heapq.heappush(open_set, (f_score, next_pos))
        
        return None, float('inf')
    
    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[1] - pos2[1]) + abs(pos1[2] - pos2[2])
    
    def reconstruct_path(self, came_from, current):
        """Reconstruct path from came_from dictionary"""
        path = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        return path[::-1]
    
    def write_output(self, output_file):
        """Write routing results to output file"""
        with open(output_file, 'w') as f:
            for net in self.nets:
                if net.route:
                    route_str = ' '.join(f"({layer},{x},{y})" for layer, x, y in net.route)
                    f.write(f"{net.name} {route_str}\n")