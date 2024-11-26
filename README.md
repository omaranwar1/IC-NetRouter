# Maze Router 

A Python implementation of a maze router, featuring multi-pin net routing with layer constraints, obstacle avoidance, and visualisation capabilities.
## Features

- Multi-layer routing (M0 and M1)
- Layer-specific preferred directions (M0: horizontal, M1: vertical)
- Multi-pin net routing 
- Obstacle avoidance
- Configurable bend and via penalties
- Automatic rip-up and reroute with randomization
- Route visualization
- Support for custom input specifications

## Requirements

- Python 3.7+
- NumPy
- MatPlotLib

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/omaranwar1/IC-NetRouter.git
   cd IC-NetRouter 
   cd src
2. **Install Packages**
    ```bash
    pip install matplotlib
    pip install numpy

## Usage 
1. Choose the test case, and add it to the main.py
2. Run the program
   ```bash
   python main.py

## Implementation Details

### Routing Algorithm

- Uses a modified A* algorithm for pathfinding
- Implements Steiner tree approach for multi-pin nets
- Features rip-up and reroute with randomisation for handling routing conflicts
- Employs layer-specific preferred directions to optimize routing by calculating the cost, and choosing the least costly path 

### Cost Model

- Base cost for each grid cell movement; adds 1 to the total route cost 
- Additional penalties for:
  - Non-preferred direction movements
  - Via transitions between layers
  - Costs are predefined in the input file 
- Manhattan distance heuristic for A* pathfinding

### Grid Management

- Two-layer grid system (M0 and M1)
- Tracks occupied cells and obstacles
- Maintains net-specific routing information
- Supports dynamic path clearing and updating

## Output

- The router generates an output file containing the routed paths for each net in the following format:
  - net1 (layer1,x1,y1) (layer2,x2,y2) ...
  - net2 (layer1,x1,y1) (layer2,x2,y2) ...

## Contributions
 - Amal Fouda:
   - Router implementation to parse through input
   - Routing implementation using A* algorithm for single pin nets
   - Routing implementation to rip and reroute when the routing algorithm yields unsuccessful 
  - Nour Selim
    - Grid implementation to get neighbours and adding obstacles 
    - Grid implementation to check valid moves
    - Routing implementation to rip and reroute when the routing algorithm yields unsuccessful 
  - Omar Saleh
    - Router implementation to use A* algorithm for multipin nets 
    - Visualisation implementation
    - Routing implementation to rip and reroute when the routing algorithm yields unsuccessful 

## Challenges 
  - Bug fixes for the visualisation tool
  - Implementing multipin routing without interferring with other nets
  - Dealing with failed attempts to route, and avoiding infinite loops in rerouting attempts
  - Efficiently connecting multiple pins while minimizing total wire length
