from grid import Grid
from net import Net, Pin
import heapq
import random
from collections import defaultdict


class MazeRouter:
   def __init__(self, input_file, grid=None):
       self.grid = None
       self.nets = []
       self.parse_input(input_file)
      
   def parse_input(self, input_file):
       """Parse the input file and initialize grid and nets"""
       print(f"Parsing input file: {input_file}")
       with open(input_file, 'r') as f:
           # Parse first line
           width, height, bend_penalty, via_penalty = map(int, f.readline().strip().split(','))
           self.grid = Grid(width, height, bend_penalty, via_penalty, self)
           print(f"Grid initialized: {width}x{height}, Bend Penalty: {bend_penalty}, Via Penalty: {via_penalty}")
          
           # Parse remaining lines
           for line in f:
               line = line.strip()
               if line.startswith('OBS'):
                   # Parse obstacle
                   parts = line[4:].strip('()').split(',')
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
                   print(f"Net added: {name}, Pins={[(pin.layer, pin.x, pin.y) for pin in pins]}")
  
   def route_all_nets(self, max_attempts=100):
       """Route all nets with complete reset and shuffle on failure"""
       for attempt in range(max_attempts):
           print(f"\nRouting attempt {attempt + 1}/{max_attempts}")
           
           # Clear all existing routes at the start of each attempt
           for net in self.nets:
               self.grid.clear_path(net.name)
               net.clear_route()
           
           # Shuffle nets for this attempt
           nets_to_route = self.nets.copy()
           random.shuffle(nets_to_route)
           
           # Try to route all nets in the new order
           success = True
           for net in nets_to_route:
               print(f"Routing net: {net.name}")
               if not self.route_net(net):
                   print(f"Failed to route net: {net.name}")
                   success = False
                   break
               print(f"Net {net.name} routed successfully.")
           
           if success:
               print("All nets routed successfully!")
               return True
       
       print("Routing failed after maximum attempts.")
       return False
  
   def route_net(self, net):
       """Route a multi-pin net using Steiner tree approach"""
       if len(net.pins) < 2:
           print(f"Net {net.name} has less than 2 pins, skipping.")
           return True
      
       source_positions = {(net.pins[0].layer, net.pins[0].x, net.pins[0].y)}
       target_positions = {(pin.layer, pin.x, pin.y) for pin in net.pins[1:]}
       complete_path = []
       total_cost = 0
      
       while target_positions:
           path, cost = self.route_to_nearest_target(source_positions, target_positions, net.name)
           if not path:
               print(f"Failed to find path for net: {net.name}")
               return False
          
           print(f"Path found for two pins: {path}, Cost: {cost}")
           total_cost += cost
          
           if complete_path:
               complete_path.extend(path[1:])
           else:
               complete_path.extend(path)
          
           for pos in path:
               source_positions.add(pos)
               target_positions.discard(pos)
           print(f"Source positions: {source_positions}")
           print(f"Target positions: {target_positions}")
      
       net.route = complete_path
       net.cost = total_cost
       self.grid.mark_path(complete_path, net.name)
       print(f"Net {net.name} routed. Path: {complete_path}, Total Cost: {total_cost}")
       return True
  
   def route_to_nearest_target(self, sources, targets, net_name):
       """Find path from any source to nearest target using modified A*"""
       open_set = []
       for source in sources:
           # Calculate minimum Manhattan distance to any target
           min_dist = min(self.manhattan_distance(source, target) for target in targets)
           heapq.heappush(open_set, (min_dist, source))
      
       came_from = {source: None for source in sources}
       g_score = {source: 0 for source in sources}
      
       while open_set:
           current = heapq.heappop(open_set)[1]
          
           # Check if we've reached any target
           if current in targets:
               path = self.reconstruct_path(came_from, current)
               return path, g_score[current]
          
           prev_pos = came_from[current]
           for layer, next_x, next_y, cost in self.grid.get_neighbors(current, prev_pos, net_name):  # Changed unpacking
               tentative_g = g_score[current] + cost
              
               if (layer, next_x, next_y) not in g_score or tentative_g < g_score[(layer, next_x, next_y)]:
                   came_from[(layer, next_x, next_y)] = current
                   g_score[(layer, next_x, next_y)] = tentative_g
                   # Use minimum distance to any remaining target as heuristic
                   min_dist = min(self.manhattan_distance((layer, next_x, next_y), target)
                               for target in targets)
                   f_score = tentative_g + min_dist
                   heapq.heappush(open_set, (f_score, (layer, next_x, next_y)))
      
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
       print(f"Writing output to {output_file}")
       with open(output_file, 'w') as f:
           for net in self.nets:
               if net.route:
                   route_str = ' '.join(f"({layer},{x},{y})" for layer, x, y in net.route)
                   f.write(f"{net.name} {route_str}\n")
       print(f"Output written successfully.")
