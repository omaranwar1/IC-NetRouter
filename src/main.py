from router import MazeRouter
from visualize import visualize_routing

def main():
    # Test files:
    # case1_simple_2pin.txt
    # case2_multipin.txt
    # case3_obstacles.txt
    # case4_layer_preference.txt
    # case5_high_density.txt
    # case6_penalties.txt
    # case7_boundary.txt
    # case8_complex.txt
    # case_ripup_test.txt
    input_file = 'test_cases/case3_obstacles.txt'
    output_file = 'output.txt'  # Replace with the path for your output file

    # Initialize MazeRouter with the input file
    router = MazeRouter(input_file)
    
    # Try to route all nets
    if router.route_all_nets(max_attempts= 100):
        print("Routing successful!")
    else:
        print("Routing failed after maximum attempts.")
    
    # Write the output to the specified file
    router.write_output(output_file)
    print(f"Routing results written to {output_file}")
    
    # Visualize the routing results
    visualize_routing(output_file, input_file)
    
if __name__ == "__main__":
    main()